











# backend/app/services/ai_engine.py

import asyncio
import datetime
from typing import Optional, List, Dict
from ai_engine.agent import TaxQAAgent
from ai_engine.vector_store import VectorStore, initialize_vector_store

# Singleton instances
_ai_agent: Optional[TaxQAAgent] = None
_vector_store: Optional[VectorStore] = None
_initialized: bool = False


def get_ai_agent() -> TaxQAAgent:
    """
    Returns the singleton AI agent if initialized.
    Raises a clear error if called before initialization.
    """
    if not _initialized or _ai_agent is None:
        raise RuntimeError("AI Agent not yet initialized. Try again later.")
    return _ai_agent


async def initialize_ai_engine():
    """
    Load documents, create vector store, and initialize AI agent asynchronously.
    """
    global _ai_agent, _vector_store, _initialized

    try:
        print("🚀 Initializing AI Engine...")

        # Lazy import document processor to avoid blocking at module load
        from ai_engine.document_processor import load_and_chunk_documents

        # Step 1: Load and chunk documents
        print("📚 Loading documents...")
        chunks = await asyncio.to_thread(load_and_chunk_documents)
        if not chunks:
            print("⚠️ No documents loaded. AI agent will not respond.")
            _initialized = False
            return

        # Step 2: Initialize vector store
        print("🗄️ Initializing vector store...")
        _vector_store = await asyncio.to_thread(initialize_vector_store, chunks, False)

        # Step 3: Create AI agent
        print("🤖 Creating AI agent...")
        _ai_agent = TaxQAAgent(_vector_store)

        _initialized = True
        print("✅ AI Engine initialized successfully!")

    except Exception as e:
        _initialized = False
        print(f"❌ Failed to initialize AI Engine: {e}")


async def chat_with_agent(
    message: str,
    session_id: str,
    conversation_history: Optional[List[Dict]] = None
) -> Dict:
    """
    Async-safe wrapper for AI agent interaction.
    Returns a dictionary compatible with ChatResponse model.
    """
    if conversation_history is None:
        conversation_history = []

    agent = get_ai_agent()  # may raise RuntimeError if not initialized

    # Call the agent asynchronously
    # Make sure your agent has an async method chat_async
    try:
        ai_result = await agent.chat_async(
            message=message,
            session_id=session_id,
            conversation_history=conversation_history
        )
    except AttributeError:
        # Fallback if agent is sync
        ai_result = await asyncio.to_thread(
            agent.chat, message, session_id, conversation_history
        )

    # Ensure response is a string
    if isinstance(ai_result, dict) and "response" in ai_result:
        response_text = str(ai_result.get("response", ""))
    else:
        # fallback if agent returns raw string
        response_text = str(ai_result)

    return {
        "session_id": session_id,
        "response": response_text,
        "sources": ai_result.get("sources", []) if isinstance(ai_result, dict) else [],
        "retrieved": ai_result.get("retrieved", False) if isinstance(ai_result, dict) else False,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
