"""
utils.py
Helper utilities for the AI Engine
"""

import logging
from datetime import datetime
from typing import Dict, List


def setup_logger(name: str, log_file: str = "ai_engine.log", level: str = "INFO"):
    """Configure logger for the application"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    fh = logging.FileHandler(log_file)
    fh.setLevel(getattr(logging, level.upper()))
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    text = " ".join(text.split())
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    return text.strip()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    if not session_id or not isinstance(session_id, str):
        return False
    if len(session_id) < 3 or len(session_id) > 100:
        return False
    return True


def validate_message(message: str) -> bool:
    """Validate user message"""
    if not message or not isinstance(message, str):
        return False
    if len(message.strip()) == 0:
        return False
    if len(message) > 5000:
        return False
    return True


def format_source_citation(source: Dict) -> str:
    """Format source citation for display"""
    doc = source.get('document', 'Unknown')
    section = source.get('section', '')
    
    if section:
        return f"[Source: {doc}, {section}]"
    return f"[Source: {doc}]"


class Timer:
    """Simple timer for performance monitoring"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = datetime.now()
    
    def stop(self):
        self.end_time = datetime.now()
    
    def elapsed(self) -> float:
        if not self.start_time or not self.end_time:
            return 0.0
        delta = self.end_time - self.start_time
        return delta.total_seconds()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()


ERROR_MESSAGES = {
    'invalid_session': "Invalid session ID format",
    'invalid_message': "Invalid message format",
    'api_error': "Error communicating with AI service",
    'retrieval_error': "Error retrieving documents",
    'generation_error': "Error generating response",
    'empty_message': "Message cannot be empty",
    'rate_limit': "Rate limit exceeded. Please try again later",
}


def get_error_message(error_key: str, default: str = "An error occurred") -> str:
    """Get user-friendly error message"""
    return ERROR_MESSAGES.get(error_key, default)