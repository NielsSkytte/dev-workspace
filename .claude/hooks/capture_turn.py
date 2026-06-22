#!/usr/bin/env python
"""Stop hook: append one raw memory record per turn to ops/memory/daily/<date>.md.

Robust by design: reads the hook JSON from stdin, extracts the last user+assistant
exchange from the transcript, writes a record in the workspace record shape, and ALWAYS
exits 0 (never blocks or errors a turn). Summarizes via a tiny local Ollama model; if Ollama
is unreachable it falls back to a deterministic truncated extract so capture always succeeds.
See C:\\Dev\\ops\\memory\\README.md for the model and record shape.
"""
import sys, os, json, datetime, hashlib

DAILY_DIR = os.environ.get("MEMORY_DAILY_DIR", r"C:\Dev\ops\memory\daily")
STATE_FILE = os.environ.get(
    "MEMORY_STATE_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".capture_state.json"),
)
# Summarizer: a tiny local Ollama model (zero cost, fully local). If Ollama is unreachable
# the caller falls back to a deterministic truncated extract.
SUMMARY_URL = os.environ.get("MEMORY_SUMMARY_URL", "http://localhost:11434/api/chat")
SUMMARY_MODEL = os.environ.get("MEMORY_SUMMARY_MODEL", "qwen3:1.7b")
SUMMARY_TIMEOUT = int(os.environ.get("MEMORY_SUMMARY_TIMEOUT", "20"))


def scope_from_cwd(cwd):
    c = (cwd or "").replace("\\", "/")
    low = c.lower()
    for bucket in ("/customers/", "/own/"):
        i = low.find(bucket)
        if i != -1:
            rest = c[i + 1:].split("/")
            # customers/<client>/<project> or own/<project>
            if rest[0].lower() == "customers" and len(rest) >= 3:
                return "project:customers/%s/%s" % (rest[1], rest[2])
            if rest[0].lower() == "own" and len(rest) >= 2:
                return "project:own/%s" % rest[1]
    return "workspace"


def extract_turn(transcript_path):
    user_text, asst_text = "", ""
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                msg = obj.get("message") or obj
                role = msg.get("role") or obj.get("type")
                content = msg.get("content")
                text = ""
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    parts = []
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "text":
                            parts.append(b.get("text", ""))
                        elif isinstance(b, str):
                            parts.append(b)
                    text = "\n".join(p for p in parts if p)
                if not text.strip():
                    continue
                if role == "user":
                    user_text = text
                elif role == "assistant":
                    asst_text = text
    except Exception:
        pass
    return user_text, asst_text


PROMPT_TMPL = (
    "Summarize this assistant turn in 1-2 sentences for a memory log. Capture the concrete "
    "action, decision, or fact - not pleasantries. Reply with only the summary.\n\n"
    "User: %s\n\nAssistant: %s"
)


def _post_json(url, body, headers, timeout):
    import urllib.request
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _summarize_local(prompt):
    """Ollama /api/chat - zero cost, fully local. Empty string on any failure (caller truncates)."""
    try:
        data = _post_json(
            SUMMARY_URL,
            {
                "model": SUMMARY_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "think": False,  # don't let a thinking model spend its budget before the answer
                "options": {"num_predict": 160, "temperature": 0.2},
            },
            {"content-type": "application/json"},
            SUMMARY_TIMEOUT,
        )
        return ((data.get("message") or {}).get("content") or "").strip()
    except Exception:
        return ""


def summarize(user_text, asst_text):
    """Local Ollama summary, or "" so the caller truncates."""
    if not (user_text or asst_text):
        return ""
    prompt = PROMPT_TMPL % (user_text[:2000], asst_text[:4000])
    return _summarize_local(prompt)


def trunc(s, n):
    s = (s or "").strip().replace("\r", " ")
    return (s[:n] + "...") if len(s) > n else s


def _hash(s):
    return hashlib.sha1((s or "").encode("utf-8")).hexdigest()


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


def header_bytes(date):
    return (
        "# Daily memory stream - %s\n\n"
        "Raw per-turn records (STORAGE tier 1), written by the Stop hook. "
        "Distilled into store/ by /log. See ../README.md.\n\n---\n\n" % date
    ).encode("utf-8")


def main():
    raw = sys.stdin.read()
    try:
        hook = json.loads(raw)
    except Exception:
        hook = {}
    if hook.get("stop_hook_active"):
        return  # avoid loops
    sid = str(hook.get("session_id", "unknown"))
    cwd = hook.get("cwd", "")
    user_text, asst_text = extract_turn(hook.get("transcript_path", ""))

    now = datetime.datetime.now(datetime.timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    date = now.strftime("%Y-%m-%d")
    rid = now.strftime("%Y%m%dT%H%M%SZ") + "-" + sid[:8]
    scope = scope_from_cwd(cwd)

    # One record per user turn: a turn is keyed by (date, session, user message). The Stop
    # hook can fire several times within one turn (the agent yields, then continues) - those
    # share the same user message, so we REPLACE the prior record in place rather than append.
    user_h, asst_h = _hash(user_text), _hash(asst_text)
    state = load_state()
    same_turn = (
        state.get("date") == date
        and state.get("session") == sid
        and state.get("user_hash") == user_h
    )
    if same_turn and state.get("asst_hash") == asst_h:
        return  # duplicate Stop, assistant unchanged - nothing new to record

    summary = summarize(user_text, asst_text)
    body_user = trunc(user_text, 500)
    body_asst = summary if summary else trunc(asst_text, 700)
    if not (body_user or body_asst):
        body_asst = "(turn captured; no text extracted from transcript)"

    rec = (
        "---\n"
        "id: %s\n" % rid +
        "ts: %s\n" % ts +
        "type: episodic\n"
        "scope: %s\n" % scope +
        "source: turn-hook\n"
        "tags: [turn]\n"
        "status: raw\n"
        "---\n\n"
        "**User:** %s\n\n" % body_user +
        "**Assistant:** %s\n\n" % body_asst +
        "---\n\n"
    ).encode("utf-8")

    try:
        os.makedirs(DAILY_DIR, exist_ok=True)
        path = os.path.join(DAILY_DIR, date + ".md")
        existing = b""
        if os.path.exists(path):
            with open(path, "rb") as f:
                existing = f.read()
        offset = state.get("offset", 0)
        if same_turn and existing and 0 <= offset <= len(existing):
            base = existing[:offset]   # same turn: drop the prior record, keep everything before
        elif existing:
            base = existing            # new turn: append to today's stream
        else:
            base = header_bytes(date)  # first record of the day
        record_start = len(base)
        with open(path, "wb") as f:    # binary write preserves the explicit "\n" line endings
            f.write(base + rec)
        save_state({
            "date": date, "session": sid,
            "user_hash": user_h, "asst_hash": asst_h, "offset": record_start,
        })
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
