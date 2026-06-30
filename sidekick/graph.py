from __future__ import annotations
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from .schemas import Signal, Decision, ProactiveAction
from .memory import MemoryStore
from .llm import complete_json
from .tools import TOOLS
from .config import get_settings


class AgentState(TypedDict):
    signals: list[Signal]
    facts: list
    rules: list
    decisions: list[Decision]
    actions: list[ProactiveAction]
    notifications: list[str]


def build_graph(memory: MemoryStore):
    cfg = get_settings()

    def load_context(state: AgentState) -> dict:
        query = "\n".join(s.as_prompt() for s in state["signals"])
        facts = memory.search_facts(query, k=6)
        rules = memory.all_rules()
        return {"facts": facts, "rules": rules}
    
    def triage(state: AgentState) -> dict:
        rules_txt = "\n".join(f"- {r.text}" for r in state["rules"]) or "- (none)"
        signals_txt = "\n\n".join(
            f"id={s.id} type={s.type.value}\n{s.as_prompt()}" for s in state["signals"]
        )
        system = (
            "You triage incoming signals for a proactive assistant. For each signal decide "
            "whether it is worth acting on RIGHT NOW without being asked, and which tool to use.\n"
            "Match the tool to the signal TYPE:\n"
            "  - a calendar/meeting signal -> kind = meeting_prep\n"
            "  - an email signal -> kind = email_reply\n"
            "  - a task signal -> kind = reminder\n"
            "Be conservative — only act when genuinely useful, to avoid notification spam.\n\n"
            f"Rules the user has taught you:\n{rules_txt}\n\n"
            'Respond as JSON: [{"signal_id": "...", "act": true/false, '
            '"kind": "meeting_prep|email_reply|reminder|", "reason": "..."}]'
        )
        raw = complete_json(system, signals_txt, model=cfg.triage_model,max_tokens=2048, fallback=[])
        decisions = [Decision(**d) for d in raw]
        return {"decisions": decisions}
    
    def act(state: AgentState) -> dict:
        by_id = {s.id: s for s in state["signals"]}
        actions, notes = [], []
        for d in state["decisions"]:
            if not d.act or d.kind not in TOOLS:
                continue
            sig = by_id.get(d.signal_id)
            if not sig:
                continue
            action = TOOLS[d.kind](sig, state["facts"], state["rules"])
            actions.append(action)
            notes.append(action.summary)
        return {"actions": actions, "notifications": notes}

    def reflect(state: AgentState) -> dict:
        for a in state.get("actions", []):
            memory.add_episode(f"{a.kind}: {a.summary}", meta={"signal_id": a.signal_id})

        if state.get("actions"):
            system = (
                "From this assistant activity, extract (a) durable FACTS about the user worth "
                "remembering long-term, and (b) reusable behavioral RULES. Only include things that "
                "generalize beyond today. Empty lists are fine.\n"
                'Respond as JSON: {"facts": ["..."], "rules": ["..."]}'
            )
            user = "\n".join(f"{a.kind} | {a.summary}\n{a.body}" for a in state["actions"])
            try:
                extracted = complete_json(system, user, model=cfg.triage_model,
                                         max_tokens=2048, fallback={"facts": [], "rules": []})
                for f in extracted.get("facts", []):
                    memory.add_fact(f)
                for r in extracted.get("rules", []):
                    memory.add_rule(r)
            except Exception:
                pass
        return {}
    
    def route_after_triage(state: AgentState) -> str:
        return "act" if any(d.act for d in state["decisions"]) else "reflect"

    g = StateGraph(AgentState)
    g.add_node("load_context", load_context)
    g.add_node("triage", triage)
    g.add_node("act", act)
    g.add_node("reflect", reflect)

    g.add_edge(START, "load_context")
    g.add_edge("load_context", "triage")
    g.add_conditional_edges("triage", route_after_triage, {"act": "act", "reflect": "reflect"})
    g.add_edge("act", "reflect")
    g.add_edge("reflect", END)

    return g.compile(checkpointer=InMemorySaver())



