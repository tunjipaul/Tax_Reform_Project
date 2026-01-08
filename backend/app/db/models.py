


from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # Session identifier
    session_id = Column(String(100), index=True, nullable=False)

    # Role: user or assistant
    role = Column(String(20), nullable=False)

    # Main message text (short or summarized)
    content = Column(String(5000), nullable=False)

    # Extra data like sources, retrieved flag, timestamp, etc.
    extra_data = Column(JSON, default=dict, nullable=False)

    # Actual timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
