from __future__ import annotations
import json
import time
from openai import OpenAI
from json_repair import repair_json
from sidekick.config import get_settings

_client: OpenAI | None = None

def client() -> OpenAI:
    """Build the AI client once, then reuse it. Points wherever config says."""
    global _client
    if _client is None:
        s = get_settings()
        _client = OpenAI(base_url=s.llm_base_url, api_key=s.llm_api_key)
    return _client

def complete(system: str, user: str, *, model: str,
             max_tokens: int = 1024, temperature: float = 0.3) -> str:
    """Send the AI a system instruction + user message, get plain text back."""
    resp = client().chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (resp.choices[0].message.content or "").strip()

def _parse_json(raw: str):
    """Turn possibly-messy model text into real Python data, walking a repair ladder."""
    cleaned = raw.strip()

    # Rung 1: strip ```json code fences if present
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip().rstrip("`").strip()

    # Rung 2: try parsing directly
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Rung 3: slice out the first {...} or [...] block, ignoring thinking-text
    start = min((cleaned.find("{"), cleaned.find("[")), key=lambda i: (i < 0, i))
    end = max(cleaned.rfind("}"), cleaned.rfind("]"))
    if start >= 0 and end > start:
        snippet = cleaned[start:end + 1]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            cleaned = snippet  # hand the snippet to the repairer

    # Rung 4: last resort — json-repair fixes mangled syntax
    return json.loads(repair_json(cleaned))

def complete_json(system: str, user: str, *, model: str,
                  max_tokens: int = 1024, temperature: float = 0.0,
                  retries: int = 2, fallback=None):
    """Get JSON from the model. Instruct hard, parse via the ladder, retry on failure."""
    system = system + "\n\nReturn ONLY valid JSON. No prose, no markdown, no code fences."
    last_error = None
    for attempt in range(retries + 1):
        try:
            raw = complete(system, user, model=model,
                           max_tokens=max_tokens, temperature=temperature)
            return _parse_json(raw)
        except Exception as e:
            last_error = e
            time.sleep(1.5 * (attempt + 1))  # back off a bit longer each try
    if fallback is not None:
        return fallback
    raise last_error
if __name__ == "__main__":
    s = get_settings()
    print(complete("You are concise.", "Say hello in one short sentence.", model=s.triage_model))