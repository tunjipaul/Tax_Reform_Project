"""
main.py
FastAPI Backend for Nigeria Tax Reform Bills Q&A Assistant.
Connects the React Frontend to the AI Engine.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# Add root directory to path so we can import ai_engine
# This ensures we can find 'ai_engine' even if running from backend/ folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.agent import create_agent, TaxQAAgent
from ai_engine.vector_store import VectorStore
from ai_engine.config import config
# Import for auto-ingestion capability
from ai_engine.document_processor import load_and_chunk_documents

# --- GLOBAL STATE ---
ai_agent: Optional[TaxQAAgent] = None

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    Initializes the AI Agent and performs auto-ingestion if DB is empty.
    """
    global ai_agent
    print("🚀 BACKEND: Initializing AI Engine...")
    
    try:
        # Initialize Vector Store (connects to existing persistent DB or creates new)
        store = VectorStore()
        store.create_collection() 
        
        # --- AUTO-INGESTION CHECK ---
        # Check if the collection is empty (e.g., fresh git clone)
        stats = store.get_collection_stats()
        doc_count = stats.get("total_documents", 0)
        
        if doc_count == 0:
            print("⚠️ Collection is empty. Starting automatic data ingestion...")
            print(f"📂 Looking for documents in: {config.DOCS_DIRECTORY}")
            
            # Run ingestion pipeline
            chunks = load_and_chunk_documents()
            
            if chunks:
                store.add_documents(chunks)
                print(f"✅ Auto-ingestion complete! Added {len(chunks)} chunks.")
            else:
                print("❌ No documents found to ingest. Agent will have no knowledge.")
        else:
            print(f"✅ Found existing collection with {doc_count} documents.")
            
        # Create the Agent
        ai_agent = create_agent(store)
        print("✅ BACKEND: AI Agent Ready!")
        
    except Exception as e:
        print(f"❌ BACKEND: Failed to initialize AI Agent: {e}")
        # We don't raise here to allow the API to start, but /api/chat will fail gracefully
    
    yield
    
    print("🛑 BACKEND: Shutting down...")

# --- APP SETUP ---
app = FastAPI(
    title="Nigeria Tax Reform Q&A API",
    description="AI-powered assistant for Nigeria's 2024 Tax Reform Bills",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration (Allow Frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve PDF documents
from fastapi.staticfiles import StaticFiles
documents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_engine", "documents")
if os.path.exists(documents_path):
    app.mount("/documents", StaticFiles(directory=documents_path), name="documents")
    print(f"📄 Serving documents from: {documents_path}")


# --- DATA MODELS (Pydantic) ---

class ChatRequest(BaseModel):
    """Data sent from Frontend"""
    session_id: str = Field(..., description="Unique identifier for the user session")
    message: str = Field(..., description="The user's question")
    # Optional: Frontend can send history if not managed statefully in backend DB yet
    history: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation history")

class SourceCitation(BaseModel):
    """Structure of a source citation"""
    document: str
    type: str
    score: float
    excerpt: str

class ChatResponse(BaseModel):
    """Data sent back to Frontend"""
    session_id: str
    response: str
    sources: List[SourceCitation] = []
    retrieved: bool
    timestamp: str

# --- ENDPOINTS ---
@app.get("/")
async def root():
    return {"message": "Welcome to the Nigeria Tax Reform Bills Q&A API"}

@app.get("/health")
async def health_check():
    """Simple health check to verify backend is running"""
    return {
        "status": "healthy",
        "ai_engine": "connected" if ai_agent else "disconnected"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main Chat Endpoint.
    Receives user message, queries AI Agent, returns answer with sources.
    """
    global ai_agent
    
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Engine is not initialized")
    
    try:
        print(f"📨 Request from {request.session_id}: {request.message[:50]}...")
        
        # Call the AI Engine
        # Note: In a high-traffic app, we'd wrap this blocking call 
        # in `await run_in_threadpool(ai_agent.chat, ...)`
        result = ai_agent.chat(
            message=request.message,
            session_id=request.session_id,
            conversation_history=request.history
        )
        
        # Format response to match Pydantic model
        response_data = ChatResponse(
            session_id=result["session_id"],
            response=result["response"],
            sources=[
                SourceCitation(
                    document=s.get("document", "Unknown"),
                    type=s.get("type", "Unknown"),
                    score=float(s.get("score", 0.0)),
                    excerpt=s.get("excerpt", "")
                ) 
                for s in result.get("sources", [])
            ],
            retrieved=result.get("retrieved", False),
            timestamp=result.get("timestamp", "")
        )
        
        return response_data

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- SESSIONS ENDPOINTS ---

@app.get("/api/sessions")
async def list_sessions():
    """
    List all conversation sessions with metadata.
    Used by frontend sidebar to show chat history.
    """
    global ai_agent
    
    if not ai_agent:
        return {"sessions": []}
    
    sessions = []
    for session_id in ai_agent.memory.get_all_sessions():
        info = ai_agent.memory.get_session_info(session_id)
        history = ai_agent.memory.get_history(session_id, limit=1)
        
        # Get first user message as title
        first_message = next(
            (msg["content"] for msg in ai_agent.memory.get_history(session_id) if msg["role"] == "user"),
            "New Chat"
        )
        
        sessions.append({
            "session_id": session_id,
            "title": first_message[:40] + "..." if len(first_message) > 40 else first_message,
            "created_at": info.get("created_at") if info else None,
            "last_active": info.get("last_active") if info else None,
            "message_count": info.get("message_count", 0) if info else 0
        })
    
    # Sort by last_active (most recent first)
    sessions.sort(key=lambda x: x.get("last_active") or "", reverse=True)
    
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get full conversation history for a specific session.
    Used to restore a previous chat when user clicks on it.
    """
    global ai_agent
    
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Engine is not initialized")
    
    history = ai_agent.memory.get_history(session_id)
    info = ai_agent.memory.get_session_info(session_id)
    
    if not history:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Transform messages to frontend format
    messages = []
    for msg in history:
        messages.append({
            "text": msg["content"],
            "isUser": msg["role"] == "user",
            "timestamp": msg.get("timestamp", ""),
            "showActions": msg["role"] == "assistant"
        })
    
    return {
        "session_id": session_id,
        "messages": messages,
        "metadata": info
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Clear a specific session's history"""
    global ai_agent
    
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Engine is not initialized")
    
    ai_agent.memory.clear_session(session_id)
    return {"success": True, "message": f"Session {session_id} cleared"}


if __name__ == "__main__":
    # Run development server
    uvicorn.run("backend.main:app", port=8000, reload=True)