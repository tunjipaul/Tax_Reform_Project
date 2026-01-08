from db.database import SessionLocal
from db.models import Message

db = SessionLocal()

# Add a test message
msg = Message(session_id="test123", role="user", content="Hello, AI!")
db.add(msg)
db.commit()

# Query it back
msgs = db.query(Message).filter_by(session_id="test123").all()
for m in msgs:
    print(m.role, m.content)

db.close()
