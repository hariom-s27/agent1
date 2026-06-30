from __future__ import annotations
from .schemas import Signal, ProactiveAction, MemoryRecord
from .llm import complete
from .config import get_settings


def _context_block(facts: list[MemoryRecord], rules: list[MemoryRecord]) -> str:
    """Turn remembered facts + rules into a text block we paste into prompts."""
    f = "\n".join(f"- {m.text}" for m in facts) or "- (none yet)"
    r = "\n".join(f"- {m.text}" for m in rules) or "- (none yet)"
    return f"What I know about the user:\n{f}\n\nRules the user has taught me:\n{r}"

def draft_meeting_prep(sig: Signal, facts, rules) -> ProactiveAction:
    """Draft meeting prep, shaped by what we remember about the user."""
    system = ("You are a proactive assistant. Draft concise meeting prep: "
              "3 likely agenda bullets and 1 thing the user should decide. "
              + _context_block(facts, rules))
    body = complete(system, sig.as_prompt(), model=get_settings().act_model, max_tokens=400)
    return ProactiveAction(signal_id=sig.id, kind="meeting_prep",
                           summary=f"Prepped: {sig.title}", body=body)


def draft_email_reply(sig: Signal, facts, rules) -> ProactiveAction:
    """Draft an email reply in the user's known style."""
    system = ("You are a proactive assistant. Draft a reply the user can send as-is. "
              "Match the user's known tone preferences. "
              + _context_block(facts, rules))
    body = complete(system, sig.as_prompt(), model=get_settings().act_model, max_tokens=400)
    return ProactiveAction(signal_id=sig.id, kind="email_reply",
                           summary=f"Drafted reply: {sig.title}", body=body)


def make_reminder(sig: Signal, facts, rules) -> ProactiveAction:
    """A simple reminder — no AI needed, just formatting."""
    body = f"Reminder: '{sig.title}' is overdue. {sig.body}"
    return ProactiveAction(signal_id=sig.id, kind="reminder",
                           summary=f"Reminder: {sig.title}", body=body)


TOOLS = {
    "meeting_prep": draft_meeting_prep,
    "email_reply": draft_email_reply,
    "reminder": make_reminder,
}



