# # Simple in-memory session storage
# from typing import Dict, List

# sessions: Dict[str, List[Dict]] = {}

# def get_session_history(session_id: str) -> List[Dict]:
#     return sessions.get(session_id, [])

# def add_message(session_id: str, role: str, content: str):
#     if session_id not in sessions:
#         sessions[session_id] = []
#     sessions[session_id].append({"role": role, "content": content})

# def clear_session(session_id: str):
#     if session_id in sessions:
#         sessions.pop(session_id)
