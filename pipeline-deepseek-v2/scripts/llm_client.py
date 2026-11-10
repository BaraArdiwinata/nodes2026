"""Shared DeepSeek client (OpenAI-compatible) with retry + exponential backoff.

- base_url https://api.deepseek.com, model deepseek-chat, key from DEEPSEEK_API_KEY (.env)
- json_mode=True sets response_format={"type": "json_object"} (DeepSeek requires the word "json" in the prompt)
- Retries on timeouts, connection errors, HTTP 429/5xx with exponential backoff + jitter (honours Retry-After)
"""
import os, re, json, time, random
import requests
from dotenv import load_dotenv

_here = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_here, "../.env"))

BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
RETRY_STATUS = {429, 500, 502, 503, 504}

STATS = {"calls": 0, "retries": 0, "failures": 0, "tokens": 0, "latency": 0.0}


class LLMError(RuntimeError):
    pass


def chat(messages, json_mode=False, tools=None, max_tokens=1200, temperature=0.1,
         retries=4, base_delay=2.0, timeout=60):
    """Returns the raw response dict. Raises LLMError after exhausting retries or on a non-retryable error."""
    if not API_KEY:
        raise LLMError("DEEPSEEK_API_KEY is not set")
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if tools is not None:
        payload["tools"] = tools
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    last = ""
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            r = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers, timeout=timeout)
            STATS["latency"] += time.time() - t0
            if r.status_code == 200:
                j = r.json()
                STATS["calls"] += 1
                STATS["tokens"] += j.get("usage", {}).get("total_tokens", 0)
                return j
            last = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code not in RETRY_STATUS:
                STATS["failures"] += 1
                raise LLMError(last)
            delay = float(r.headers.get("Retry-After", 0) or 0)
        except (requests.Timeout, requests.ConnectionError) as e:
            last, delay = f"{type(e).__name__}: {e}", 0
        if attempt < retries:
            STATS["retries"] += 1
            time.sleep(max(delay, base_delay * (2 ** attempt)) + random.uniform(0, 0.5))
    STATS["failures"] += 1
    raise LLMError(f"gave up after {retries + 1} attempts: {last}")


def chat_json(system, user, **kw):
    """JSON-mode call; returns a parsed dict, or None if the model returned invalid JSON."""
    if "json" not in (system + user).lower():
        system += "\nRespond with a valid JSON object."
    resp = chat([{"role": "system", "content": system}, {"role": "user", "content": user}], json_mode=True, **kw)
    content = resp["choices"][0]["message"]["content"].strip()
    content = re.sub(r"^```json\s*|^```\s*|```$", "", content, flags=re.M).strip()
    try:
        out = json.loads(content)
        return out if isinstance(out, dict) else None
    except Exception:
        return None
