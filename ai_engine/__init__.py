# ai_engine/__init__.py
"""
AI Engine for Nigeria Tax Reform Bills Q&A Assistant
"""

from .config import config
from .agent import TaxQAAgent, create_agent
from .memory import ConversationMemory, shared_memory
from .vector_store import VectorStore

__version__ = "1.0.0"
__all__ = [
    "config",
    "TaxQAAgent",
    "create_agent",
    "ConversationMemory",
    "shared_memory",
    "VectorStore",
]
