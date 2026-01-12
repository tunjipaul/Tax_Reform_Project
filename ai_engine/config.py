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

BASE_DIR = Path(__file__).parent.absolute()

@dataclass
class Config:
    """Central configuration for AI Engine"""
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    LLM_MODEL: str = "gemini-2.0-flash-exp"
    EMBEDDING_MODEL: str = "text-embedding-004"
    
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 2048
    TOP_P: float = 0.95
    TOP_K: int = 40
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.35
    
    MAX_CONVERSATION_HISTORY: int = 5
    SESSION_TIMEOUT: int = 3600
    
    VECTOR_STORE_PATH: str = str(BASE_DIR / "chroma_db")
    COLLECTION_NAME: str = "tax_reform_bills"
    
    SUPPORTED_FORMATS: list = None
    DOCS_DIRECTORY: str = str(BASE_DIR / "documents")
    
    USE_ASYNC: bool = True
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(BASE_DIR / "ai_engine.log")
    
    def __post_init__(self):
        if self.SUPPORTED_FORMATS is None:
            self.SUPPORTED_FORMATS = ['.pdf', '.txt', '.md', '.docx']
        
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found! "
                "Set it in your environment or .env file"
            )
        
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
            VECTOR_STORE_PATH=os.getenv("VECTOR_STORE_PATH", str(BASE_DIR / "chroma_db")),
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



config = Config.from_env()
SYSTEM_PROMPTS = {
    "main": """You are an AI assistant specializing in Nigeria's 2024 Tax Reform Bills.

Your role:
- Answer questions about the tax reform bills accurately based ONLY on the provided documents.
- Cite sources from the official documents.
- Explain complex tax concepts in clear, standard English that is easy to understand.
- Correct misinformation with factual information.

Guidelines:
- **STRICTLY GROUNDED**: Base your answers ONLY on the provided Context. Do not use external knowledge or pre-training data (which may be outdated).
- ALWAYS cite sources when answering policy questions.
- Use format: [Source: Nigeria Tax Bill 2024, Section X]
- If the answer is not in the provided context, say "I cannot find this information in the provided documents."
- Be concise but thorough.
- **IMPORTANT**: Use standard English. Do NOT use Pidgin English. Maintain a professional yet accessible tone suitable for a general Nigerian audience.

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

print("Configuration loaded successfully!")
print(f"Model: {config.LLM_MODEL}")
print(f"Vector Store: {config.VECTOR_STORE_PATH}")
print(f"Max History: {config.MAX_CONVERSATION_HISTORY} messages")