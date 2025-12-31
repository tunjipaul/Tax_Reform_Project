from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str
    conversation_history: Optional[List[Dict]] = []

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: Optional[List[Dict]] = []
    retrieved: bool
    timestamp: str
