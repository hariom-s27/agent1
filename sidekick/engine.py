from __future__ import annotations
import threading
from apscheduler.schedulers.background import BackgroundScheduler

from .config import get_settings
from .memory import MemoryStore
from .connectors import default_connectors, gather_signals
from .graph import build_graph
from .schemas import ProactiveAction


class Engine:
    def __init__(self):
        cfg = get_settings()
        self.memory = MemoryStore(cfg.data_dir, dedup_distance=cfg.fact_dedup_distance)
        self.connectors = default_connectors()
        self.graph = build_graph(self.memory)
        self.notifications: list[ProactiveAction] = []
        self._extra_signals = []
        self._tick_count = 0
        self._seen_signal_ids: set[str] = set()
        self._lock = threading.Lock()
        self._scheduler: BackgroundScheduler | None = None


    def inject_signal(self, signal):
        """Queue a manually-added signal (from the dashboard) for the next tick."""
        self._extra_signals.append(signal)

    def tick(self) -> list[ProactiveAction]:
        """One heartbeat: gather signals, run the graph, store results. Thread-safe + crash-safe."""
        with self._lock:                      # only one tick touches shared state at a time
            try:
                self._tick_count += 1
                signals = gather_signals(self.connectors) + self._extra_signals
                self._extra_signals = []
                if not signals:
                    return []

                result = self.graph.invoke(
                    {"signals": signals, "facts": [], "rules": [],
                     "decisions": [], "actions": [], "notifications": []},
                    config={"configurable": {"thread_id": f"tick-{self._tick_count}"}},
                )
                actions = result.get("actions", [])
                self.notifications = actions + self.notifications   # newest first
                return actions
            except Exception as e:
                print(f"[tick error] {e}")     # one bad tick must never kill the scheduler
                return []   
            

    def start_scheduler(self):
        """Start the background timer that fires tick() automatically."""
        cfg = get_settings()
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(
            self.tick, "interval", seconds=cfg.tick_seconds, id="tick",
            max_instances=1,    # never run two ticks at once
            coalesce=True,      # if ticks pile up, run only one
        )
        self._scheduler.start()

    def stop_scheduler(self):
        """Stop the timer cleanly (called on shutdown)."""
        if self._scheduler:
            self._scheduler.shutdown(wait=False)        