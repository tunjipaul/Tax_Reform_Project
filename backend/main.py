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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.agent import create_agent, TaxQAAgent
from ai_engine.vector_store import VectorStore
from ai_engine.config import config

# --- GLOBAL STATE ---
ai_agent: Optional[TaxQAAgent] = None

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    Initializes the AI Agent once to keep DB connection alive.
    """
    global ai_agent
    print("🚀 BACKEND: Initializing AI Engine...")
    
    try:
        # Initialize Vector Store (connects to existing persistent DB)
        store = VectorStore()
        store.create_collection() # Connects to existing collection
        
        # Create the Agent
        ai_agent = create_agent(store)
        print("✅ BACKEND: AI Agent Ready!")
    except Exception as e:
        print(f"❌ BACKEND: Failed to initialize AI Agent: {e}")
    
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
    return {"message": "Welcome to the Nigeria Tax Reform Bills Q&A Assistant API"}

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

if __name__ == "__main__":
    # Run development server
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)