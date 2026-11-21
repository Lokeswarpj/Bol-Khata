"""
BolKhata - Conversational Session & Context State Manager
Maintains in-memory state per active session:
- Pending disambiguation (e.g. waiting for user to specify which 'Ramesh')
- Last transaction reference for spoken corrections ('nahi, 430')
- First-turn AI disclosure tracker
"""

import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.models import ParsedIntent


class PendingAction(BaseModel):
    """An action awaiting disambiguation confirmation."""
    intent: ParsedIntent
    candidates: List[Dict[str, Any]]
    created_at: float = 0.0


class SessionState:
    """Session state for a connected client or counter."""

    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.first_turn_completed: bool = False
        self.pending_action: Optional[PendingAction] = None
        self.last_transaction_id: Optional[int] = None
        self.last_customer_id: Optional[int] = None
        self.last_customer_name: Optional[str] = None
        self.last_amount: Optional[float] = None
        self.last_direction: Optional[str] = None
        self.last_activity_time: float = time.time()

    def set_pending_action(self, intent: ParsedIntent, candidates: List[Dict[str, Any]]):
        self.pending_action = PendingAction(
            intent=intent,
            candidates=candidates,
            created_at=time.time(),
        )
        self.last_activity_time = time.time()

    def clear_pending_action(self):
        self.pending_action = None

    def record_transaction(
        self,
        txn_id: int,
        customer_id: int,
        customer_name: str,
        amount: float,
        direction: str,
    ):
        self.last_transaction_id = txn_id
        self.last_customer_id = customer_id
        self.last_customer_name = customer_name
        self.last_amount = amount
        self.last_direction = direction
        self.last_activity_time = time.time()


class SessionManager:
    """Manages active sessions across WebSocket and REST requests."""

    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id)
        session = self._sessions[session_id]
        session.last_activity_time = time.time()
        return session

    def reset_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


# Singleton instance
session_manager = SessionManager()
