"""The hour bank: deposits, what was drawn, what remains (ops/time/bank.md).

    python ops/bin/bank.py            open deposits
    python ops/bin/bank.py --all      every deposit, drawn ones too

Reads only. See ops/lib/bank.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import bank  # noqa: E402


def main(argv):
    rows = bank.balances()
    if "--all" not in argv:
        rows = [r for r in rows if r["remaining"] > 0.005]
    if not rows:
        print("No open deposits.")
        return 0
    print("| Id | Opened | Holding | For | Hours | Drawn | Remaining | Work h | Weighted h | Terms |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s | %s | %.2f | %.2f | %.2f | %.2f | %.2f | %s |" % (
            r["id"], r["opened"], r["holding"], ", ".join(r["for"]) or "-", r["hours"],
            r["drawn"], r["remaining"], r["work"], r["weighted"], r["terms"]))
    print("\nOpen: %.2f h" % sum(r["remaining"] for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
