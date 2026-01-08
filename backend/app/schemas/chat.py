from pydantic import BaseModel, constr, Field
from typing import List, Dict, Optional

class ChatMessage(BaseModel):
    role: constr(min_length=1, max_length=10)  # 'user' or 'assistant'
    content: constr(min_length=1, max_length=2000)

class ChatRequest(BaseModel):
    session_id: constr(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$"  # <-- Pydantic v2 change
    ) = Field(..., description="Unique session ID, alphanumeric, dashes/underscores allowed")

    message: constr(min_length=1, max_length=2000) = Field(..., description="User message, max 2000 chars")
    
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[],
        description="Up to 10 previous messages"
    )

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: Optional[List[Dict]] = []
    retrieved: bool
    timestamp: str