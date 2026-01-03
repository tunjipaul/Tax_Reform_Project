from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.session_repo import add_message, get_recent_messages
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_engine import get_ai_agent

router = APIRouter()
agent = get_ai_agent()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        history = get_recent_messages(db, request.session_id, limit=10)
        formatted_history = [{"role": m.role, "content": m.content} for m in history]

        response = agent.chat(
            message=request.message,
            session_id=request.session_id,
            conversation_history=formatted_history
        )

        add_message(db, request.session_id, "user", request.message)
        add_message(db, request.session_id, "assistant", response["response"],
                    metadata={"sources": response.get("sources")})

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
