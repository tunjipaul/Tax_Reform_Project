from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_engine import get_ai_agent

router = APIRouter()

# Initialize the AI agent once (singleton)
agent = get_ai_agent()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = agent.chat(
            message=request.message,
            session_id=request.session_id,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
