















# backend/app/api/chat.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.db.models import Message
from app.db.database import SessionLocal
from app.services.ai_engine import get_ai_agent

router = APIRouter(prefix="/api/chat")

# -------------------------------
# Dependency to get DB session
# -------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# Chat endpoint
# -------------------------------
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Handles chat requests:
    1. Calls the AI agent
    2. Persists user and AI messages in MySQL
    """

    try:
        # Get AI agent
        agent = get_ai_agent()

        # Call agent asynchronously (if agent supports async, otherwise use thread)
        # Here we assume agent.chat is a regular method returning a dict
        import asyncio
        response_dict = await asyncio.to_thread(
            agent.chat,
            message=request.message,
            session_id=request.session_id,
            conversation_history=request.conversation_history
        )

        # Validate response dict keys
        response_text = response_dict.get("response", "")
        if not response_text:
            response_text = "Sorry, I could not generate a response."

        # -------------------------------
        # Persist user message
        # -------------------------------
        user_msg = Message(
            session_id=request.session_id,
            role="user",
            content=request.message,
            extra_data={}  # empty for user messages
        )
        db.add(user_msg)

        # -------------------------------
        # Persist AI message
        # -------------------------------
        ai_msg = Message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            extra_data=response_dict  # full AI response dict
        )
        db.add(ai_msg)

        # Commit all messages
        db.commit()
        db.refresh(user_msg)
        db.refresh(ai_msg)

        # Return only what frontend needs
        return ChatResponse(**response_dict)

    except Exception as e:
        # Log the error
        print(f"[ERROR] Unexpected error in chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
