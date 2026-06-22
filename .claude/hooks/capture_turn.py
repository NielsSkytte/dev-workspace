#!/usr/bin/env python
"""Stop hook: append one raw memory record per turn to ops/memory/daily/<date>.md.

Robust by design: reads the hook JSON from stdin, extracts the last user+assistant
exchange from the transcript, writes a record in the workspace record shape, and ALWAYS
exits 0 (never blocks or errors a turn). Summarizes via Haiku only if ANTHROPIC_API_KEY is
set; otherwise falls back to a deterministic truncated extract so capture always succeeds.
See C:\\Dev\\ops\\memory\\README.md for the model and record shape.
"""
import sys, os, json, datetime

DAILY_DIR = os.environ.get("MEMORY_DAILY_DIR", r"C:\Dev\ops\memory\daily")
HAIKU_MODEL = "claude-haiku-4-5-20251001"


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


def summarize(user_text, asst_text):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not (user_text or asst_text):
        return ""
    try:
        import urllib.request
        prompt = (
            "Summarize this assistant turn in 1-2 sentences for a memory log. "
            "Capture the concrete action, decision, or fact - not pleasantries.\n\n"
            "User: %s\n\nAssistant: %s" % (user_text[:2000], asst_text[:4000])
        )
        body = json.dumps({
            "model": HAIKU_MODEL,
            "max_tokens": 160,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return "".join(
            b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
        ).strip()
    except Exception:
        return ""


def trunc(s, n):
    s = (s or "").strip().replace("\r", " ")
    return (s[:n] + "...") if len(s) > n else s


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
    )

    try:
        os.makedirs(DAILY_DIR, exist_ok=True)
        path = os.path.join(DAILY_DIR, date + ".md")
        new = not os.path.exists(path)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            if new:
                f.write(
                    "# Daily memory stream - %s\n\n"
                    "Raw per-turn records (STORAGE tier 1), written by the Stop hook. "
                    "Distilled into store/ by /log. See ../README.md.\n\n---\n\n" % date
                )
            f.write(rec)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
