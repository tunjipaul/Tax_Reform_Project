





# backend/app/db/session_repo.py
from sqlalchemy.orm import Session
from app.db.models import Message
from datetime import datetime
from typing import Optional, List

def add_message(db: Session, session_id: str, role: str, content: str, metadata: Optional[dict] = None) -> Message:
    """
    Add a message to the database. Metadata is optional extra data (e.g., sources).
    """
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        extra_data=metadata or {},
        timestamp=datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_recent_messages(db: Session, session_id: str, limit: int = 10) -> List[Message]:
    """
    Fetch the most recent messages for a session.
    """
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.timestamp.asc())
        .limit(limit)
        .all()
    )

def clear_session(db: Session, session_id: str):
    """
    Remove all messages for a session.
    """
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.commit()
