"""
config.py
Configuration and environment setup for AI Engine
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass
class Config:
    """Central configuration for AI Engine"""
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Model Configuration
    LLM_MODEL: str = "gemini-2.0-flash-exp"
    EMBEDDING_MODEL: str = "text-embedding-004"
    
    # Generation Parameters
    TEMPERATURE: float = 0.1  # Low for factual accuracy
    MAX_TOKENS: int = 2048
    TOP_P: float = 0.95
    TOP_K: int = 40
    
    # Retrieval Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.35 # Revised from 0.7
    
    # Memory Configuration
    MAX_CONVERSATION_HISTORY: int = 5  # Last 5 Q&A pairs
    SESSION_TIMEOUT: int = 3600  # 1 hour in seconds
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = "./chroma_db"
    COLLECTION_NAME: str = "tax_reform_bills"
    
    # Document Processing
    SUPPORTED_FORMATS: list = None
    DOCS_DIRECTORY: str = "./documents"
    
    # Performance
    USE_ASYNC: bool = True
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "ai_engine.log"
    
    def __post_init__(self):
        if self.SUPPORTED_FORMATS is None:
            self.SUPPORTED_FORMATS = ['.pdf', '.txt', '.md', '.docx']
        
        # Validate API key
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found! "
                "Set it in your environment or .env file"
            )
        
        # Create necessary directories
        Path(self.VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.DOCS_DIRECTORY).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", ""),
            LLM_MODEL=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
            EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "text-embedding-004"),
            TEMPERATURE=float(os.getenv("TEMPERATURE", "0.1")),
            CHUNK_SIZE=int(os.getenv("CHUNK_SIZE", "1000")),
            VECTOR_STORE_PATH=os.getenv("VECTOR_STORE_PATH", "./chroma_db"),
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        checks = [
            (self.GEMINI_API_KEY, "API key is required"),
            (0 <= self.TEMPERATURE <= 1, "Temperature must be between 0 and 1"),
            (self.CHUNK_SIZE > 0, "Chunk size must be positive"),
            (self.MAX_CONVERSATION_HISTORY > 0, "History size must be positive"),
        ]
        
        for check, error_msg in checks:
            if not check:
                raise ValueError(f"Configuration error: {error_msg}")
        
        return True


# Singleton instance
config = Config.from_env()

# System prompts
SYSTEM_PROMPTS = {
    "main": """You are an AI assistant specializing in Nigeria's 2024 Tax Reform Bills.

Your role:
- Answer questions about the tax reform bills accurately
- Cite sources from the official documents
- Explain complex tax concepts in simple Nigerian English not Pidgin
- Correct misinformation with factual information

Guidelines:
- ALWAYS cite sources when answering policy questions
- Use format: [Source: Nigeria Tax Bill 2024, Section X]
- If you don't know, say so - don't make up information
- Be concise but thorough
- Use Nigerian context in explanations

Remember: People's livelihoods depend on understanding these reforms correctly.""",

    "retrieval_decision": """Analyze the user's message and decide if document retrieval is needed.

Retrieve documents when:
- User asks about tax policy, rates, laws, or regulations
- User asks "what", "how", "when", "why" about tax reforms
- User needs specific information from the bills

Do NOT retrieve when:
- User greets you (hello, hi, etc.)
- User thanks you
- User asks about your capabilities
- User's question can be answered from conversation history

Return: "RETRIEVE" or "NO_RETRIEVE" with a brief reason.""",

    "citation_extraction": """Extract and format citations from the retrieved documents.

Format each citation as:
{
    "source": "Nigeria Tax Bill 2024",
    "section": "Section X",
    "text": "relevant excerpt (max 200 chars)",
    "page": "page number if available"
}

Ensure citations are accurate and relevant to the answer."""
}

print("✅ Configuration loaded successfully!")
print(f"📊 Model: {config.LLM_MODEL}")
print(f"🗂️ Vector Store: {config.VECTOR_STORE_PATH}")
print(f"💾 Max History: {config.MAX_CONVERSATION_HISTORY} messages")