














# backend/app/api/chat.py

import asyncio
import datetime
import traceback
from typing import Optional, List, Dict

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
    1. Calls the AI agent asynchronously
    2. Persists user and AI messages in MySQL
    3. Returns a fully validated ChatResponse
    """
    try:
        agent = get_ai_agent()

        # -------------------------------
        # Call agent asynchronously
        # -------------------------------
        try:
            # If agent.chat is synchronous, run in thread to avoid blocking event loop
            ai_result = await asyncio.to_thread(
                agent.chat,
                message=request.message,
                session_id=request.session_id,
                conversation_history=request.conversation_history or []
            )
        except Exception as e:
            # Fallback in case agent fails
            print(f"[WARN] AI agent call failed: {e}")
            ai_result = {"response": "Sorry, I could not generate a response."}

        # -------------------------------
        # Normalize AI response
        # -------------------------------
        if isinstance(ai_result, dict):
            response_text = str(ai_result.get("response", "Sorry, I could not generate a response."))
            sources = ai_result.get("sources", [])
            retrieved = ai_result.get("retrieved", False)
        else:
            # If AI returned raw string
            response_text = str(ai_result)
            sources = []
            retrieved = False

        # Ensure all fields required by ChatResponse exist
        response_dict = {
            "session_id": request.session_id,
            "response": response_text,
            "sources": sources,
            "retrieved": retrieved,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        # -------------------------------
        # Persist user message
        # -------------------------------
        user_msg = Message(
            session_id=request.session_id,
            role="user",
            content=request.message,
            extra_data={}  # No extra data for user messages
        )
        db.add(user_msg)

        # -------------------------------
        # Persist AI message
        # -------------------------------
        ai_msg = Message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            extra_data=ai_result  # Full AI response
        )
        db.add(ai_msg)

        # Commit all messages atomically
        db.commit()
        db.refresh(user_msg)
        db.refresh(ai_msg)

        # -------------------------------
        # Return response to frontend
        # -------------------------------
        return ChatResponse(**response_dict)

    except Exception as e:
        print(f"[ERROR] Unexpected error in chat_endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error.")
