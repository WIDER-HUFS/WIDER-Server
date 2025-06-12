from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class StartChatRequest(BaseModel):
    topic: Optional[str] = None

class UserResponseRequest(BaseModel):
    session_id: str
    user_answer: str
    current_level: int
    topic: str
    topic_prompt: str

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

class ChatSession(BaseModel):
    session_id: str
    topic: str
    started_at: str
    completed: bool
    completed_at: Optional[str]
    message_count: int

class ConversationMessage(BaseModel):
    speaker: str
    content: str
    timestamp: str
    message_order: int

class ConversationHistory(BaseModel):
    session_id: str
    topic: str
    current_level: int
    is_complete: bool
    messages: List[ConversationMessage] 