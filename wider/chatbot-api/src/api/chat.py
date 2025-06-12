from fastapi import APIRouter, Depends, HTTPException
from services.auth import verify_token
from services.chat import (
    start_chat_service,
    process_response_service,
    end_chat_service
)
from models.schemas import (
    StartChatRequest,
    UserResponseRequest,
    EndChatRequest,
    ChatResponse,
    ConversationHistory,
    ConversationMessage
)
from database.db import get_conversation_history, get_session_info, get_session_max_bloom_level
from typing import List
import logging

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/start")
async def start_chat(
    request: StartChatRequest,
    user_id: str = Depends(verify_token)
) -> ChatResponse:
    return await start_chat_service(request.topic, user_id)

@router.post("/respond")
async def process_response(
    request: UserResponseRequest,
    user_id: str = Depends(verify_token)
) -> ChatResponse:
    return await process_response_service(
        request.session_id,
        request.user_answer,
        request.current_level,
        request.topic,
        request.topic_prompt,
        user_id
    )

@router.post("/end")
async def end_chat(
    request: EndChatRequest,
    user_id: str = Depends(verify_token)
) -> dict:
    return await end_chat_service(request.session_id)

@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history_endpoint(
    session_id: str,
    user_id: str = Depends(verify_token)
) -> ConversationHistory:
    """특정 세션의 대화 기록을 가져옵니다."""
    try:
        # 대화 기록 가져오기
        messages = get_conversation_history(session_id)
        
        # 세션 정보 가져오기
        session_info = get_session_info(session_id)
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="세션을 찾을 수 없습니다."
            )
            
        # 세션의 최고 Bloom 레벨 가져오기
        max_bloom_level = get_session_max_bloom_level(session_id)
            
        return ConversationHistory(
            session_id=session_id,
            topic=session_info["topic"],
            current_level=max_bloom_level,  # questions 테이블에서 조회한 최고 레벨 사용
            is_complete=session_info["completed"],
            messages=[
                ConversationMessage(
                    speaker=msg["speaker"],
                    content=msg["content"],
                    timestamp=msg["timestamp"].isoformat(),
                    message_order=msg.get("message_order", 0)
                )
                for msg in messages
            ]
        )
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"대화 기록을 가져오는 중 오류가 발생했습니다: {str(e)}"
        ) 