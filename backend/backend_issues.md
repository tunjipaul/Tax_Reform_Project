# Backend - Critical & High-Severity Issues

**Last Updated:** January 1, 2026  
**Severity Levels:** 🔴 Critical | 🟠 High | 🟡 Medium

---

## Table of Contents
1. [Critical Issues](#critical-issues)
2. [High-Severity Issues](#high-severity-issues)
3. [Medium-Severity Issues](#medium-severity-issues)
4. [Architecture Problems](#architecture-problems)
5. [Testing & Documentation](#testing--documentation)
6. [Resolution Timeline](#resolution-timeline)

---

## Critical Issues

### 🔴 Issue #1: Document Loading Blocks Startup

**File:** `app/services/ai_engine.py` (lines 6-12)  
**Severity:** 🔴 CRITICAL  
**Status:** Open

#### Problem
Document processing runs at module import time:

```python
# backend/app/services/ai_engine.py
chunks = load_and_chunk_documents()  # Runs immediately on import!
vector_store = initialize_vector_store(chunks, reset=False)
```

**Why It's Critical:**
- Server startup hangs until ALL documents are processed
- For 10,000 pages of PDFs, could take 10-30 minutes
- If documents corrupt, server won't start at all
- Deployment becomes fragile and slow

**Timeline Example:**
```
FastAPI server startup sequence:
1. Import app module
2. Import ai_engine.py
3. load_and_chunk_documents() runs
   - Find all PDFs
   - Extract text from pages
   - Create 5000+ chunks
   - Generate embeddings for each chunk
   [WAITING 15+ MINUTES...]
4. initialize_vector_store() completes
5. Server finally accepts requests
```

**Risk Scenarios:**
- Deploy at 9:55 AM, server doesn't respond until 10:10 AM
- CI/CD pipeline timeout on deployment
- Health checks fail during startup
- Rolling deployment leaves services down

#### Solution
```python
# backend/app/services/ai_engine.py
from contextlib import asynccontextmanager
from ai_engine.agent import TaxQAAgent
from ai_engine.vector_store import VectorStore

# Don't load here - will be loaded in lifespan
_ai_agent: TaxQAAgent | None = None
_vector_store: VectorStore | None = None

def get_ai_agent() -> TaxQAAgent:
    """Returns initialized AI agent"""
    if _ai_agent is None:
        raise RuntimeError("AI Agent not initialized. Wait for server startup.")
    return _ai_agent

async def initialize_ai_engine():
    """Initialize AI engine in background during startup"""
    global _ai_agent, _vector_store
    
    try:
        print("🤖 Initializing AI Engine...")
        
        from ai_engine.document_processor import load_and_chunk_documents
        from ai_engine.vector_store import initialize_vector_store
        
        # Load documents
        print("📚 Loading documents...")
        chunks = load_and_chunk_documents()
        
        if not chunks:
            raise RuntimeError("No documents loaded!")
        
        # Initialize vector store
        print("🗄️ Initializing vector store...")
        _vector_store = initialize_vector_store(chunks, reset=False)
        
        # Create agent
        print("🤖 Creating agent...")
        _ai_agent = TaxQAAgent(_vector_store)
        
        print("✅ AI Engine initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize AI Engine: {e}")
        raise

# In main.py:
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import chat
from app.services.ai_engine import initialize_ai_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_ai_engine()
    yield
    # Shutdown
    print("🛑 Shutting down...")

app = FastAPI(
    title="Nigeria Tax Q&A Assistant",
    lifespan=lifespan
)

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/health")
def health():
    return {"status": "ready"}
```

#### Acceptance Criteria
- [ ] Move document loading to `lifespan` startup
- [ ] Server responds to `/health` before AI engine ready
- [ ] AI engine initialization doesn't block other routes
- [ ] Startup takes < 5 minutes for 10,000 pages
- [ ] Clear error message if AI engine fails to initialize

---

### 🔴 Issue #2: Duplicate Session Storage - Data Loss

**Files:** `app/core/sessions.py`, `app/api/chat.py`, `ai_engine/memory.py`  
**Severity:** 🔴 CRITICAL  
**Status:** Open

#### Problem
Two separate, unsynchronized session stores:

```python
# Backend (app/core/sessions.py)
sessions: Dict[str, List[Dict]] = {}

def add_message(session_id: str, role: str, content: str):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"role": role, "content": content})

# AI Engine (ai_engine/memory.py)
class ConversationMemory:
    def __init__(self):
        self.sessions: Dict[str, List[Dict]] = defaultdict(list)
        # Completely separate storage!
```

**Why It's Critical:**
- Backend updates one, AI engine updates the other
- No synchronization between them
- Changes don't propagate
- Data consistency broken

**Data Loss Scenario:**
```
1. User sends message
   Backend: saves to sessions.py
   AI Engine: saves to memory.py

2. Backend tries to get history for follow-up:
   Uses sessions.py (correct)

3. AI Engine independently saves response to memory.py
   But backend never reads from memory.py!

4. Message exchange is fragmented:
   Backend knows: [user_msg]
   AI Engine knows: [user_msg, ai_response]
   
5. Next request, AI Engine gets incomplete history

6. User loses context, gets generic responses
```

**Real Example:**
```
User: "What's the income tax threshold?"
AI Engine saves to memory.py
Response returned to frontend

User: "What if I earn more than that?"
Backend retrieves from sessions.py (empty or incomplete)
Passes to AI Engine
AI Engine has no context because it only uses internal memory.py

Result: AI answers generic tax question, not follow-up
```

#### Solution
**Option 1: Single Source of Truth in Backend (RECOMMENDED)**

```python
# app/core/sessions.py - become the single source of truth
from typing import Dict, List
import asyncio
from datetime import datetime

class SessionManager:
    """Centralized session management"""
    
    def __init__(self):
        self._sessions: Dict[str, List[Dict]] = {}
        self._lock = asyncio.Lock()  # For thread safety
    
    async def get_history(self, session_id: str) -> List[Dict]:
        """Get all messages for a session"""
        async with self._lock:
            return self._sessions.get(session_id, []).copy()
    
    async def add_message(self, session_id: str, role: str, content: str, 
                         metadata: Dict = None):
        """Add message and automatically save"""
        async with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            self._sessions[session_id].append(message)
            
            # TODO: Persist to database
            # db.save_message(session_id, message)
    
    async def clear_session(self, session_id: str):
        """Clear session history"""
        async with self._lock:
            self._sessions.pop(session_id, None)
            # TODO: Delete from database

# Singleton instance
session_manager = SessionManager()

# In app/api/chat.py
from app.core.sessions import session_manager

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Get history from backend
        history = await session_manager.get_history(request.session_id)
        
        # Call AI engine with backend history
        # AI engine doesn't manage its own memory - uses provided history
        response = agent.chat(
            message=request.message,
            session_id=request.session_id,
            conversation_history=history
        )
        
        # Save user message
        await session_manager.add_message(
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        
        # Save AI response
        await session_manager.add_message(
            session_id=request.session_id,
            role="assistant",
            content=response["response"],
            metadata={"sources": response.get("sources", [])}
        )
        
        return response
        
    except Exception as e:
        # Log and handle error
        raise HTTPException(status_code=500, detail="Failed to process chat")
```

**Option 2: Database-Backed Sessions (FOR PRODUCTION)**

```python
# Use PostgreSQL or Redis for persistence
# app/core/sessions.py with SQLAlchemy

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SessionRecord(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String(255), primary_key=True)
    messages = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class SessionManager:
    async def get_history(self, session_id: str) -> List[Dict]:
        session = db.query(SessionRecord).filter_by(session_id=session_id).first()
        return session.messages if session else []
    
    async def add_message(self, session_id: str, role: str, content: str):
        session = db.query(SessionRecord).filter_by(session_id=session_id).first()
        
        if not session:
            session = SessionRecord(session_id=session_id, messages=[])
        
        session.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        session.last_active = datetime.utcnow()
        
        db.add(session)
        db.commit()
```

#### Acceptance Criteria
- [ ] Remove duplicate session storage in ai_engine/memory.py
- [ ] Backend manages all session history
- [ ] AI engine receives history as parameter, doesn't store it
- [ ] All messages saved through single SessionManager
- [ ] Persistence to database (Redis or PostgreSQL)
- [ ] Test concurrent requests to same session

---

### 🔴 Issue #3: Blocking AI Operations in Async Context

**File:** `app/api/chat.py` (line 13)  
**Severity:** 🔴 CRITICAL  
**Status:** Open

#### Problem
FastAPI endpoint is async but calls blocking AI operation:

```python
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):  # async!
    try:
        response = agent.chat(  # BLOCKING! Ties up event loop
            message=request.message,
            session_id=request.session_id,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Why It's Critical:**
- `agent.chat()` is synchronous and takes 2-5 seconds
- During this time, FastAPI event loop is blocked
- All other requests must wait
- Server becomes unresponsive under load

**Real Impact:**
```
Scenario: 10 concurrent requests arrive
Request 1: starts agent.chat() → blocks event loop [2 seconds]
Request 2-10: QUEUED, waiting for event loop to free up
Timeline:
  t=0s: Request 1 starts processing
  t=1s: Requests 2-10 waiting... ⏳
  t=2s: Request 1 completes, Request 2 starts
  t=4s: Request 2 completes, Request 3 starts
  ...
  t=20s: Request 10 completes (18 seconds later!)

User experience: API feels slow, timeout errors
```

#### Solution
```python
# app/api/chat.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
import asyncio

router = APIRouter()
agent = get_ai_agent()

# Create thread pool for blocking operations
thread_pool = ThreadPoolExecutor(max_workers=5)

def _chat_blocking(message: str, session_id: str, history: List[Dict]) -> Dict:
    """Blocking chat operation"""
    return agent.chat(
        message=message,
        session_id=session_id,
        conversation_history=history
    )

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint - offloads blocking operations to thread pool"""
    try:
        # Validate input first (fast, non-blocking)
        if not request.session_id or not request.message:
            raise HTTPException(status_code=400, detail="Invalid request")
        
        # Get conversation history
        history = await session_manager.get_history(request.session_id)
        
        # Run blocking operation in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            thread_pool,
            _chat_blocking,
            request.message,
            request.session_id,
            history
        )
        
        # Save to session store
        await session_manager.add_message(
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        
        await session_manager.add_message(
            session_id=request.session_id,
            role="assistant",
            content=response["response"],
            metadata={"sources": response.get("sources", [])}
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat")

# Alternative: Make agent async
# async def _async_chat(...):
#     return await agent.chat_async(...)
```

#### Acceptance Criteria
- [ ] Use `run_in_executor` for blocking AI operations
- [ ] Test with 10+ concurrent requests
- [ ] Response time consistent under load
- [ ] No timeout errors
- [ ] Event loop not blocked

---

### 🔴 Issue #4: No Input Validation - DoS Vulnerability

**Files:** `app/schemas/chat.py`, `app/api/chat.py`  
**Severity:** 🔴 CRITICAL  
**Status:** Open

#### Problem
Requests accepted with no validation:

```python
# app/schemas/chat.py
class ChatRequest(BaseModel):
    session_id: str           # Could be anything!
    message: str              # Could be 1MB!
    conversation_history: Optional[List[Dict]] = []  # No size limit!

class ChatResponse(BaseModel):
    session_id: str
    response: str             # No length limit
    sources: Optional[List[Dict]] = []
    retrieved: bool
    timestamp: str
```

**Why It's Critical:**
- Accept 10MB message string → memory exhaustion
- Conversation history with 1000 messages → slow processing
- Session ID injection attacks
- No protection against malformed data

**Attack Scenarios:**
```
1. Payload Explosion:
   POST /api/chat with 10MB JSON message
   → Backend tries to embed it
   → Gemini API fails
   → Server crashes

2. DoS via History:
   "conversation_history": [messages repeated 10,000 times]
   → Server processes all
   → CPU/memory spike

3. Injection:
   "session_id": "../../../admin"
   → Path traversal if not handled

4. Long-running queries:
   "message": "..." * 100000
   → Takes 10 minutes to process
   → Ties up thread
```

#### Solution
```python
# app/schemas/chat.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern="^[a-zA-Z0-9_-]+$",  # Alphanumeric, underscore, dash only
        description="Unique session identifier"
    )
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,  # Limit to 5000 chars
        description="User question"
    )
    
    conversation_history: Optional[List[Dict]] = Field(
        default=[],
        max_items=10,  # Max 10 previous messages
        description="Previous messages in conversation"
    )
    
    @validator('message')
    def message_not_only_whitespace(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be only whitespace')
        return v
    
    @validator('conversation_history')
    def validate_history(cls, v):
        """Validate history structure"""
        for item in v:
            if not isinstance(item, dict):
                raise ValueError('History items must be dictionaries')
            if 'role' not in item or 'content' not in item:
                raise ValueError('History items must have role and content')
            if item['role'] not in ['user', 'assistant']:
                raise ValueError('Role must be user or assistant')
            if len(item.get('content', '')) > 5000:
                raise ValueError('History message too long')
        return v

class ChatResponse(BaseModel):
    session_id: str
    response: str = Field(..., max_length=10000)
    sources: Optional[List[Dict]] = Field(default=[], max_items=10)
    retrieved: bool
    timestamp: str

# In chat.py - add validation middleware
from pydantic import ValidationError

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Input validation happens automatically via Pydantic
        # (happens before this function is called)
        
        # Additional runtime checks
        total_history_length = sum(
            len(msg.get('content', '')) 
            for msg in request.conversation_history
        )
        
        if total_history_length > 50000:  # Total 50K chars max
            raise HTTPException(
                status_code=400,
                detail="Conversation history too long"
            )
        
        # ... rest of endpoint
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")
```

#### Acceptance Criteria
- [ ] Add min/max length validators to all fields
- [ ] Add regex validation for session_id
- [ ] Limit conversation history to 10 messages
- [ ] Test with oversized payloads (rejected with 400)
- [ ] Test with malformed data
- [ ] Document API constraints in README

---

### 🔴 Issue #5: Missing Dependencies in requirements.txt

**File:** `requirements.txt`  
**Severity:** 🔴 CRITICAL  
**Status:** Open

#### Problem
Requirements incomplete, installation will fail:

```
fastapi
uvicorn
pydantic

# Missing everything for AI engine!
```

**What's Missing:**
- google-genai (Gemini API)
- langgraph (AI workflow)
- chromadb (Vector database)
- PyPDF2 (Document processing)
- python-dotenv (Config)
- And many others from ai_engine/requirements.txt

**Why It's Critical:**
- `pip install -r requirements.txt` fails
- Server won't start
- Deployment broken
- Developers confused

#### Solution
```
# requirements.txt - COMPLETE LIST

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.3
pydantic-settings==2.1.0

# AI Engine Dependencies
langchain==0.1.0
langchain-core==0.1.10
langchain-community==0.0.13
langgraph==0.0.20

# Google Gemini (NEW SDK)
google-genai==0.3.0

# Vector Database
chromadb==0.4.22

# Document Processing
PyPDF2==3.0.1
python-docx==1.1.0

# Configuration
python-dotenv==1.0.0

# Database (for sessions - optional initially)
sqlalchemy==2.0.23
psycopg2-binary==2.9.9  # PostgreSQL
redis==5.0.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1

# Development
black==23.12.1
flake8==7.0.0
mypy==1.8.0

# Monitoring
python-json-logger==2.0.7

# Additional utilities
requests==2.31.0
aiohttp==3.9.1
```

#### Acceptance Criteria
- [ ] Install all requirements successfully
- [ ] Server starts without import errors
- [ ] All AI engine features work
- [ ] Document which packages are optional

---

## High-Severity Issues

### 🟠 Issue #6: No Error Handling Middleware

**File:** `app/api/chat.py` (line 15-16)  
**Severity:** 🟠 HIGH  
**Status:** Open

#### Problem
Generic exception handler exposes internal details:

```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    # detail = full exception message including stack trace!
```

**Why It's High-Severity:**
- Internal errors exposed to client
- Security risk (reveals implementation details)
- User confusion (sees technical jargon)
- Difficult debugging (can't tell if frontend issue)

**Real Examples Frontend Sees:**
```
"detail": "KeyError: 'chunks' at line 45"
"detail": "ConnectionError: Failed to connect to 127.0.0.1:8000"
"detail": "ValueError: Invalid API key at genai.Client(...)"
"detail": "AttributeError: 'NoneType' object has no attribute 'chat'"
```

#### Solution
```python
# app/api/chat.py
from fastapi import APIRouter, HTTPException
from app.core.logger import logger
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

# Custom exception classes
class AIEngineError(Exception):
    """AI Engine-specific error"""
    pass

class DocumentNotFoundError(Exception):
    """Document retrieval failed"""
    pass

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint with proper error handling
    
    Responses:
    - 200: Success
    - 400: Invalid request
    - 500: Server error (user-friendly message)
    - 503: AI Engine unavailable
    """
    try:
        # Get conversation history
        history = await session_manager.get_history(request.session_id)
        
        # Call AI engine
        try:
            response = await loop.run_in_executor(
                thread_pool,
                agent.chat,
                request.message,
                request.session_id,
                history
            )
        except Exception as e:
            # Log actual error (for debugging)
            logger.error(f"AI Engine error: {type(e).__name__}: {str(e)}", 
                        extra={"session_id": request.session_id})
            
            # Return user-friendly message
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable. Please try again."
            )
        
        # Save messages
        await session_manager.add_message(request.session_id, "user", request.message)
        await session_manager.add_message(request.session_id, "assistant", 
                                         response["response"])
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise
    except ValueError as e:
        # User input errors
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request data")
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {type(e).__name__}: {str(e)}", 
                    exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )

# Add global exception handler
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", 
                exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )
```

#### Acceptance Criteria
- [ ] No stack traces in error responses
- [ ] User-friendly error messages
- [ ] Detailed logging for debugging
- [ ] Different status codes for different errors (400, 503, 500)
- [ ] Test error cases manually

---

### 🟠 Issue #7: No Request Timeout Protection

**File:** `app/api/chat.py`  
**Severity:** 🟠 HIGH  
**Status:** Open

#### Problem
AI operations can take indefinitely, no timeout:

```python
response = agent.chat(...)  # Could wait 5 minutes!
```

**Why It's High-Severity:**
- Clients timeout (default 30s)
- Resources tied up indefinitely
- Memory exhaustion
- Server becomes unresponsive

**Scenario:**
```
User sends message → AI Engine starts processing
→ Gets stuck on vector search
→ 5 minutes pass
→ Client timeout error
→ Server still processing, wasting resources
```

#### Solution
```python
# app/api/chat.py
from asyncio import timeout
import asyncio

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        history = await session_manager.get_history(request.session_id)
        
        # Set timeout for AI operations
        try:
            async with asyncio.timeout(30):  # 30 second timeout
                response = await loop.run_in_executor(
                    thread_pool,
                    agent.chat,
                    request.message,
                    request.session_id,
                    history
                )
        except asyncio.TimeoutError:
            logger.warning(f"Chat timeout for session {request.session_id}")
            raise HTTPException(
                status_code=504,
                detail="Request took too long. Please try a simpler question."
            )
        
        # Save messages
        await session_manager.add_message(request.session_id, "user", request.message)
        await session_manager.add_message(request.session_id, "assistant", 
                                         response["response"])
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat")
```

#### Acceptance Criteria
- [ ] Add 30 second timeout for AI operations
- [ ] Test timeout behavior with slow AI
- [ ] Return 504 on timeout
- [ ] Log timeout events

---

### 🟠 Issue #8: No CORS Configuration

**File:** `app/main.py`  
**Severity:** 🟠 HIGH  
**Status:** Open

#### Problem
No CORS headers configured. Frontend can't call API:

```python
from fastapi import FastAPI

app = FastAPI(title="Nigeria Tax Q&A Assistant")
# No CORS setup!
```

**Why It's High-Severity:**
- Browser blocks cross-origin requests
- Frontend in different domain/port can't call backend
- API appears broken to frontend developers
- Developers waste time debugging this

**Error Users See:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/chat' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

#### Solution
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_ai_engine()
    yield
    # Shutdown

app = FastAPI(
    title="Nigeria Tax Q&A Assistant",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Development frontend
        "http://localhost:5173",      # Vite dev server
        "https://tax-assistant.com",  # Production frontend
        # Add other origins as needed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/health")
def health():
    return {"status": "ready"}

@app.get("/")
def root():
    return {"message": "Welcome to Nigeria Tax Q&A Assistant API"}
```

#### Acceptance Criteria
- [ ] Configure CORS for development and production
- [ ] Test frontend can call backend API
- [ ] Document allowed origins
- [ ] Use environment variables for origins

---

### 🟠 Issue #9: No Rate Limiting

**File:** `app/main.py` & `app/api/chat.py`  
**Severity:** 🟠 HIGH  
**Status:** Open

#### Problem
User can spam requests indefinitely:

```
POST /api/chat
POST /api/chat
POST /api/chat
... (1000 times per second)
```

**Why It's High-Severity:**
- DDoS vulnerability
- Gemini API quota exhausted
- Server resource exhaustion
- Unfair usage by one user

#### Solution
```python
# app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

# In app/api/chat.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/", response_model=ChatResponse)
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat_endpoint(request: ChatRequest):
    # ... endpoint code
```

#### Acceptance Criteria
- [ ] Limit to 10 requests per minute per IP
- [ ] Limit to 100 requests per hour per session
- [ ] Return 429 when limit exceeded
- [ ] Test rate limiting works

---

### 🟠 Issue #10: No Health Check / Startup Validation

**File:** `app/main.py`  
**Severity:** 🟠 HIGH  
**Status:** Open

#### Problem
No way to verify server is ready to handle requests:

```python
# No health endpoint exists
```

**Why It's High-Severity:**
- Load balancer can't determine if server is healthy
- Kubernetes can't know if container should be killed
- Monitors can't track service status
- Deployment issues go unnoticed

#### Solution
```python
# app/main.py
from app.services.ai_engine import get_ai_agent

@app.get("/health")
def health_check():
    """
    Basic health check
    Returns 200 if server is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/ready")
def readiness_check():
    """
    Readiness check - server can handle requests
    Returns 200 only if AI engine is initialized
    """
    try:
        agent = get_ai_agent()
        if agent is None:
            return {"status": "not_ready", "reason": "AI Engine not initialized"}
        
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}

@app.get("/health/live")
def liveness_check():
    """
    Liveness check - server is alive
    Returns 200 unless server should be restarted
    """
    return {"status": "alive"}
```

#### Acceptance Criteria
- [ ] `/health` endpoint returns 200
- [ ] `/health/ready` returns 200 only when AI ready
- [ ] Test with Kubernetes health probes
- [ ] Document in README

---

## Medium-Severity Issues

### 🟡 Issue #11: No Database for Session Persistence

**File:** `app/core/sessions.py`  
**Severity:** 🟡 MEDIUM  
**Status:** Open

#### Problem
Sessions stored in memory only:

```python
sessions: Dict[str, List[Dict]] = {}  # Lost on restart!
```

**Why It's Medium-Severity:**
- Server restart = all conversations lost
- Users lose context after deploy
- Not suitable for production

#### Solution
Implement database persistence:
```python
# Use PostgreSQL + SQLAlchemy
# Or Redis for faster in-memory with persistence

# See Critical Issue #2 for implementation
```

---

### 🟡 Issue #12: No Logging

**Files:** All files  
**Severity:** 🟡 MEDIUM  
**Status:** Open

#### Problem
No structured logging anywhere:

```python
# Current: print statements
print("Starting...")

# Missing: proper logging
logger.info("Starting...", extra={"component": "ai_engine"})
```

**Why It's Medium-Severity:**
- Can't debug production issues
- No request tracing
- No performance monitoring

#### Solution
```python
# app/core/logger.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # JSON handler for structured logging
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# In modules:
from app.core.logger import setup_logger
logger = setup_logger(__name__)

logger.info("Processing chat", extra={
    "session_id": "user_123",
    "message_length": 50,
    "has_history": True
})
```

---

### 🟡 Issue #13: No Dependency Injection

**File:** `app/api/chat.py`  
**Severity:** 🟡 MEDIUM  
**Status:** Open

#### Problem
Global agent instance shared across requests:

```python
agent = get_ai_agent()  # Global singleton

@router.post("/")
async def chat_endpoint(request: ChatRequest):
    response = agent.chat(...)  # Uses global
```

**Why It's Medium-Severity:**
- Difficult to test
- Can't swap implementations
- Implicit dependencies

#### Solution
Use FastAPI dependency injection:
```python
from fastapi import Depends

def get_agent() -> TaxQAAgent:
    return get_ai_agent()

@router.post("/")
async def chat_endpoint(
    request: ChatRequest,
    agent: TaxQAAgent = Depends(get_agent)
):
    response = agent.chat(...)
```

---

### 🟡 Issue #14: No Environment Configuration

**Files:** `app/main.py`, `app/services/ai_engine.py`  
**Severity:** 🟡 MEDIUM  
**Status:** Open

#### Problem
Hard-coded settings, can't adjust for different environments:

```python
# Current: hard-coded
CHUNK_SIZE = 1000

# Missing: environment-based
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
```

#### Solution
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # AI Engine
    DOCS_DIRECTORY: str = "./documents"
    CHUNK_SIZE: int = 1000
    SIMILARITY_THRESHOLD: float = 0.35
    
    # Database
    DATABASE_URL: str = "sqlite:///./chat.db"
    
    # API
    RATE_LIMIT: str = "10/minute"
    REQUEST_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## Architecture Problems

### Problem 1: Blocking Operations in Async Context
FastAPI is async-first, but all operations are blocking.

### Problem 2: Dual Session Stores
Backend and AI engine manage separate session storage with no sync.

### Problem 3: Document Loading at Startup
Blocking initialization prevents server from starting quickly.

### Problem 4: No Persistence
In-memory only = data loss on restart.

### Problem 5: Weak Error Handling
Generic errors expose implementation details.

---

## Testing & Documentation

### 🟡 Issue #15: Minimal Test Coverage

**File:** `tests/test_sessions.py`  
**Severity:** 🟡 MEDIUM  
**Status:** Open

Current coverage:
- Only 2 test functions
- No endpoint tests
- No error cases

Needed:
```python
# tests/test_chat.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint_success():
    response = client.post("/api/chat", json={
        "session_id": "test_user",
        "message": "What is income tax?",
        "conversation_history": []
    })
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_endpoint_invalid_session_id():
    response = client.post("/api/chat", json={
        "session_id": "",  # Empty
        "message": "Hello",
        "conversation_history": []
    })
    assert response.status_code == 400

def test_chat_endpoint_timeout():
    # Mock slow AI engine
    # Should timeout after 30 seconds
    pass

def test_chat_endpoint_concurrent_requests():
    # Test 10 concurrent requests
    # Should not corrupt data
    pass
```

### 🟡 Issue #16: No README

**File:** Missing  
**Severity:** 🟡 MEDIUM  
**Status:** Open

Needed:
```markdown
# Backend - Nigeria Tax Q&A Assistant

## Setup
1. Install requirements
2. Set environment variables
3. Run: uvicorn app.main:app --reload

## API Documentation
GET /health - Health check
POST /api/chat - Send message

## Architecture
- FastAPI for HTTP API
- AI Engine integration
- Session management
```

### 🟡 Issue #17: No Docker Support

Needed:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Resolution Timeline

### Phase 1 (BLOCKING - Immediately)
- [ ] Fix requirements.txt
- [ ] Fix document loading to startup phase
- [ ] Add input validation
- [ ] Fix CORS configuration
- **Target:** Today

### Phase 2 (HIGH - Next Sprint)
- [ ] Implement thread pool for blocking ops
- [ ] Add error handling middleware
- [ ] Implement session manager
- [ ] Add request timeout
- [ ] Add rate limiting
- **Target:** 1 week

### Phase 3 (MEDIUM - 2-4 Sprints)
- [ ] Implement database persistence
- [ ] Add logging
- [ ] Add tests
- [ ] Add documentation
- [ ] Environment configuration
- **Target:** 2-4 weeks

---

## Deployment Checklist

Before deploying:
- [ ] All requirements installed successfully
- [ ] Server starts without errors
- [ ] `/health` endpoint responds
- [ ] `/api/chat` endpoint accepts requests
- [ ] Rate limiting works
- [ ] CORS configured for production domain
- [ ] Error messages are user-friendly
- [ ] Timeouts configured
- [ ] Database persistence working
- [ ] Logging shows all operations
- [ ] Load test with 100+ concurrent users

---

**Prepared By:** Code Analysis  
**Status:** Open Issues - Require Implementation  
**Last Updated:** January 1, 2026
