from sqlalchemy.orm import Session
from app.db.models import Message
from datetime import datetime

def add_message(db: Session, session_id: str, role: str, content: str, metadata: dict = None):
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        metadata=metadata or {},
        timestamp=datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_recent_messages(db: Session, session_id: str, limit: int = 10):
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.timestamp.asc())
        .limit(limit)
        .all()
    )

def clear_session(db: Session, session_id: str):
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.commit()
