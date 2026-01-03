from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    role = Column(String(20))  # 'user' or 'assistant'
    content = Column(String(5000))
    extra_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
