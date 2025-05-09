import uuid
import json
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_API_KEY
from database.db import (
    create_session,
    get_current_question,
    save_question,
    mark_answered,
    get_daily_topic,
    mark_session_completed,
    get_session_summary
)
from prompts.question import question_prompt
from prompts.evaluation import eval_prompt
from models.schemas import ChatResponse

# LLM 설정
llm1 = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
llm2 = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

# 체인 설정
question_chain = question_prompt | llm1
eval_chain = eval_prompt | llm2

async def start_chat_service(topic: str = None, user_id: str = None) -> ChatResponse:
    # 1. 주제 선택 (요청된 주제가 없으면 오늘의 주제 선택)
    daily_topic = get_daily_topic()
    if not daily_topic:
        raise HTTPException(
            status_code=500,
            detail="오늘의 주제가 설정되지 않았습니다. 잠시 후 다시 시도해주세요."
        )
    
    topic = topic or daily_topic["topic"]
    
    # 2. 세션 생성
    session_id = str(uuid.uuid4())
    create_session(session_id, topic, user_id)
    
    # 3. Bloom's Taxonomy 1단계 질문 생성
    question = question_chain.invoke({
        "topic": topic,
        "bloom_level": 1
    }).content
    
    save_question(session_id, topic, question, 1)
    
    return ChatResponse(
        session_id=session_id,
        topic=topic,
        current_level=1,
        question=question,
        message=f"안녕하세요! 오늘의 주제는 '{topic}'입니다. 첫 번째 질문을 드리겠습니다.",
        is_complete=False
    )

async def process_response_service(
    session_id: str,
    user_answer: str,
    current_level: int,
    topic: str
) -> ChatResponse:
    # 1. 현재 질문 확인
    current_question = get_current_question(session_id)
    if not current_question:
        raise HTTPException(
            status_code=404,
            detail="진행 중인 질문을 찾을 수 없습니다."
        )
    
    # 2. 응답 평가
    evaluation = json.loads(
        eval_chain.invoke({
            "question": current_question["question"],
            "bloom_level": current_question["bloom_level"],
            "user_answer": user_answer
        }).content
    )
    
    # 3. 응답 저장
    mark_answered(
        session_id,
        current_question["bloom_level"],
        user_answer
    )
    
    # 4. 다음 단계 결정
    if evaluation["is_appropriate"]:
        next_level = current_question["bloom_level"] + 1
        
        if next_level <= 6:
            # 다음 단계로 진행
            next_question = question_chain.invoke({
                "topic": topic,
                "bloom_level": next_level
            }).content
            
            save_question(
                session_id,
                topic,
                next_question,
                next_level
            )
            
            return ChatResponse(
                session_id=session_id,
                topic=topic,
                current_level=next_level,
                question=next_question,
                message="좋은 답변입니다! 다음 단계로 넘어가겠습니다.",
                is_complete=False
            )
        else:
            # 모든 단계 완료
            mark_session_completed(session_id)
            return ChatResponse(
                session_id=session_id,
                topic=topic,
                current_level=6,
                question=None,
                message="모든 단계를 완료하셨습니다! 수고하셨습니다.",
                is_complete=True
            )
    else:
        # 힌트 제공 또는 추가 유도
        message = (
            evaluation["hint"]
            if evaluation["is_looking_for_help"]
            else f"조금 더 생각해볼까요? {evaluation['feedback']}"
        )
        
        return ChatResponse(
            session_id=session_id,
            topic=topic,
            current_level=current_question["bloom_level"],
            question=current_question["question"],
            message=message,
            is_complete=False
        )

async def end_chat_service(session_id: str) -> dict:
    # 1. 세션 종료 처리
    mark_session_completed(session_id)
    
    # 2. 세션 요약 생성
    session_summary = get_session_summary(session_id)
    
    return {
        "session_id": session_id,
        "summary": session_summary,
        "message": "오늘의 학습을 마치겠습니다. 수고하셨습니다!"
    }

def check_daily_topic():
    daily_topic = get_daily_topic()
    if not daily_topic:
        print("경고: 오늘의 주제가 아직 선정되지 않았습니다. Airflow DAG가 정상적으로 실행되고 있는지 확인해주세요.") 