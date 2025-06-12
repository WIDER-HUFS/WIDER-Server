import uuid
import json
import logging
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from config.settings import OPENAI_API_KEY
from database.db import (
    create_session,
    get_current_question,
    save_question,
    mark_answered,
    get_daily_topic,
    mark_session_completed,
    get_session_summary,
    save_conversation_history
)
from services.report import generate_report_for_session
from prompts.question import question_prompt
from prompts.evaluation import eval_prompt
from models.schemas import ChatResponse
from .evaluation import evaluate_response

# 로거 설정
logger = logging.getLogger(__name__)

# LLM 설정
llm1 = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)
llm2 = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)

# 체인 설정
question_chain = question_prompt | llm1
eval_chain = eval_prompt | llm2

# 세션별 메모리 저장소
session_memories = {}

def get_session_memory(session_id: str) -> ConversationBufferMemory:
    """세션 ID에 해당하는 메모리를 가져오거나 생성합니다."""
    try:
        if session_id not in session_memories:
            session_memories[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        return session_memories[session_id]
    except Exception as e:
        logger.error(f"Error in get_session_memory for session {session_id}: {str(e)}")
        raise

def format_chat_history(memory: ConversationBufferMemory) -> str:
    """대화 기록을 문자열로 포맷팅합니다."""
    try:
        if not memory.chat_memory.messages:
            return ""
        
        return "\n".join([
            f"{'Human' if msg.type == 'human' else 'AI'}: {msg.content}"
            for msg in memory.chat_memory.messages
        ])
    except Exception as e:
        logger.error(f"Error in format_chat_history: {str(e)}")
        raise

async def start_chat_service(topic: str = None, user_id: str = None) -> ChatResponse:
    try:
        logger.info(f"Starting chat service with topic: {topic}, user_id: {user_id}")
        
        # 1. 주제 선택
        daily_topic = get_daily_topic()
        if not daily_topic:
            logger.error("No daily topic found")
            raise HTTPException(
                status_code=500,
                detail="오늘의 주제가 설정되지 않았습니다. 잠시 후 다시 시도해주세요."
            )
        
        topic = topic or daily_topic["topic"]
        logger.info(f"Selected topic: {topic}")
        
        # 2. 세션 생성
        session_id = str(uuid.uuid4())
        create_session(session_id, topic, user_id)
        logger.info(f"Created new session: {session_id}")
        
        # 3. 세션 메모리 초기화
        memory = get_session_memory(session_id)
        memory.clear()
        
        # 4. 첫 번째 질문 생성
        try:
            topic_prompt = daily_topic["topic_prompt"]  # ✅ 추가
            question = question_chain.invoke({
                "topic": topic,
                "bloom_level": 1,
                "chat_history": "",
                "topic_prompt": topic_prompt  # ✅ 추가
            }).content
            logger.info(f"Generated first question for session {session_id}")
        except Exception as e:
            logger.error(f"Error generating first question: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="질문 생성 중 오류가 발생했습니다."
            )
        
        # 5. 질문을 메모리에 저장
        memory.save_context(
            {"input": f"주제: {topic}"},
            {"output": question}
        )
        
        # 6. 질문 저장
        save_question(session_id, topic, question, 1)
        
        # 7. 대화 기록 저장
        welcome_message = f"안녕하세요! 오늘의 주제는 '{topic}'입니다. 첫 번째 질문을 드리겠습니다."
        save_conversation_history(session_id, "AI", welcome_message)
        save_conversation_history(session_id, "AI", question)
        
        return ChatResponse(
            session_id=session_id,
            topic=topic,
            current_level=1,
            question=question,
            message=welcome_message,
            is_complete=False
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in start_chat_service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"채팅 시작 중 오류가 발생했습니다: {str(e)}"
        )

async def process_response_service(
    session_id: str,
    user_answer: str,
    current_level: int,
    topic: str,
    topic_prompt: str,
    user_id: str
) -> ChatResponse:
    try:
        logger.info(f"Processing response for session {session_id}, level {current_level}")
        
        # 1. 현재 질문 확인
        current_question = get_current_question(session_id)
        if not current_question:
            logger.error(f"No current question found for session {session_id}")
            raise HTTPException(
                status_code=404,
                detail="진행 중인 질문을 찾을 수 없습니다."
            )
        
        # 2. 사용자 응답 평가
        evaluation = evaluate_response(
            question=current_question["question"],
            bloom_level=current_level,
            user_answer=user_answer
        )
        
        # 3. 세션 메모리 가져오기
        memory = get_session_memory(session_id)
        
        # 4. 사용자 응답을 메모리에 저장
        memory.save_context(
            {"input": current_question["question"]},
            {"output": user_answer}
        )
        
        # 5. 사용자 응답 저장
        mark_answered(session_id, current_level, user_answer)
        
        # 6. 대화 기록 저장
        save_conversation_history(session_id, "Human", user_answer)
        
        # 7. 응답이 부적절한 경우
        if not evaluation["is_appropriate"]:
            # 피드백과 힌트를 포함한 메시지 생성
            feedback_message = f"{evaluation['feedback']}\n\n힌트: {evaluation['hint']}"
            
            # 대화 기록에 피드백 저장
            save_conversation_history(session_id, "AI", feedback_message)
            
            # 같은 질문을 다시 저장하여 다음 응답에서도 사용할 수 있도록 함
            save_question(
                session_id,
                topic,
                current_question["question"],
                current_level
            )
            
            return ChatResponse(
                session_id=session_id,
                topic=topic,
                current_level=current_level,
                question=current_question["question"],
                message=feedback_message,
                is_complete=False
            )
        
        # 8. 다음 단계 결정
        next_level = current_level + 1
        
        if next_level > 6:
            # 세션 종료
            mark_session_completed(session_id)
            
            # 리포트 생성
            report = await generate_report_for_session(session_id, user_id)
            
            # 세션 메모리 정리
            if session_id in session_memories:
                del session_memories[session_id]
            
            # 대화 기록 저장
            save_conversation_history(session_id, "AI", "오늘의 학습을 마치겠습니다. 수고하셨습니다!")
            
            return ChatResponse(
                session_id=session_id,
                topic=topic,
                current_level=current_level,
                message="오늘의 학습을 마치겠습니다. 수고하셨습니다!",
                is_complete=True
            )
        
        if next_level <= 6:
            # 다음 단계로 진행
            chat_history = format_chat_history(memory)
            
            try:
                next_question = question_chain.invoke({
                    "topic": topic,
                    "topic_prompt": topic_prompt,
                    "bloom_level": next_level,
                    "chat_history": chat_history
                }).content
                logger.info(f"Generated next question for level {next_level}")
            except Exception as e:
                logger.error(f"Error generating next question: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="다음 질문 생성 중 오류가 발생했습니다."
                )
            
            # 새 질문을 메모리에 저장
            memory.save_context(
                {"input": f"다음 단계({next_level}) 질문 생성"},
                {"output": next_question}
            )
            
            save_question(
                session_id,
                topic,
                next_question,
                next_level
            )
            
            # 대화 기록 저장
            save_conversation_history(session_id, "AI", "좋은 답변입니다! 다음 단계로 넘어가겠습니다.")
            save_conversation_history(session_id, "AI", next_question)
            
            return ChatResponse(
                session_id=session_id,
                topic=topic,
                current_level=next_level,
                question=next_question,
                message="좋은 답변입니다! 다음 단계로 넘어가겠습니다.",
                is_complete=False
            )

    except Exception as e:
        logger.error(f"Error in process_response_service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"응답 처리 중 오류가 발생했습니다: {str(e)}"
        )

async def end_chat_service(session_id: str) -> dict:
    try:
        logger.info(f"Ending chat service for session {session_id}")
        
        # 1. 세션 종료 처리
        mark_session_completed(session_id)
        
        # 2. 세션 메모리 정리
        if session_id in session_memories:
            del session_memories[session_id]
        
        # 3. 세션 요약 생성
        session_summary = get_session_summary(session_id)
        logger.info(f"Generated session summary for {session_id}")
        
        return {
            "session_id": session_id,
            "summary": session_summary,
            "message": "오늘의 학습을 마치겠습니다. 수고하셨습니다!"
        }
    except Exception as e:
        logger.error(f"Error in end_chat_service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"채팅 종료 중 오류가 발생했습니다: {str(e)}"
        )

def check_daily_topic():
    try:
        daily_topic = get_daily_topic()
        if not daily_topic:
            logger.warning("No daily topic found. Please check if Airflow DAG is running properly.")
    except Exception as e:
        logger.error(f"Error in check_daily_topic: {str(e)}", exc_info=True) 