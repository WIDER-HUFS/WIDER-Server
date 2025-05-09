from pydantic import BaseModel
from typing import Optional, Dict, Any

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

class ReportResponse(BaseModel):
    session_id: str
    report: Dict[str, Any] 