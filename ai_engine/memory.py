"""
memory.py
Conversation memory management for maintaining context across messages

NOTE: This will be shared storage with ADEMS (Paul mentioned collaboration)
Design for easy integration with backend session storage
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

from config import config


class ConversationMemory:
    """
    Manage conversation history per session
    
    Features:
    - Store last N messages per session
    - Auto-prune old sessions
    - Thread-safe for FastAPI integration
    - Easy serialization for backend storage
    """
    
    def __init__(self, max_history: int = None):
        self.max_history = max_history or config.MAX_CONVERSATION_HISTORY
        self.sessions: Dict[str, List[Dict]] = defaultdict(list)
        self.session_metadata: Dict[str, Dict] = {}
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a message to session history
        
        Args:
            session_id: Unique session identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional additional data
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.sessions[session_id].append(message)
        
        # Update session metadata
        if session_id not in self.session_metadata:
            self.session_metadata[session_id] = {
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "message_count": 0
            }
        
        self.session_metadata[session_id]["last_active"] = datetime.now().isoformat()
        self.session_metadata[session_id]["message_count"] += 1
        
        # Prune if exceeds max history
        if len(self.sessions[session_id]) > self.max_history * 2:  # 2 messages per Q&A
            self._prune_session(session_id)
    
    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Max number of messages to return (most recent)
        
        Returns:
            List of messages in chronological order
        """
        history = self.sessions.get(session_id, [])
        
        if limit:
            return history[-limit:]
        
        return history
    
    def get_recent_context(
        self,
        session_id: str,
        num_turns: int = None
    ) -> str:
        """
        Get formatted recent conversation for context
        
        Args:
            session_id: Session identifier
            num_turns: Number of Q&A turns to include
        
        Returns:
            Formatted conversation string
        """
        num_turns = num_turns or self.max_history
        num_messages = num_turns * 2  # Each turn = user + assistant message
        
        history = self.get_history(session_id, limit=num_messages)
        
        if not history:
            return ""
        
        formatted = []
        for msg in history:
            role = msg["role"].title()
            content = msg["content"]
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def _prune_session(self, session_id: str):
        """Keep only the most recent messages"""
        max_messages = self.max_history * 2
        self.sessions[session_id] = self.sessions[session_id][-max_messages:]
    
    def clear_session(self, session_id: str):
        """Clear all history for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all active sessions"""
        return list(self.sessions.keys())
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get metadata about a session"""
        return self.session_metadata.get(session_id)
    
    def cleanup_old_sessions(self, hours: int = None):
        """
        Remove sessions inactive for specified hours
        
        Args:
            hours: Hours of inactivity before cleanup (default from config)
        """
        hours = hours or (config.SESSION_TIMEOUT / 3600)
        cutoff = datetime.now() - timedelta(hours=hours)
        
        sessions_to_remove = []
        
        for session_id, metadata in self.session_metadata.items():
            last_active = datetime.fromisoformat(metadata["last_active"])
            if last_active < cutoff:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.clear_session(session_id)
        
        if sessions_to_remove:
            print(f"🧹 Cleaned up {len(sessions_to_remove)} inactive sessions")
    
    # =========================================================================
    # SERIALIZATION FOR BACKEND INTEGRATION
    # =========================================================================
    
    def to_dict(self) -> Dict:
        """
        Convert memory to dictionary for backend storage
        
        Returns:
            Dict with all sessions and metadata
        """
        return {
            "sessions": dict(self.sessions),
            "metadata": self.session_metadata,
            "config": {
                "max_history": self.max_history
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationMemory':
        """
        Create ConversationMemory from dictionary
        
        Args:
            data: Dictionary from to_dict()
        
        Returns:
            ConversationMemory instance
        """
        memory = cls(max_history=data.get("config", {}).get("max_history"))
        memory.sessions = defaultdict(list, data.get("sessions", {}))
        memory.session_metadata = data.get("metadata", {})
        return memory
    
    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ConversationMemory':
        """Load from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def export_session(self, session_id: str) -> Optional[Dict]:
        """
        Export a single session for backend
        
        Args:
            session_id: Session to export
        
        Returns:
            Session data or None
        """
        if session_id not in self.sessions:
            return None
        
        return {
            "session_id": session_id,
            "messages": self.sessions[session_id],
            "metadata": self.session_metadata.get(session_id, {})
        }
    
    def import_session(self, session_data: Dict):
        """
        Import session data from backend
        
        Args:
            session_data: Session dict from export_session()
        """
        session_id = session_data["session_id"]
        self.sessions[session_id] = session_data["messages"]
        self.session_metadata[session_id] = session_data["metadata"]
    
    # =========================================================================
    # STATISTICS & MONITORING
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Get memory usage statistics"""
        total_messages = sum(len(msgs) for msgs in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "total_messages": total_messages,
            "avg_messages_per_session": total_messages / len(self.sessions) if self.sessions else 0,
            "max_history_per_session": self.max_history,
            "oldest_session": min(
                (metadata["created_at"] for metadata in self.session_metadata.values()),
                default="N/A"
            ),
            "most_recent_activity": max(
                (metadata["last_active"] for metadata in self.session_metadata.values()),
                default="N/A"
            )
        }


# =============================================================================
# SHARED MEMORY INSTANCE (for backend integration)
# =============================================================================

# This can be imported by both AI engine and backend
shared_memory = ConversationMemory()


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("🧪 Testing Conversation Memory\n")
    
    memory = ConversationMemory(max_history=3)
    
    # Simulate conversation
    session_id = "test_user_123"
    
    print("📝 Adding messages...")
    memory.add_message(session_id, "user", "Will I pay more tax?")
    memory.add_message(session_id, "assistant", "Based on the new bills...")
    
    memory.add_message(session_id, "user", "What about VAT?")
    memory.add_message(session_id, "assistant", "VAT changes include...")
    
    memory.add_message(session_id, "user", "Tell me more")
    memory.add_message(session_id, "assistant", "Regarding VAT...")
    
    # Get history
    print("\n📜 Full History:")
    history = memory.get_history(session_id)
    for msg in history:
        print(f"  {msg['role']}: {msg['content']}")
    
    # Get recent context
    print("\n🔄 Recent Context (2 turns):")
    context = memory.get_recent_context(session_id, num_turns=2)
    print(context)
    
    # Session info
    print("\n📊 Session Info:")
    info = memory.get_session_info(session_id)
    print(f"  Created: {info['created_at']}")
    print(f"  Messages: {info['message_count']}")
    
    # Stats
    print("\n📈 Memory Stats:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Export/Import
    print("\n💾 Testing Serialization...")
    exported = memory.export_session(session_id)
    print(f"  Exported {len(exported['messages'])} messages")
    
    # Create new memory and import
    new_memory = ConversationMemory()
    new_memory.import_session(exported)
    print(f"  Imported successfully!")
    
    # Verify
    imported_history = new_memory.get_history(session_id)
    assert len(imported_history) == len(history), "Import failed!"
    print("  ✅ Serialization works correctly")
    
    print("\n✅ All tests passed!")