"""Hours per F&O line: keyboard, measured, registered, weighted -- the dashboard's own numbers.

    python ops/bin/hours.py                    this ISO week, a table per project
    python ops/bin/hours.py last|month|YYYY-MM-DD [YYYY-MM-DD]
    python ops/bin/hours.py ... --days         a table per day and project
    python ops/bin/hours.py ... --json         the lines as JSON (the hours-chart mod reads this)

One source for every view of time: the Time page's week data (dashboard.collect_audit), which
joins the finalized timesheet, the heartbeat measurement and the value records, and applies the
corrections /log makes (measure-moves.md, session splits, dimension changes). Reading the raw
value files instead showed moved lines as 0 keyboard / 0 weighted (2026-10-04, Carl Ras 10-01).

Columns: keyboard = typing time (evidence); measured = the 15+5 model; registered = the
timesheet hours (claimed, what F&O gets before the entry figure); weighted = value time, the
ceiling. The F&O entry figure lies between registered and weighted and is computed only on the
dashboard's entry page. `shared` = the line's measurement is a share of its project's day.

Pure stdlib + ops/dashboard.py. Reads only.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import dashboard  # noqa: E402

FIELDS = ("keyboard", "measured", "claimed", "weighted")


def period(args, today):
    d = datetime.date.fromisoformat(today)
    if args and args[0] == "last":
        mon = d - datetime.timedelta(days=d.weekday() + 7)
        return mon.isoformat(), (mon + datetime.timedelta(days=6)).isoformat()
    if args and args[0] == "month":
        return today[:8] + "01", today
    iso = [a for a in args if len(a) == 10 and a[4] == "-"]
    if len(iso) == 2:
        return iso[0], iso[1]
    if len(iso) == 1:
        return iso[0], iso[0]
    mon = d - datetime.timedelta(days=d.weekday())
    return mon.isoformat(), today


def lines(start, end, today):
    audit = dashboard.collect_audit(today)
    out = []
    for wk in audit["weeks"]:
        for l in audit["byWeek"][wk]["lines"]:
            if start <= l["date"] <= end:
                out.append({"date": l["date"], "project": l["project"],
                            "activity": l.get("activity") or "", "task": l.get("fno_task") or "",
                            "keyboard": round(l.get("keyboard") or 0.0, 2),
                            "measured": round(l.get("measured") or 0.0, 2),
                            "claimed": round(l.get("claimed") or 0.0, 2),
                            "weighted": round(l.get("weighted") or 0.0, 2),
                            "shared": bool(l.get("shared")), "billable": bool(l.get("billable")),
                            "live": bool(l.get("live"))})
    return sorted(out, key=lambda x: (x["date"], x["project"], x["task"]))


def table(rows, key):
    agg = {}
    for r in rows:
        k = key(r)
        a = agg.setdefault(k, dict.fromkeys(FIELDS, 0.0))
        for f in FIELDS:
            a[f] += r[f]
    out = ["| %s | Keyboard h | Measured h | Registered h | Weighted h | Weighted / registered |"
           % ("Day | Project" if key(rows[0]).count("|") else "Project"),
           "|---|---|---|---|---|---|" + ("---|" if key(rows[0]).count("|") else "")]
    tot = dict.fromkeys(FIELDS, 0.0)
    for k in sorted(agg):
        a = agg[k]
        for f in FIELDS:
            tot[f] += a[f]
        ratio = "%d%%" % round(100 * a["weighted"] / a["claimed"]) if a["claimed"] else "-"
        out.append("| %s | %.2f | %.2f | %.2f | %.2f | %s |"
                   % (k, a["keyboard"], a["measured"], a["claimed"], a["weighted"], ratio))
    ratio = "%d%%" % round(100 * tot["weighted"] / tot["claimed"]) if tot["claimed"] else "-"
    pad = " |" if key(rows[0]).count("|") else ""
    out.append("| **Total**%s | %.2f | %.2f | %.2f | %.2f | %s |"
               % (pad, tot["keyboard"], tot["measured"], tot["claimed"], tot["weighted"], ratio))
    return "\n".join(out)


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    today = datetime.date.today().isoformat()
    start, end = period(args, today)
    rows = lines(start, end, today)
    if "--json" in flags:
        print(json.dumps({"from": start, "to": end, "lines": rows}))
        return 0
    if not rows:
        print("No time in %s .. %s." % (start, end))
        return 0
    print("Hours %s .. %s (Time page data; F&O entry figure: dashboard entry page)\n" % (start, end))
    if "--days" in flags:
        print(table(rows, lambda r: "%s | %s" % (r["date"], r["project"])))
    else:
        print(table(rows, lambda r: r["project"]))
    if any(r["live"] for r in rows):
        print("\nIncludes a day not finalized yet (live): its numbers move until the rollup.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
