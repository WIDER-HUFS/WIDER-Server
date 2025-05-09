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
    ChatResponse
)

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
        request.topic
    )

@router.post("/end")
async def end_chat(
    request: EndChatRequest,
    user_id: str = Depends(verify_token)
) -> dict:
    return await end_chat_service(request.session_id) 