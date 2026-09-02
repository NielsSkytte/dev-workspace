"""Where a period's invoiced hours land in the bonus model, and what the nearest boundary costs.

The bonus is a STEP function on faktureringsprocent (invoiced hours / monthly basis), changing only
at whole 10% marks. Landing at 89.8% pays the 80% rate, not the 90% one -- so the distance to the
nearest boundary matters far more than the hours themselves. Run this at every close.

EVALUATED PER MONTH, not accumulated over the year (Niels, 2026-09-02). Each month stands alone: a
weak month cannot be rescued by a later strong one, and a strong month is not dragged down by an
earlier weak one. May-Aug 2026 taken together would be 46.10% and pay nothing; taken monthly,
August pays 20%. So the question at every close is only ever about THAT month's boundary.

The 50% tier pays 0%, so reaching it is worth nothing -- the first paying boundary is 60%. July 2026
landed 1.00 h short of 50% and lost NOTHING by it.

    python ops/time/bonus.py 145 --basis 155.5
    python ops/time/bonus.py 145 --basis 155.5 --rate 1200

THE BASIS IS NOT A CONSTANT. faktureringsprocent = "Fakturerbare timer" / "Timer per maaned", and
"Timer per maaned" changes every month. Read it off the F&O page, never assume:

    https://pingprod.operations.dynamics.com/?cmp=ping&mi=HRMUtalizationEmplTrans_PIN
    ("Beregnet nytte per medarbejder per periode")

Observed 2026: May 140.00, Jun 163.00, Jul 170.00, Aug 155.50, Sep 163.00. A wrong basis moves the
answer by a whole tier -- assuming a flat 160 put August at 90.6% when it is 93.25%.

FERIE DOES NOT LOWER THE TARGET. August 2026 has 21 arbejdsdage and Niels took a week off; had the
basis been reduced it would read ~118 h, but F&O shows the full 155.50. So a vacation week costs
about 5 x 7.4 = 37 h of billing capacity while the bonus target stays put -- a month with holiday in
it is structurally harder, and that is worth knowing BEFORE the month rather than at its close.
(Not yet confirmed with HR whether the bonus rule itself adjusts separately; the page does not.)

Note the workspace's own coverage check does the opposite: absence.md removes vacation days from
ITS denominator, which is why August reads 104% internally and 93.25% for bonus. Both are correct;
they answer different questions. Only faktureringsprocent pays.

That page also shows "Nytte til stede" = Fakturerbare / Normtimer -- a DIFFERENT denominator that
IS absence-adjusted (141.00 in August, giving 102.84%). The BONUS runs on faktureringsprocent, not
on that one. Don't read the flattering number by mistake.

WHAT THIS IS NOT. A boundary that is a couple of hours away is a reason to go LOOKING for hours
that were genuinely worked and never registered -- an unlogged meeting, a day the value model
supports and the timesheet undercounts. It is never a reason to enter hours that were not worked.
The evidence rule is unchanged: see ops/memory/store/time-shortfall-can-be-in-the-target.

Model parameters come from Niels's bonus sheet; ASCII only per AGENTS.md > Conventions.
"""
import argparse

# faktureringsprocent -> bonus pct. Floor to the tier at or below the achieved percentage;
# 100% and above all pay 24% (the sheet is flat from 100% to 150%).
TIERS = [(0.50, 0.00), (0.60, 0.02), (0.70, 0.10), (0.80, 0.16), (0.90, 0.20), (1.00, 0.24)]
BASIS = 155.5     # "Timer per maaned" -- PER MONTH, read it off the F&O page. See the docstring.
RATE = 1200.0     # "gennemsnitsats" -- average hourly rate feeding Grundlag

THIN = 2.0        # h. Below this above a boundary, the tier is one correction away from dropping.


def tier_of(pct):
    """Bonus pct for an achieved faktureringsprocent, and the boundary it sits on."""
    hit = [t for t in TIERS if t[0] <= pct]
    if not hit:
        return 0.0, None
    boundary, bonus = max(hit)
    return bonus, boundary


def bonus_kr(hours, basis=BASIS, rate=RATE):
    """Grundlag is the actual invoiced value; only the bonus PERCENTAGE steps."""
    pct = hours / basis
    bonus, _ = tier_of(pct)
    return hours * rate * bonus


def report(hours, basis=BASIS, rate=RATE):
    pct = hours / basis
    bonus, boundary = tier_of(pct)
    out = ["", "  %.2f h / %.2f h = %.2f%% faktureringsprocent" % (hours, basis, pct * 100)]

    if boundary is None:
        out.append("  -> below the 50% floor; no bonus tier reached")
    else:
        out.append("  -> tier %.0f%%, bonus %.0f%% = %s kr"
                   % (boundary * 100, bonus * 100, "{:,.0f}".format(hours * rate * bonus)))
        margin = hours - boundary * basis
        drop = bonus_kr(hours, basis, rate) - bonus_kr(boundary * basis - 0.01, basis, rate)
        flag = "  <-- THIN" if margin < THIN else ""
        out.append("  -> %.2f h above the %.0f%% line (%.2f h); losing it costs %s kr%s"
                   % (margin, boundary * 100, boundary * basis, "{:,.0f}".format(drop), flag))

    # Show the next boundary AND, when that one pays nothing, the next one that does. The 50% tier
    # pays 0% -- pointing at it as "the next boundary" is worthless advice for an early month.
    nxt = sorted(t for t in TIERS if t[0] > pct)
    if not nxt:
        out += ["", "  at or above the top tier -- bonus is capped at 24%"]
        return "\n".join(l for l in out if l != "")

    out.append("")
    shown = [nxt[0]]
    if nxt[0][1] <= bonus:                      # next boundary adds nothing
        paying = [t for t in nxt if t[1] > bonus]
        if paying:
            shown.append(paying[0])
    for nb, _nbonus in shown:
        need = nb * basis
        gain = bonus_kr(need, basis, rate) - bonus_kr(hours, basis, rate)
        note = "  (pays no more than you get now)" if gain <= 0 else ""
        out.append("  %.0f%% at %.2f h -- %.2f h away, worth %s kr%s"
                   % (nb * 100, need, need - hours, "{:,.0f}".format(gain), note))
        if gain > 0 and need > hours:
            out.append("    = %s kr per hour, IF those hours were actually worked."
                       % "{:,.0f}".format(gain / (need - hours)))
    return "\n".join(l for l in out if l != "")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Bonus tier and distance to the nearest boundary.")
    ap.add_argument("hours", type=float, help="invoiced hours for the period")
    ap.add_argument("--basis", type=float, default=BASIS, help="Mdl timer (default %g)" % BASIS)
    ap.add_argument("--rate", type=float, default=RATE, help="average rate (default %g)" % RATE)
    a = ap.parse_args()
    print(report(a.hours, a.basis, a.rate))
    print("")
