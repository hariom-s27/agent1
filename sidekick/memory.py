from __future__ import annotations
import uuid
from pathlib import Path
import chromadb
from .schemas import MemoryRecord, now


class MemoryStore:
    """Episodic + semantic + procedural memory over a persistent Chroma database."""

    SCOPES = ("episodic", "semantic", "procedural")

    def __init__(self, path: Path, dedup_distance: float = 0.15):
        self._client = chromadb.PersistentClient(path=str(path / "chroma"))
        self._dedup = dedup_distance
        self._col = {
            s: self._client.get_or_create_collection(s, metadata={"hnsw:space": "cosine"})
            for s in self.SCOPES
        }

    # ---------- internal helper: add one item to a drawer ----------
    def _add(self, scope: str, text: str, meta: dict | None) -> str:
        rid = uuid.uuid4().hex
        meta = {**(meta or {}), "ts": now().isoformat()}
        self._col[scope].add(ids=[rid], documents=[text], metadatas=[meta])
        return rid

    # ---------- episodic: a log; duplicates are allowed ----------
    def add_episode(self, text: str, meta: dict | None = None) -> str:
        return self._add("episodic", text, meta)

    def recall_episodes(self, query: str, k: int = 5) -> list[MemoryRecord]:
        return self._search("episodic", query, k)

    # ---------- semantic: a knowledge base; deduplicated ----------
    def add_fact(self, text: str, meta: dict | None = None) -> str | None:
        if self._is_duplicate("semantic", text):
            return None
        return self._add("semantic", text, meta)

    def search_facts(self, query: str, k: int = 5) -> list[MemoryRecord]:
        return self._search("semantic", query, k)

    # ---------- procedural: learned rules; injected into prompts ----------
    def add_rule(self, text: str) -> str | None:
        if self._is_duplicate("procedural", text):
            return None
        return self._add("procedural", text, {})

    def all_rules(self) -> list[MemoryRecord]:
        got = self._col["procedural"].get()
        return [
            MemoryRecord(id=i, scope="procedural", text=d, ts=now(), meta=m or {})
            for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])
        ]

    # ---------- internal helper: search a drawer by meaning ----------
    def _search(self, scope: str, query: str, k: int) -> list[MemoryRecord]:
        col = self._col[scope]
        if col.count() == 0:
            return []
        res = col.query(query_texts=[query], n_results=min(k, col.count()))
        out = []
        for i, doc, meta in zip(res["ids"][0], res["documents"][0], res["metadatas"][0]):
            out.append(MemoryRecord(id=i, scope=scope, text=doc, ts=now(), meta=meta or {}))
        return out

    # ---------- internal helper: is this near-identical to something stored? ----------
    def _is_duplicate(self, scope: str, text: str) -> bool:
        col = self._col[scope]
        if col.count() == 0:
            return False
        res = col.query(query_texts=[text], n_results=1)
        distance = res["distances"][0][0]
        return distance < self._dedup

    # ---------- introspection for the dashboard ----------
    def dump(self) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for scope in self.SCOPES:
            got = self._col[scope].get()
            out[scope] = [
                {"id": i, "text": d, "meta": m}
                for i, d, m in zip(got["ids"], got["documents"], got["metadatas"])
            ]
        return out