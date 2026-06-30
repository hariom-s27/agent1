from __future__ import annotations
from datetime import timedelta
from typing import Protocol
from .schemas import Signal, SignalType, now


class Connector(Protocol):
    """Anything that can be polled for signals. The 'plug shape' for sources."""
    def poll(self) -> list[Signal]: ...


class MockCalendar:
    """A meeting starting soon with no agenda -> a prep opportunity."""
    def poll(self) -> list[Signal]:
        start = now() + timedelta(minutes=25)
        return [Signal(
            id="cal-roadmap-sync",
            type=SignalType.calendar,
            title="Roadmap sync with Priya (25 min away)",
            body="Attendees: you, Priya (eng lead). No agenda attached. Recurring weekly.",
            meta={"starts_at": start.isoformat(), "has_agenda": False},
        )]


class MockEmail:
    """An unread email that clearly wants a reply."""
    def poll(self) -> list[Signal]:
        return [Signal(
            id="mail-vendor-quote",
            type=SignalType.email,
            title="Re: pricing for the GPU instances",
            body=("From: vendor@acme.cloud\n"
                  "Hi — can you confirm whether you want the 4x or 8x A100 config "
                  "before Friday? Happy to lock the quarterly rate."),
            meta={"from": "vendor@acme.cloud", "unread": True},
        )]


class MockTasks:
    """A task that is overdue."""
    def poll(self) -> list[Signal]:
        return [Signal(
            id="task-blogpost",
            type=SignalType.task,
            title="Publish the launch blog post",
            body="Due yesterday. Draft exists in Notion; needs a final read.",
            meta={"overdue": True},
        )]



def default_connectors() -> list[Connector]:
    """The set of sources the agent watches."""
    return [MockCalendar(), MockEmail(), MockTasks()]


def gather_signals(connectors: list[Connector]) -> list[Signal]:
    """Poll every connector and collect all signals into one list."""
    signals: list[Signal] = []
    for c in connectors:
        signals.extend(c.poll())
    return signals        