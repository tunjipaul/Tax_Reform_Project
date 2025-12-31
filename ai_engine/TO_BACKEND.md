***

# Integration Guide: AI Engine -> FastAPI Backend

**To:** Adems (Backend Engineer)  
**From:** Samuel (AI Engineer)

This guide explains how to integrate the LangGraph AI Engine into your FastAPI application.

---

## 1. Environment Setup

Ensure your backend environment has the required dependencies.

1.  **Copy Files:** Copy the `ai_engine` folder into your root project directory.
2.  **Install Dependencies:**

```bash
pip install -r ai_engine/requirements.txt
```

3.  **Environment Variables:**
    Ensure your `.env` file (or environment configuration) includes the following:

```properties
GEMINI_API_KEY="your_google_api_key_here"

# Optional overrides (defaults exist in config.py)

## Model Configuration
#LLM_MODEL=gemini-2.0-flash-exp
#EMBEDDING_MODEL=text-embedding-004

## Generation Parameters
#TEMPERATURE=0.1
#MAX_TOKENS=2048

## Retrieval Configuration
#CHUNK_SIZE=1000
#CHUNK_OVERLAP=200
#RETRIEVAL_TOP_K=5
#SIMILARITY_THRESHOLD=0.35 # Revised from 0.7

## Memory Configuration
#MAX_CONVERSATION_HISTORY=5

## Paths
#VECTOR_STORE_PATH=./chroma_db
#DOCS_DIRECTORY=./documents

## Logging
#LOG_LEVEL=INFO
#LOG_FILE=ai_engine.log

```

---

## 2. Initialization

You need to initialize the `TaxQAAgent` once when the application starts (e.g., in the `main.py` startup event) to keep the Vector DB connection alive.

**File:** `main.py`

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from ai_engine.agent import create_agent
from ai_engine.vector_store import VectorStore

# Global variable to hold the agent instance
ai_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    global ai_agent
    print("🤖 Initializing AI Agent...")
    
    # Initialize Vector Store (connects to existing persistent DB)
    store = VectorStore()
    store.create_collection() # Just gets the existing collection
    
    # Create the Agent
    ai_agent = create_agent(store)
    print("✅ AI Agent Ready!")
    
    yield
    # --- SHUTDOWN ---
    print("🛑 Shutting down AI Agent...")

app = FastAPI(lifespan=lifespan)
```

---

## 3. Usage in Endpoints

The agent exposes a single `chat()` method that handles decision making, retrieval, generation, and memory updates.

### Method Signature

```python
def chat(
    message: str, 
    session_id: str, 
    conversation_history: Optional[List[Dict]] = None
) -> Dict
```

### Example API Endpoint

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    global ai_agent
    
    # 1. Retrieve history from your DB (Redis/Postgres)
    # The agent expects a list of dicts: [{"role": "user", "content": "..."}, ...]
    # For now, you can pass None if you want the Agent's internal memory to handle it temporarily,
    # BUT for scalability, pass the history you store.
    
    # Example:
    # history = db.get_history(request.session_id) 
    
    # 2. Call the AI Agent
    # This is currently synchronous (blocking). If high load is expected, run in threadpool.
    result = ai_agent.chat(
        message=request.message,
        session_id=request.session_id,
        conversation_history=None # Or pass 'history' variable
    )
    
    # 3. 'result' dictionary structure:
    # {
    #     "session_id": "...",
    #     "response": "The answer text...",
    #     "sources": [
    #         {"document": "Tax Act.pdf", "score": 0.55, "excerpt": "..."},
    #         ...
    #     ],
    #     "retrieved": True/False,
    #     "timestamp": "..."
    # }
    
    # 4. Save the new turn to your DB (if you are managing persistence)
    # db.save_turn(request.session_id, request.message, result["response"])
    
    return result
```

---

## 4. Key Notes

*   **Memory:** The agent has an internal `ConversationMemory` class (`ai_engine/memory.py`). However, for a production FastAPI app, you should likely persist conversation history in your database (PostgreSQL/Redis) and pass it to `agent.chat()`.
*   **Vector DB:** The agent looks for the ChromaDB at `./chroma_db`. Ensure the backend process has **read/write access** to this folder.
*   **Async Handling:** The `agent.chat()` method is currently blocking (synchronous). For best performance in FastAPI, consider running it in a `run_in_threadpool` or updating the agent to be async in the future (Phase 2).
*   **Data Ingestion:** If you need to re-ingest documents, run the following commands:

```bash
python ai_engine/document_processor.py
python ai_engine/vector_store.py
```

*Let me know if you run into any import errors!*
