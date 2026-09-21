"""Reading the raw heartbeat record.

`ops/time/heartbeats/<date>.jsonl` is the immutable measurement: one line per turn,
written by the time hook. Everything downstream derives from it, and nothing rewrites
it -- a correction is applied on the way out, so past days heal on any re-read.

This module does the reading and nothing else: parse the line, put the timestamps in
UTC, guarantee end >= start. It deliberately does NOT bound a span, split at local
midnight, group, or round. Those are the timesheet's rules (`time/rollup.py`) and the
value model's rules (`time/value.py`), and the two differ on purpose -- the timesheet
bounds a runaway turn because it bills clock time, the value model does not because it
scores transcript evidence. Folding either rule in here would silently change the
other consumer's numbers.

Read-only. Pure stdlib, ASCII-only.
"""
import datetime
import glob
import json
import os

__all__ = ["parse_ts", "records", "dir_for"]


def dir_for(root=None):
    """The heartbeat directory under a workspace root."""
    base = root or os.environ.get("DEV_WORKSPACE", r"C:\Dev")
    return os.path.join(base, "ops", "time", "heartbeats")


def parse_ts(s):
    """An ISO timestamp -> aware UTC datetime, or None. Never raises.

    The hook writes `2026-06-22T06:14:03Z`. A value with no zone is read as UTC rather
    than dropped, because a dropped heartbeat is unbilled work."""
    if not s:
        return None
    try:
        d = datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(datetime.timezone.utc)


def records(dirpath):
    """Every heartbeat in a directory -> [{start, end, project, task, session}].

    Files are read in name order, lines in file order. A line that will not parse is
    skipped rather than failing the read: the record is append-only and a truncated
    last line is the normal shape of a session still running.

    `project` defaults to "Dev" (the workspace itself) when the hook recorded none;
    `session` is the full session id, which callers key on by its first 8 characters."""
    out = []
    for path in sorted(glob.glob(os.path.join(dirpath, "*.jsonl"))):
        try:
            fh = open(path, encoding="utf-8")
        except Exception:
            continue
        with fh as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                start, end = parse_ts(o.get("ts_start")), parse_ts(o.get("ts_end"))
                if not start or not end:
                    continue
                if end < start:
                    end = start
                out.append({"start": start, "end": end,
                            "project": o.get("project") or "Dev",
                            "task": o.get("task"),
                            "session": o.get("session") or ""})
    return out
