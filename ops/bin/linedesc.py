#!/usr/bin/env python
"""Line descriptions -- prepare the material, and say what is still undescribed.

A timesheet row says `customers/Carl-Ras/datahub | 230-02 | - | - | 3.00 | yes` and nothing
about the work. This script gathers, per F&O line, the sessions behind it and what was said
in them, so a session at /log can write one sentence per line into
`ops/time/lines/<YYYY-MM>/<date>.md`.

It does NOT write the descriptions. A local model was tried for that in July and August and
switched off on 2026-09-02 for writing summaries that contradicted their turn (memory record
`local-summarizer-off`); the sentence is written by the session that closed the day, which
has the context and is already reviewing the timesheet at the same gate.

Modes:
  python ops/bin/linedesc.py 2026-09-18        the material for one date
  python ops/bin/linedesc.py 2026-W38          every date of one ISO week
  python ops/bin/linedesc.py 2026-09           every date of one month
  python ops/bin/linedesc.py --check [2026-09] what is described and what is not
  python ops/bin/linedesc.py --skeleton DATE   just the empty table, to fill in

Add `--turns N` to widen the transcript per session (default 3), `--all` to include lines
that already have a description.

Derive-only. Pure stdlib, ASCII output.
"""
import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OPS = os.path.dirname(HERE)
sys.path.insert(0, OPS)

import dashboard                                   # noqa: E402  (the collectors live there)
from lib import lines as linedesc                  # noqa: E402

rollup = dashboard.rollup


def ascii_(s):
    """The workspace convention: scripts print ASCII, because a Windows console will
    otherwise raise on a task title and the failure gets swallowed."""
    return (s or "").encode("ascii", "replace").decode("ascii")


def dates_in(span):
    """A date, an ISO week or a month -> the dates it covers, ascending."""
    if len(span) == 10:
        datetime.date.fromisoformat(span)
        return [span]
    if len(span) == 8 and span[4:6].upper() == "-W":
        return rollup.week_dates(span.upper())
    if len(span) == 7:
        first = datetime.date.fromisoformat(span + "-01")
        nxt = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        return [(first + datetime.timedelta(days=i)).isoformat()
                for i in range((nxt - first).days)]
    raise SystemExit("not a date, ISO week or month: %s" % span)


def rows_for(date):
    """The F&O lines of one date: the finalized timesheet if there is one, else the live
    tally. Same order the timesheet has them, so the two files read side by side."""
    rows = rollup.parse_daily_file(date)
    if rows is None:
        hbs = [h for h in rollup.load_heartbeats() if h["date"] == date]
        rows = rollup.rows_for(hbs) if hbs else []
    return [r for r in rows if r["hours"] > 0]


def evidence(today, turns, weeks):
    """{lineSessions key: record} with the caps widened for a backfill.

    The dashboard carries this for a hover, so it keeps it small. Describing a line wants
    more of the transcript and a longer reach, and the constants are the only difference --
    so they are set here rather than the join being written a second time."""
    dashboard.TIP_LINES = turns
    dashboard.TIP_BLOCKS = 6
    dashboard.SESSION_WEEKS = weeks
    return dashboard.collect_line_sessions(today)


def key_for(date, r):
    return ("%s|%s|%s|%s" % (date, r["project"], r["activity"] or "",
                             r["fno_task"] or "")).lower()


def sessions_for(ev, date, r):
    """(blocks, widened). The exact key is date + project + the two sub-dimensions as the
    timesheet holds them, and it misses whenever a dimension was corrected after the day was
    written -- which is exactly the line most in need of a description. A miss falls back to
    every session on that date and project, merged, and says so."""
    rec = ev.get(key_for(date, r)) or {}
    if rec.get("blocks"):
        return rec["blocks"], rec.get("more", 0), False
    prefix = ("%s|%s|" % (date, r["project"])).lower()
    merged = {}
    for k, v in ev.items():
        if not k.startswith(prefix):
            continue
        for b in v.get("blocks") or []:
            m = merged.setdefault(b["session"], {"session": b["session"], "turns": 0,
                                                 "hours": 0.0, "task": b["task"],
                                                 "lines": []})
            m["turns"] += b["turns"]
            m["hours"] = round(m["hours"] + b["hours"], 2)
            if b["task"] and not m["task"]:
                m["task"] = b["task"]
            for t in b["lines"]:
                if t not in m["lines"]:
                    m["lines"].append(t)
    blocks = sorted(merged.values(), key=lambda b: -b["hours"])
    return blocks, 0, bool(blocks)


def prepare(spans, turns, weeks, include_all):
    today = datetime.date.today().isoformat()
    ev = evidence(today, turns, weeks)
    shown = 0
    for date in spans:
        rows = rows_for(date)
        if not rows:
            continue
        have = linedesc.read_day(date)
        todo = [r for r in rows
                if include_all
                or linedesc.dimkey(r["project"], r["activity"], r["fno_task"]) not in have]
        if not todo:
            print("%s -- all %d line(s) already described" % (date, len(rows)))
            continue
        dow = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%a")
        total = sum(r["hours"] for r in rows)
        print("")
        print("=" * 78)
        print("%s (%s) -- %d line(s), %.2f h; %d to describe"
              % (date, dow, len(rows), total, len(todo)))
        print("=" * 78)
        for r in todo:
            print("")
            print("## %s | %s | %s | %.2f h"
                  % (r["project"], r["activity"] or "-", r["fno_task"] or "-", r["hours"]))
            blocks, more, wide = sessions_for(ev, date, r)
            if wide:
                print("   (no session carries this line's exact dimensions -- one of them was")
                print("    corrected after the day was written. Every session on this date and")
                print("    project follows; more than one line may share them.)")
            elif not blocks:
                print("   (no session evidence at all -- read ops/memory/daily/%s.md)" % date)
            for b in blocks:
                print("   session %s -- %.2f h, %d turn(s), task %s"
                      % (b["session"], b["hours"], b["turns"], ascii_(b["task"]) or "none"))
                for t in b["lines"]:
                    print("     - %s" % ascii_(t))
            if more:
                print("   (+%d smaller session(s) not shown)" % more)
        print("")
        print("-" * 78)
        print("Write ops/time/lines/%s/%s.md as:" % (date[:7], date))
        print("-" * 78)
        print(skeleton(date, rows, have))
        shown += 1
    if not shown:
        print("Nothing to describe.")


def skeleton(date, rows, have=None):
    have = have or {}
    out = []
    for r in rows:
        k = linedesc.dimkey(r["project"], r["activity"], r["fno_task"])
        out.append({"project": r["project"], "activity": r["activity"],
                    "fno_task": r["fno_task"], "hours": r["hours"],
                    "description": have.get(k, "")})
    return linedesc.render(date, out)


def check(month):
    dates = dates_in(month)
    days = missing_days = total = described = 0
    gaps = []
    for date in dates:
        rows = rows_for(date)
        if not rows:
            continue
        days += 1
        have = linedesc.read_day(date)
        n = sum(1 for r in rows
                if linedesc.dimkey(r["project"], r["activity"], r["fno_task"]) in have)
        total += len(rows)
        described += n
        if n < len(rows):
            gaps.append("%s (%d/%d)" % (date, n, len(rows)))
            if not n:
                missing_days += 1
    print("%s -- %d day(s) with time, %d described line(s) of %d"
          % (month, days, described, total))
    if gaps:
        print("incomplete: %s" % ", ".join(gaps))
        print("%d day(s) with nothing at all" % missing_days)
    else:
        print("every line described")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("span", nargs="?", help="YYYY-MM-DD, YYYY-Www or YYYY-MM")
    ap.add_argument("--check", nargs="?", const="", metavar="YYYY-MM",
                    help="report coverage instead of preparing material")
    ap.add_argument("--skeleton", metavar="YYYY-MM-DD", help="print the empty table only")
    ap.add_argument("--turns", type=int, default=3, help="turns per session (default 3)")
    ap.add_argument("--weeks", type=int, default=20, help="how far back to read memory")
    ap.add_argument("--all", action="store_true", help="include already-described lines")
    a = ap.parse_args()

    if a.skeleton:
        print(skeleton(a.skeleton, rows_for(a.skeleton), linedesc.read_day(a.skeleton)))
        return
    if a.check is not None:
        check(a.check or datetime.date.today().isoformat()[:7])
        return
    span = a.span or datetime.date.today().isoformat()
    prepare(dates_in(span), a.turns, a.weeks, a.all)


if __name__ == "__main__":
    main()
