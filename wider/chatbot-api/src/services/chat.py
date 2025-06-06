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
    get_session_summary
)
from services.report import generate_report_for_session
from prompts.question import question_prompt
from prompts.evaluation import eval_prompt
from models.schemas import ChatResponse

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
            question = question_chain.invoke({
                "topic": topic,
                "bloom_level": 1,
                "chat_history": "",
                "question": ""
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
        
        return ChatResponse(
            session_id=session_id,
            topic=topic,
            current_level=1,
            question=question,
            message=f"안녕하세요! 오늘의 주제는 '{topic}'입니다. 첫 번째 질문을 드리겠습니다.",
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
        
        # 2. 세션 메모리 가져오기
        memory = get_session_memory(session_id)
        
        # 3. 사용자 응답을 메모리에 저장
        memory.save_context(
            {"input": current_question["question"]},
            {"output": user_answer}
        )
        
        # 4. 응답 평가
        try:
            eval_response = eval_chain.invoke({
                "question": current_question["question"],
                "bloom_level": current_question["bloom_level"],
                "user_answer": user_answer
            }).content
            
            try:
                evaluation = json.loads(eval_response)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from eval_chain: {eval_response}")
                # 기본 평가 결과 반환
                evaluation = {
                    "is_appropriate": False,
                    "feedback": "응답을 평가하는 데 문제가 발생했습니다. 다시 시도해주세요.",
                    "is_looking_for_help": False,
                    "hint": "이 주제에 대해 더 깊이 생각해볼 수 있을까요?"
                }
            
            # 필수 필드 확인 및 기본값 설정
            required_fields = {
                "is_appropriate": False,
                "feedback": "응답을 평가하는 데 문제가 발생했습니다.",
                "is_looking_for_help": False,
                "hint": "이 주제에 대해 더 깊이 생각해볼 수 있을까요?"
            }
            
            for field, default_value in required_fields.items():
                if field not in evaluation or evaluation[field] is None:
                    logger.warning(f"Missing or null field '{field}' in evaluation, using default value")
                    evaluation[field] = default_value
            
            logger.info(f"Response evaluation completed for session {session_id}")
        except Exception as e:
            logger.error(f"Error evaluating response: {str(e)}")
            # 기본 평가 결과 반환
            evaluation = {
                "is_appropriate": False,
                "feedback": "응답을 평가하는 데 문제가 발생했습니다. 다시 시도해주세요.",
                "is_looking_for_help": False,
                "hint": "이 주제에 대해 더 깊이 생각해볼 수 있을까요?"
            }
        
        # 5. 응답이 적절한 경우에만 answered로 마크
        if evaluation["is_appropriate"]:
            mark_answered(
                session_id,
                current_question["bloom_level"],
                user_answer
            )
            logger.info(f"Marked answer as appropriate for session {session_id}")
            
            # 6. 다음 단계 결정
            next_level = current_question["bloom_level"] + 1
            
            if next_level <= 6:
                # 다음 단계로 진행
                chat_history = format_chat_history(memory)
                
                try:
                    next_question = question_chain.invoke({
                        "topic": topic,
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
                if session_id in session_memories:
                    del session_memories[session_id]
                logger.info(f"Session {session_id} completed all levels")
                
                # 6단계 완료 시 바로 리포트 생성
                try:
                    await generate_report_for_session(session_id, user_id)
                    logger.info(f"Generated report for completed session {session_id}")
                except Exception as e:
                    logger.error(f"Error generating report: {str(e)}")
                
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
                current_level=current_level,
                question=current_question["question"],
                message=message,
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