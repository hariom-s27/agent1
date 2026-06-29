from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


def now() -> datetime:
    return datetime.now(timezone.utc)

class SignalType(str, Enum):
    calendar = "calendar"
    email = "email"
    task = "task"


class Signal(BaseModel):
    """Something happening in the user's world that the agent might act on."""
    id: str
    type: SignalType
    title: str
    body: str = ""
    ts: datetime = Field(default_factory=now)
    meta: dict = Field(default_factory=dict)

    def as_prompt(self) -> str:
        return f"[{self.type.value}] {self.title}\n{self.body}".strip()
    

class Decision(BaseModel):
    """Triage output for one signal: act or not, and which tool."""
    signal_id: str
    act: bool
    kind: str = ""          # meeting_prep | email_reply | reminder | ""
    reason: str = ""


class ProactiveAction(BaseModel):
    """A completed (or drafted) action the agent took on its own."""
    signal_id: str
    kind: str
    summary: str            # one line shown in the notification
    body: str               # the actual draft / prep / reminder text
    status: str = "proposed"  # proposed | approved | dismissed
    ts: datetime = Field(default_factory=now)


class MemoryRecord(BaseModel):
    """One item stored in the memory layer."""
    id: str
    scope: str              # episodic | semantic | procedural
    text: str
    ts: datetime
    meta: dict = Field(default_factory=dict)
