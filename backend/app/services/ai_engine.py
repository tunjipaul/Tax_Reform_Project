# backend/app/services/ai_engine.py

from ai_engine.agent import TaxQAAgent
from ai_engine.vector_store import VectorStore, initialize_vector_store
from ai_engine.document_processor import load_and_chunk_documents

# -------------------------------
# Step 1: Initialize Vector Store
# -------------------------------
# Load documents from configured directory
chunks = load_and_chunk_documents()  # List[DocumentChunk]

# Initialize the vector store with chunks (do not reset unless needed)
vector_store = initialize_vector_store(chunks, reset=False)

# -------------------------------
# Step 2: Singleton AI Agent
# -------------------------------
_ai_agent: TaxQAAgent | None = None

def get_ai_agent() -> TaxQAAgent:
    """
    Returns a singleton instance of TaxQAAgent
    """
    global _ai_agent
    if _ai_agent is None:
        _ai_agent = TaxQAAgent(vector_store)
        print("✅ AI Agent initialized")
    return _ai_agent
