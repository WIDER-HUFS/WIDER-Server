from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional
import httpx
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class LevelProgress(BaseModel):
    session_id: str
    started_at: datetime
    max_bloom_level: int

@router.get("/level-progress", response_model=List[LevelProgress])
async def get_level_progress(authorization: Optional[str] = Header(None)):
    """
    세션별 최고 레벨 진행도를 조회합니다.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )

    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": authorization}
            response = await client.get(
                "http://localhost:8080/api/level-progress",
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch level progress data"
                )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching level progress: {str(e)}"
        ) 