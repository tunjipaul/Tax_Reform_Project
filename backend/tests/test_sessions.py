import pytest
from app.core import sessions

def test_add_and_get_session():
    session_id = "test123"
    sessions.add_message(session_id, "user", "Hello")
    history = sessions.get_session_history(session_id)
    assert len(history) == 1
    assert history[0]["content"] == "Hello"

def test_clear_session():
    session_id = "test_clear"
    sessions.add_message(session_id, "user", "Hi")
    sessions.clear_session(session_id)
    history = sessions.get_session_history(session_id)
    assert history == []
