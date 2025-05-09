from fastapi import APIRouter, Depends, Path
from services.auth import verify_token
from services.report import generate_report_service, get_report_service

router = APIRouter(prefix="/chat", tags=["report"])

@router.post("/report/generate/{session_id}")
async def generate_report(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(verify_token)
) -> dict:
    return await generate_report_service(session_id, user_id)

@router.get("/report/{session_id}")
async def get_report(
    session_id: str = Path(..., description="Session ID"),
    user_id: str = Depends(verify_token)
) -> dict:
    return await get_report_service(session_id) 