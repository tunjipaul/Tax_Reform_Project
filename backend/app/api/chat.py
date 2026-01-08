# # backend/app/api/chat.py

# import asyncio
# import datetime
# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from fastapi.responses import JSONResponse
# from app.schemas.chat import ChatRequest, ChatResponse
# from app.db.models import Message
# from app.db.database import SessionLocal
# from app.services.ai_engine import get_ai_agent

# router = APIRouter(prefix="/api/chat", tags=["Chat"])

# # -------------------------------
# # Dependency to get DB session
# # -------------------------------
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # -------------------------------
# # Chat endpoint with timeout & async
# # -------------------------------
# @router.post("/", response_model=ChatResponse)
# async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
#     """
#     Handles chat requests:
#     1. Calls the AI agent asynchronously
#     2. Persists user and AI messages
#     3. Enforces a timeout to prevent blocking
#     """
#     try:
#         # Get AI agent (may raise RuntimeError if not initialized)
#         agent = get_ai_agent()

#         # -------------------------------
#         # Run AI operation with timeout
#         # -------------------------------
#         TIMEOUT_SECONDS = 15  # adjust based on expected response times

#         try:
#             response_dict = await asyncio.wait_for(
#                 asyncio.to_thread(
#                     agent.chat,
#                     message=request.message,
#                     session_id=request.session_id,
#                     conversation_history=request.conversation_history
#                 ),
#                 timeout=TIMEOUT_SECONDS
#             )
#         except asyncio.TimeoutError:
#             # Timeout: return friendly error to client
#             response_dict = {
#                 "session_id": request.session_id,
#                 "response": "Sorry, the AI took too long to respond. Please try again.",
#                 "sources": [],
#                 "retrieved": False,
#                 "timestamp": datetime.datetime.utcnow().isoformat()
#             }

#         # Ensure response_dict has required keys
#         response_text = str(response_dict.get("response", ""))
#         if not response_text:
#             response_text = "Sorry, I could not generate a response."

#         # -------------------------------
#         # Persist user message
#         # -------------------------------
#         user_msg = Message(
#             session_id=request.session_id,
#             role="user",
#             content=request.message,
#             extra_data={}  # user messages don't have extra data
#         )
#         db.add(user_msg)

#         # -------------------------------
#         # Persist AI message
#         # -------------------------------
#         ai_msg = Message(
#             session_id=request.session_id,
#             role="assistant",
#             content=response_text,
#             extra_data=response_dict  # store full AI response for debugging
#         )
#         db.add(ai_msg)

#         # Commit all messages
#         db.commit()
#         db.refresh(user_msg)
#         db.refresh(ai_msg)

#         # -------------------------------
#         # Return sanitized response to frontend
#         # -------------------------------
#         return ChatResponse(**response_dict)

#     except RuntimeError as re:
#         # AI not initialized yet
#         return JSONResponse(
#             status_code=503,
#             content={
#                 "detail": "AI engine is still starting. Please try again shortly."
#             }
#         )
#     except Exception as e:
#         # Catch-all (won't expose internal error thanks to middleware)
#         print(f"[ERROR] Unexpected error in chat_endpoint: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error.")




from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
import asyncio

from app.schemas.chat import ChatRequest, ChatResponse
from app.db.models import Message
from app.db.database import SessionLocal
from app.services.ai_engine import chat_with_agent

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# -------------------------------
# DB Dependency
# -------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# Chat Endpoint (RATE LIMITED)
# -------------------------------
@router.post("/", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat_endpoint(
    request: Request,
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Handles chat requests using the singleton AI engine.
    """

    try:
        response_dict = await asyncio.wait_for(
            chat_with_agent(
                message=payload.message,
                session_id=payload.session_id,
                conversation_history=payload.conversation_history,
            ),
            timeout=30,
        )

        # Save messages (non-blocking)
        try:
            db.add(Message(
                session_id=payload.session_id,
                role="user",
                content=payload.message,
                extra_data={}
            ))

            db.add(Message(
                session_id=payload.session_id,
                role="assistant",
                content=response_dict["response"],
                extra_data=response_dict
            ))

            db.commit()
        except Exception as db_err:
            print(f"⚠️ DB write failed: {db_err}")

        return ChatResponse(**response_dict)

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="AI response timed out.")

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")
