from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import mysql.connector
from contextlib import contextmanager
from dotenv import load_dotenv
import os
import uuid
import json
from datetime import date
import jwt
from typing import Optional, Dict, Any
import logging

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 환경 설정
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
jwt_secret = os.getenv("JWT_SECRET")
mysql_config = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE")
}

# FastAPI 앱
app = FastAPI()

# JWT 검증 함수
async def verify_token(authorization: str = Header(...)) -> str:
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
            
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload["sub"]  # user_id 반환
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# DB 설정
@contextmanager
def get_db():
    conn = mysql.connector.connect(**mysql_config)
    try:
        yield conn
    finally:
        conn.close()

# DB 헬퍼
def create_session(session_id: str, topic: str, user_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO session_logs (
                session_id, 
                started_at, 
                completed, 
                topic,
                user_id
            )
            VALUES (%s, NOW(), 0, %s, %s)
            """,
            (session_id, topic, user_id)
        )
        conn.commit()

def mark_session_completed(session_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE session_logs
            SET completed = 1, completed_at = NOW()
            WHERE session_id = %s
            """,
            (session_id,)
        )
        conn.commit()

def get_current_question(session_id: str) -> dict:
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT topic, question, bloom_level, is_answered
            FROM questions
            WHERE session_id = %s AND is_answered = 0
            ORDER BY bloom_level ASC LIMIT 1
            """,
            (session_id,)
        )
        row = cursor.fetchone()
        if row:
            return row
        return None

def save_question(session_id: str, topic: str, question: str, bloom_level: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO questions (session_id, topic, question, bloom_level, is_answered)
            VALUES (%s, %s, %s, %s, 0)
            """,
            (session_id, topic, question, bloom_level)
        )
        conn.commit()

def mark_answered(session_id: str, bloom_level: int, user_answer: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE questions
            SET is_answered = 1, user_answer = %s
            WHERE session_id = %s AND bloom_level = %s
            """,
            (user_answer, session_id, bloom_level)
        )
        conn.commit()

def get_daily_topic() -> dict:
    today = str(date.today())
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT topic, topic_prompt
            FROM daily_topic
            WHERE topic_date = %s
            """,
            (today,)
        )
        row = cursor.fetchone()
        if row:
            return row
        return None

# LLM 설정
llm1 = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)
llm2 = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)

# 질문 생성 프롬프트
question_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        당신은 Bloom's Taxonomy(기억, 이해, 적용, 분석, 평가, 창조)에 기반한 질문을 생성하는 전문가입니다.
        주어진 주제({topic})와 Bloom {bloom_level}단계에 맞는 질문을 하나만 생성하세요.
        질문은 간결하고 명확하며, 해당 단계의 인지적 요구를 정확히 반영해야 합니다.
        - 1단계: Remember
        - 사고 수준: 낮음
        - 설명: 정보를 기억하거나 회상
        - 예시 질문: 정부가 발표한 AI 정책의 핵심은 무엇인가요?
        - 2단계: Understand
            - 사고 수준: 낮음 ~ 중간
            - 설명: 정보를 해석, 요약, 설명
            - 예시 질문: 이 정책이 왜 필요한지 설명해보세요.
        - 3단계: Apply
            - 사고 수준: 중간
            - 설명: 배운 지식을 실제 문제에 적용
            - 예시 질문: 이 정책을 학교 교육 현장에 어떻게 적용할 수 있을까요?
        - 4단계: Analyze
            - 사고 수준: 중간 ~ 높음
            - 설명: 정보를 분해, 관계 파악
            - 예시 질문: 이 정책의 각 조항은 어떤 목적을 갖고 있나요?
        - 5단계: Evaluate
            - 사고 수준: 높음
            - 설명: 주장을 비판적 판단, 가치 평가
            - 예시 질문: 이 정책이 사회에 미칠 영향을 어떻게 평가하나요?
        - 6단계: Create
            - 사고 수준: 최고
            - 설명: 새로운 아이디어, 구조, 해법 창출
            - 예시 질문: 더 나은 AI 정책을 설계해 본다면 어떻게 하시겠어요?
        """,
        ),
        ("user", "주제: {topic}, Bloom 단계: {bloom_level}"),
    ]
)

question_chain = question_prompt | llm1

# 응답 평가 프롬프트
eval_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        당신은 사용자의 응답이 질문의 의도에 부합하는지 체크하고, 응답이 부족하다면 피드백을 제공합니다.
        만약 사용자가 잘 모르는 내용이라 도움을 요청한다면, 답변을 제공하진 말고 사용자의 답변을 유도할 수 있도록 힌트를 제공해주세요.
        
        주어진 질문({question})은 Bloom {bloom_level}단계에 해당합니다.
        사용자의 응답({user_answer})을 분석해 다음을 판단하세요:
        1. 응답이 질문의 의도에 부합하는가?
        2. 응답이 충분히 구체적인가?
        3. 사용자가 도움을 요청했는가?
        결과는 JSON으로 반환하세요:
        {{
            "is_appropriate": true/false,
            "feedback": "응답이 적절한 이유 또는 부족한 점"
            "is_looking_for_help": true/false,
            "hint": "사용자의 답변을 이끌어내기 위한 힌트"
        }}
        (단, is_appropriate와 is_looking_for_help가 동시에 true가 될 수 없음을 명심하세요.)
        """,
        ),
        (
            "user",
            """
        질문: {question}
        Bloom 단계: {bloom_level}
        사용자 응답: {user_answer}
        """,
        ),
    ]
)

eval_chain = eval_prompt | llm2

# 1. 데이터 모델 정의
class StartChatRequest(BaseModel):
    topic: Optional[str] = None

class UserResponseRequest(BaseModel):
    session_id: str
    user_answer: str
    current_level: int
    topic: str

class EndChatRequest(BaseModel):
    session_id: str

class ChatResponse(BaseModel):
    session_id: str
    topic: str
    current_level: int
    question: Optional[str] = None
    message: str
    is_complete: bool = False

# 2. 채팅 시작 API
@app.post("/chat/start")
async def start_chat(
    request: StartChatRequest,
    user_id: str = Depends(verify_token)
) -> ChatResponse:
    try:
        # 1. 주제 선택 (요청된 주제가 없으면 오늘의 주제 선택)
        daily_topic = get_daily_topic()
        if not daily_topic:
            raise HTTPException(
                status_code=500,
                detail="오늘의 주제가 설정되지 않았습니다. 잠시 후 다시 시도해주세요."
            )
        
        topic = request.topic or daily_topic["topic"]
        topic_prompt = daily_topic["topic_prompt"]
        
        # 2. 세션 생성
        session_id = str(uuid.uuid4())
        create_session(session_id, topic, user_id)
        
        # 3. Bloom's Taxonomy 1단계 질문 생성
        question = question_chain.invoke({
            "topic": topic,
            "bloom_level": 1
        }).content
        
        save_question(session_id, topic, question, 1)
        
        response = ChatResponse(
            session_id=session_id,
            topic=topic,
            current_level=1,
            question=question,
            message=f"안녕하세요! 오늘의 주제는 '{topic}'입니다. 첫 번째 질문을 드리겠습니다.",
            is_complete=False
        )
        logger.info(f"채팅 시작: {response}")
        return response
    except Exception as e:
        logger.error(f"채팅 시작 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. 사용자 응답 처리 API
@app.post("/chat/respond")
async def process_response(
    request: UserResponseRequest,
    user_id: str = Depends(verify_token)
) -> ChatResponse:
    try:
        # 1. 현재 질문 확인
        current_question = get_current_question(request.session_id)
        logger.info(f"현재 질문: {current_question}")
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
                "user_answer": request.user_answer
            }).content
        )
        
        # 3. 응답 저장
        mark_answered(
            request.session_id,
            current_question["bloom_level"],
            request.user_answer
        )
        
        # 4. 다음 단계 결정
        if evaluation["is_appropriate"]:
            next_level = current_question["bloom_level"] + 1
            
            if next_level <= 6:
                # 다음 단계로 진행
                next_question = question_chain.invoke({
                    "topic": request.topic,
                    "bloom_level": next_level
                }).content
                
                save_question(
                    request.session_id,
                    request.topic,
                    next_question,
                    next_level
                )
                
                
                response = ChatResponse(
                    session_id=request.session_id,
                    topic=request.topic,
                    current_level=next_level,
                    question=next_question,
                    message="좋은 답변입니다! 다음 단계로 넘어가겠습니다.",
                    is_complete=False
                )
                logger.info(f"다음 단계로 넘어가기: {response}")
                return response
            else:
                # 모든 단계 완료
                mark_session_completed(request.session_id)
                response = ChatResponse(
                    session_id=request.session_id,
                    topic=request.topic,
                    current_level=6,
                    question=None,
                    message="모든 단계를 완료하셨습니다! 수고하셨습니다.",
                    is_complete=True
                )
                logger.info(f"모든 단계 완료: {response}")
                return response
        else:
            # 힌트 제공 또는 추가 유도
            message = (
                evaluation["hint"]
                if evaluation["is_looking_for_help"]
                else f"조금 더 생각해볼까요? {evaluation['feedback']}"
            )
            
            response = ChatResponse(
                session_id=request.session_id,
                topic=request.topic,
                current_level=current_question["bloom_level"],
                question=current_question["question"],
                message=message,
                is_complete=False
            )
            logger.info(f"힌트 제공 또는 추가 유도: {response}")
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. 채팅 세션 종료 API
@app.post("/chat/end")
async def end_chat(
    request: EndChatRequest,
    user_id: str = Depends(verify_token)
) -> Dict[str, Any]:
    try:
        # 1. 세션 종료 처리
        mark_session_completed(request.session_id)
        
        # 2. 세션 요약 생성
        session_summary = get_session_summary(request.session_id)
        
        return {
            "session_id": request.session_id,
            "summary": session_summary,
            "message": "오늘의 학습을 마치겠습니다. 수고하셨습니다!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. 세션 요약 조회 함수 (새로 추가)
def get_session_summary(session_id: str) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                q.bloom_level,
                q.question,
                q.user_answer
            FROM questions q
            WHERE q.session_id = %s
            ORDER BY q.bloom_level ASC
            """,
            (session_id,)
        )
        questions = cursor.fetchall()
        
        return {
            "total_questions": len(questions),
            "completed_levels": [q["bloom_level"] for q in questions],
            "questions_and_answers": questions
        }

# 6. 서버 시작 시 실행되는 이벤트
@app.on_event("startup")
async def startup_event():
    # 서버 시작 시 오늘의 주제가 있는지 확인만 하면 됨
    daily_topic = get_daily_topic()
    if not daily_topic:
        print("경고: 오늘의 주제가 아직 선정되지 않았습니다. Airflow DAG가 정상적으로 실행되고 있는지 확인해주세요.") 