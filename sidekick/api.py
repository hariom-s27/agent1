from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .engine import Engine
from .schemas import Signal, SignalType

engine = Engine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine.start_scheduler()
    yield
    engine.stop_scheduler()


app = FastAPI(title="Sidekick", lifespan=lifespan)

@app.get("/notifications")
def notifications():
    """What the agent has done (newest first)."""
    return [a.model_dump(mode="json") for a in engine.notifications]


@app.get("/memories")
def memories():
    """Everything the agent remembers, by scope."""
    return engine.memory.dump()

@app.post("/tick")
def run_tick():
    """Run one proactive cycle on demand (the 'Run a cycle' button)."""
    actions = engine.tick()
    return {"ran": True, "produced": len(actions),
            "actions": [a.model_dump(mode="json") for a in actions]}


class InjectBody(BaseModel):
    type: SignalType = SignalType.task
    title: str
    body: str = ""


@app.post("/signals")
def inject(body: InjectBody):
    """Add a custom signal, then it's processed on the next tick."""
    sig = Signal(id=f"manual-{len(engine.notifications)}",
                 type=body.type, title=body.title, body=body.body)
    engine.inject_signal(sig)
    return {"queued": True, "tip": "POST /tick to process now."}


@app.post("/notifications/{idx}/{decision}")
def respond(idx: int, decision: str):
    """Approve/dismiss a notification — this feedback becomes memory."""
    if 0 <= idx < len(engine.notifications):
        a = engine.notifications[idx]
        a.status = "approved" if decision == "approve" else "dismissed"
        verb = "approved" if a.status == "approved" else "dismissed"
        engine.memory.add_episode(f"user {verb} a {a.kind} for {a.signal_id}",
                                  meta={"feedback": a.status})
        if a.status == "dismissed":
            engine.memory.add_fact(f"User tends to dismiss {a.kind} like '{a.summary}'.")
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Serve the dashboard web page."""
    return (Path(__file__).parent / "static" / "index.html").read_text()