"""The value model: tiering, stretch grouping, and the customer cap that moves
weighted hours between dates.

ADR-004. The cap is the last thing between a weighted day and a number a
customer would query, so the invariants here are: hours move but do not vanish,
a closed month is never crossed, and no customer-day is left over the cap while
the month still has room.
"""
import datetime
import unittest

import _bootstrap  # noqa: F401
import value
from lib.workspace import customer_name


UTC = datetime.timezone.utc


def rec(date, project, weighted_h, billable=True, task=None):
    return {"date": date, "project": project, "task": task,
            "keyboard_min": 0.0, "keyboard_h": 0.0, "turns": 1, "stretches": 1,
            "overhead_min": 0.0, "tiers": {}, "deliverables": [], "t5_events": 0,
            "weighted_h": weighted_h, "proj_id": "P1", "activity": "", "fno_task": "",
            "billable": billable}


def turn(start_min, end_min):
    base = datetime.datetime(2026, 9, 14, 9, 0, tzinfo=UTC)
    return {"start": base + datetime.timedelta(minutes=start_min),
            "end": base + datetime.timedelta(minutes=end_min)}


def total(records):
    return round(sum(r["weighted_h"] for r in records), 2)


def cust_day(records):
    tot = {}
    for r in records:
        if not r["billable"]:
            continue
        k = (customer_name(r["project"]), r["date"])
        tot[k] = tot.get(k, 0.0) + r["weighted_h"]
    return tot


class CustomerName(unittest.TestCase):

    def test_customer_project_gives_the_customer_name(self):
        self.assertEqual(customer_name("customers/Carl-Ras/datahub"), "Carl-Ras")

    def test_internal_project_has_no_customer(self):
        self.assertIsNone(customer_name("own/MetaAtomic"))
        self.assertIsNone(customer_name("Dev"))


class TurnTier(unittest.TestCase):
    """Tier from tool evidence alone (before the ledger and the T5 gate)."""

    def _turn(self, muts=(), execs=0, research=0, reads=0):
        return {"muts": list(muts), "execs": execs, "research": research, "reads": reads}

    def test_a_turn_with_nothing_is_tier_1(self):
        self.assertEqual(value.turn_tier(self._turn()), 1)

    def test_reads_alone_reach_tier_2_only_at_three(self):
        self.assertEqual(value.turn_tier(self._turn(reads=2)), 1)
        self.assertEqual(value.turn_tier(self._turn(reads=3)), 2)

    def test_research_is_tier_2(self):
        self.assertEqual(value.turn_tier(self._turn(research=1)), 2)

    def test_a_shell_command_is_tier_3(self):
        self.assertEqual(value.turn_tier(self._turn(execs=1)), 3)

    def test_a_small_edit_is_tier_3_and_a_large_one_tier_4(self):
        small = [("f.py", value.T4_MIN_LINES - 1)]
        large = [("f.py", value.T4_MIN_LINES)]
        self.assertEqual(value.turn_tier(self._turn(muts=small)), 3)
        self.assertEqual(value.turn_tier(self._turn(muts=large)), 4)

    def test_lines_accumulate_across_edits_in_one_turn(self):
        muts = [("a.py", 11), ("b.py", 11)]
        self.assertEqual(value.turn_tier(self._turn(muts=muts)), 4)


class StretchGroups(unittest.TestCase):
    """A gap over TURN_GAP splits a stretch. Matches the timesheet idle timeout."""

    def test_no_turns_gives_no_groups(self):
        self.assertEqual(value.stretch_groups([]), [])

    def test_turns_inside_the_gap_are_one_stretch(self):
        items = [turn(0, 10), turn(20, 30)]
        self.assertEqual(len(value.stretch_groups(items)), 1)

    def test_a_gap_over_the_limit_starts_a_new_stretch(self):
        items = [turn(0, 10), turn(40, 50)]
        self.assertEqual(len(value.stretch_groups(items)), 2)

    def test_a_gap_exactly_at_the_limit_does_not_split(self):
        items = [turn(0, 10), turn(10 + int(value.TURN_GAP), 40)]
        self.assertEqual(len(value.stretch_groups(items)), 1)

    def test_out_of_order_input_is_grouped_chronologically(self):
        items = [turn(40, 50), turn(0, 10)]
        groups = value.stretch_groups(items)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0], [1])

    def test_a_contained_turn_does_not_shorten_the_stretch(self):
        items = [turn(0, 60), turn(5, 10), turn(70, 80)]
        self.assertEqual(len(value.stretch_groups(items)), 1)


class ApplyCaps(unittest.TestCase):

    def test_a_day_under_the_cap_is_untouched(self):
        recs = [rec("2026-09-14", "customers/A/p", 8.0)]
        moves, unplaced, flags = value.apply_caps(recs)
        self.assertEqual(moves, [])
        self.assertEqual(unplaced, [])
        self.assertEqual(flags, [])
        self.assertEqual(recs[0]["weighted_h"], 8.0)

    def test_excess_spills_and_hours_are_preserved(self):
        recs = [rec("2026-09-14", "customers/A/p", 14.0),
                rec("2026-09-15", "customers/A/p", 2.0)]
        before = total(recs)
        value.apply_caps(recs)
        self.assertEqual(total(recs), before)

    def test_no_customer_day_is_left_over_the_cap_when_the_month_has_room(self):
        recs = [rec("2026-09-14", "customers/A/p", 16.0),
                rec("2026-09-15", "customers/A/p", 1.0),
                rec("2026-09-16", "customers/A/p", 1.0)]
        value.apply_caps(recs)
        for hours in cust_day(recs).values():
            self.assertLessEqual(hours, value.CUSTOMER_CAP + 1e-9)

    def test_internal_hours_are_not_capped(self):
        recs = [rec("2026-09-14", "Dev", 20.0, billable=False)]
        moves, unplaced, flags = value.apply_caps(recs)
        self.assertEqual(moves, [])
        self.assertEqual(recs[0]["weighted_h"], 20.0)

    def test_the_spill_never_crosses_a_month_boundary(self):
        # the only other date with room is in the next month; a closed month may
        # already be invoiced, so the excess stays put and is reported unplaced
        recs = [rec("2026-09-30", "customers/A/p", 16.0),
                rec("2026-10-01", "customers/A/p", 1.0)]
        moves, unplaced, flags = value.apply_caps(recs)
        self.assertEqual(moves, [])
        self.assertEqual(len(unplaced), 1)
        self.assertEqual(unplaced[0]["date"], "2026-09-30")

    def test_two_customers_on_one_date_are_capped_independently(self):
        recs = [rec("2026-09-14", "customers/A/p", 10.0),
                rec("2026-09-15", "customers/A/p", 1.0),
                rec("2026-09-14", "customers/B/q", 10.0),
                rec("2026-09-15", "customers/B/q", 1.0)]
        before = total(recs)
        moves, unplaced, flags = value.apply_caps(recs)
        self.assertEqual(moves, [])
        self.assertEqual(total(recs), before)

    def test_a_spill_lands_on_an_existing_line_rather_than_a_duplicate(self):
        recs = [rec("2026-09-14", "customers/A/p", 14.0),
                rec("2026-09-15", "customers/A/p", 1.0)]
        value.apply_caps(recs)
        on_15 = [r for r in recs if r["date"] == "2026-09-15"]
        self.assertEqual(len(on_15), 1)

    def test_a_spill_to_an_empty_date_records_where_it_came_from(self):
        recs = [rec("2026-09-14", "customers/A/p", 14.0),
                rec("2026-09-15", "customers/A/q", 1.0)]
        value.apply_caps(recs)
        clones = [r for r in recs if r.get("spilled_from") == "2026-09-14"]
        self.assertEqual(len(clones), 1)
        self.assertEqual(clones[0]["date"], "2026-09-15")

    def test_a_day_over_the_review_threshold_is_flagged_not_moved(self):
        # two customers, each under its own cap, but the day totals over FLAG_CAP
        recs = [rec("2026-09-14", "customers/A/p", 9.0),
                rec("2026-09-14", "customers/B/q", 9.0)]
        moves, unplaced, flags = value.apply_caps(recs)
        self.assertEqual(moves, [])
        self.assertEqual([f["level"] for f in flags], ["REVIEW"])
        self.assertAlmostEqual(flags[0]["hours"], 18.0)

    def test_a_physically_impossible_day_is_flagged_as_such(self):
        recs = [rec("2026-09-14", "customers/A/p", 9.0),
                rec("2026-09-14", "customers/B/q", 9.0),
                rec("2026-09-14", "customers/C/r", 9.0)]
        moves, unplaced, flags = value.apply_caps(recs)
        self.assertEqual([f["level"] for f in flags], ["IMPOSSIBLE"])

    def test_dust_lines_are_dropped(self):
        recs = [rec("2026-09-14", "customers/A/p", 0.005),
                rec("2026-09-14", "customers/A/q", 1.0)]
        value.apply_caps(recs)
        self.assertEqual(len(recs), 1)

    def test_an_impossible_week_terminates_instead_of_looping(self):
        # every date is already at the cap; the guard must end the loop
        recs = [rec("2026-09-%02d" % d, "customers/A/p", 20.0) for d in range(14, 19)]
        before = total(recs)
        moves, unplaced, flags = value.apply_caps(recs)
        self.assertEqual(total(recs), before)
        self.assertTrue(unplaced)


if __name__ == "__main__":
    unittest.main()
