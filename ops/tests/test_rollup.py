"""The timesheet arithmetic: the 15+5 model, the top-up distribution, and the
merge/spill rules that decide what date an hour is registered on.

These numbers reach an invoice, so every test here asserts one of two things:
the documented rule, or the invariant that hours are MOVED and never invented
or lost.
"""
import contextlib
import datetime
import io
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
import rollup
from lib.workspace import billing_entity


UTC = datetime.timezone.utc


def t(h, m=0):
    """A datetime on a fixed day -- only the differences matter here."""
    return datetime.datetime(2026, 9, 14, h, m, tzinfo=UTC)


def hb(project, task, start, end, date="2026-09-14"):
    return {"project": project, "task": task, "start": start, "end": end, "date": date}


def entry(date, project, hours, billable=True, activity="", fno_task="", live=False):
    return {"date": date, "project": project, "proj_id": "P1", "activity": activity,
            "fno_task": fno_task, "hours": hours, "billable": billable, "live": live}


def quiet(fn, *a, **kw):
    """rollup reports merges and spills on stdout; the tests assert on values."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


WEEK = ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]


class StretchHours(unittest.TestCase):
    """README section 3: a stretch is active time plus a 5 min tail; a gap over
    15 min starts a new stretch."""

    def test_no_intervals_is_zero(self):
        self.assertEqual(rollup.stretch_hours([]), 0.0)

    def test_single_interval_gets_one_tail_buffer(self):
        # 60 min worked + 5 min tail
        self.assertAlmostEqual(rollup.stretch_hours([(t(9), t(10))]), 65 / 60.0)

    def test_gap_under_idle_timeout_stays_one_stretch(self):
        # 09:00-09:30, 09:40-10:00 -> 10 min gap, one stretch 09:00-10:00 + one tail
        got = rollup.stretch_hours([(t(9), t(9, 30)), (t(9, 40), t(10))])
        self.assertAlmostEqual(got, 65 / 60.0)

    def test_gap_over_idle_timeout_splits_and_buffers_twice(self):
        # 09:00-09:30, 10:00-10:30 -> 30 min gap, two stretches of 30 min, two tails
        got = rollup.stretch_hours([(t(9), t(9, 30)), (t(10), t(10, 30))])
        self.assertAlmostEqual(got, (30 + 5 + 30 + 5) / 60.0)

    def test_gap_exactly_at_idle_timeout_does_not_split(self):
        got = rollup.stretch_hours([(t(9), t(9, 30)), (t(9, 45), t(10))])
        self.assertAlmostEqual(got, 65 / 60.0)

    def test_contained_interval_does_not_shorten_the_stretch(self):
        got = rollup.stretch_hours([(t(9), t(10)), (t(9, 10), t(9, 20))])
        self.assertAlmostEqual(got, 65 / 60.0)

    def test_unsorted_input_gives_the_same_answer(self):
        ivs = [(t(10), t(10, 30)), (t(9), t(9, 30))]
        self.assertAlmostEqual(rollup.stretch_hours(ivs),
                               rollup.stretch_hours(list(reversed(ivs))))


class RoundQuarter(unittest.TestCase):
    """F&O takes quarter hours."""

    def test_rounds_to_the_nearest_quarter(self):
        self.assertEqual(rollup.round_quarter(1.10), 1.0)
        self.assertEqual(rollup.round_quarter(1.13), 1.25)
        self.assertEqual(rollup.round_quarter(0.0), 0.0)

    def test_exact_half_quarter_rounds_to_even(self):
        # round() is round-half-to-even; pinned here so a change is visible
        self.assertEqual(rollup.round_quarter(0.125), 0.0)
        self.assertEqual(rollup.round_quarter(0.375), 0.5)


class Group(unittest.TestCase):

    def test_groups_by_project_and_task(self):
        hbs = [hb("customers/A/p", None, t(9), t(10)),
               hb("customers/A/p", "slug", t(10), t(11)),
               hb("customers/A/p", None, t(11), t(12))]
        g = rollup.group(hbs)
        self.assertEqual(len(g), 2)
        self.assertEqual(sorted(len(v) for v in g.values()), [1, 2])


class BillingEntity(unittest.TestCase):
    """The cap is a statement about a customer, not a folder."""

    def test_customer_project_rolls_up_two_levels(self):
        self.assertEqual(billing_entity("customers/Carl-Ras/datahub"),
                         "customers/Carl-Ras")

    def test_own_project_is_its_own_entity(self):
        self.assertEqual(billing_entity("own/MetaAtomic"), "own/MetaAtomic")

    def test_bare_name_is_returned_unchanged(self):
        self.assertEqual(billing_entity("Dev"), "Dev")


class WeekKeyAndWorkday(unittest.TestCase):

    def test_week_key_is_iso(self):
        self.assertEqual(rollup.week_key("2026-09-14"), "2026-W38")

    def test_iso_week_number_is_zero_padded(self):
        self.assertEqual(rollup.week_key("2026-01-05"), "2026-W02")

    def test_weekend_is_not_a_workday(self):
        self.assertTrue(rollup.is_workday("2026-09-18"))    # Friday
        self.assertFalse(rollup.is_workday("2026-09-19"))   # Saturday
        self.assertFalse(rollup.is_workday("2026-09-20"))   # Sunday


class DistributeHours(unittest.TestCase):
    """README section 8: the top-up is proportional, billable-only, and lands
    the rounding drift on the largest line so the day totals exactly."""

    def test_zero_or_negative_extra_changes_nothing(self):
        rows = [entry("d", "customers/A/p", 3.0)]
        self.assertEqual(rollup.distribute_hours(rows, 0)[0]["hours"], 3.0)
        self.assertEqual(rollup.distribute_hours(rows, -1)[0]["hours"], 3.0)

    def test_empty_rows_are_returned_unchanged(self):
        self.assertEqual(rollup.distribute_hours([], 2.0), [])

    def test_single_row_absorbs_the_whole_top_up(self):
        rows = [entry("d", "customers/A/p", 3.0)]
        rollup.distribute_hours(rows, 1.5)
        self.assertEqual(rows[0]["hours"], 4.5)

    def test_day_totals_exactly_base_plus_extra(self):
        rows = [entry("d", "customers/A/p", 2.0), entry("d", "customers/B/q", 3.0),
                entry("d", "customers/C/r", 1.0)]
        base = sum(r["hours"] for r in rows)
        rollup.distribute_hours(rows, 1.5)
        self.assertAlmostEqual(sum(r["hours"] for r in rows), base + 1.5, places=2)

    def test_internal_lines_are_never_inflated(self):
        rows = [entry("d", "customers/A/p", 2.0, billable=True),
                entry("d", "Dev", 3.0, billable=False)]
        rollup.distribute_hours(rows, 1.0)
        self.assertEqual(rows[1]["hours"], 3.0)
        self.assertEqual(rows[0]["hours"], 3.0)

    def test_a_day_with_no_billable_line_still_places_the_hours(self):
        rows = [entry("d", "Dev", 2.0, billable=False),
                entry("d", "own/X", 2.0, billable=False)]
        rollup.distribute_hours(rows, 1.0)
        self.assertAlmostEqual(sum(r["hours"] for r in rows), 5.0, places=2)

    def test_proportional_share_follows_the_larger_line(self):
        rows = [entry("d", "customers/A/p", 6.0), entry("d", "customers/B/q", 2.0)]
        rollup.distribute_hours(rows, 2.0)
        self.assertGreater(rows[0]["hours"] - 6.0, rows[1]["hours"] - 2.0)


class ConsolidateWeek(unittest.TestCase):
    """Merging moves hours between dates. It must never invent or lose one."""

    def test_small_entries_collapse_onto_one_day(self):
        es = [entry("2026-09-14", "customers/A/p", 0.5),
              entry("2026-09-15", "customers/A/p", 0.5),
              entry("2026-09-16", "customers/A/p", 0.5)]
        out = quiet(rollup.consolidate_week, es, WEEK)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["date"], "2026-09-14")
        self.assertAlmostEqual(out[0]["hours"], 1.5)

    def test_entries_at_or_over_the_threshold_stay_put(self):
        es = [entry("2026-09-14", "customers/A/p", 2.0),
              entry("2026-09-15", "customers/A/p", 3.0)]
        out = quiet(rollup.consolidate_week, es, WEEK)
        self.assertEqual(sorted(e["date"] for e in out), ["2026-09-14", "2026-09-15"])

    def test_week_total_is_preserved(self):
        es = [entry("2026-09-14", "customers/A/p", 0.75),
              entry("2026-09-15", "customers/A/p", 1.25),
              entry("2026-09-16", "customers/B/q", 0.5),
              entry("2026-09-17", "customers/B/q", 4.0)]
        before = sum(e["hours"] for e in es)
        out = quiet(rollup.consolidate_week, es, WEEK)
        self.assertAlmostEqual(sum(e["hours"] for e in out), before, places=2)

    def test_different_projects_do_not_merge_together(self):
        es = [entry("2026-09-14", "customers/A/p", 0.5),
              entry("2026-09-14", "customers/B/q", 0.5)]
        out = quiet(rollup.consolidate_week, es, WEEK)
        self.assertEqual(len(out), 2)

    def test_billable_and_internal_lines_do_not_merge_together(self):
        es = [entry("2026-09-14", "customers/A/p", 0.5, billable=True),
              entry("2026-09-15", "customers/A/p", 0.5, billable=False)]
        out = quiet(rollup.consolidate_week, es, WEEK)
        self.assertEqual(len(out), 2)

    def test_an_explicit_threshold_overrides_the_default(self):
        # the F&O entry page passes a higher threshold to get fewer lines to type
        es = [entry("2026-09-14", "customers/A/p", 3.0),
              entry("2026-09-15", "customers/A/p", 1.0)]
        out = quiet(rollup.consolidate_week, es, WEEK, 5.0)
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0]["hours"], 4.0)

    def test_a_group_that_cannot_fit_is_left_where_it_was_worked(self):
        # the customer is already at the cap every day of the week
        es = [entry(d, "customers/A/p", rollup.DAY_CAP) for d in WEEK]
        es.append(entry("2026-09-14", "customers/A/p2", 0.5))
        before = sum(e["hours"] for e in es)
        out = quiet(rollup.consolidate_week, es, WEEK)
        self.assertAlmostEqual(sum(e["hours"] for e in out), before, places=2)
        self.assertTrue(any(e["project"] == "customers/A/p2" and e["date"] == "2026-09-14"
                            for e in out))


class SpillOverCap(unittest.TestCase):
    """No customer shows more than DAY_CAP on one date; hours move, never vanish."""

    def _cust_day(self, out):
        tot = {}
        for e in out:
            k = (billing_entity(e["project"]), e["date"])
            tot[k] = tot.get(k, 0.0) + e["hours"]
        return tot

    def test_a_day_under_the_cap_is_untouched(self):
        es = [entry("2026-09-14", "customers/A/p", 8.0)]
        out = quiet(rollup.spill_over_cap, es, WEEK)
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0]["hours"], 8.0)

    def test_excess_moves_off_the_over_cap_date(self):
        es = [entry("2026-09-14", "customers/A/p", 8.0),
              entry("2026-09-14", "customers/A/q", 6.0)]
        out = quiet(rollup.spill_over_cap, es, WEEK)
        tot = self._cust_day(out)
        self.assertAlmostEqual(tot[("customers/A", "2026-09-14")], rollup.DAY_CAP, places=2)
        self.assertAlmostEqual(sum(e["hours"] for e in out), 14.0, places=2)

    def test_total_hours_are_preserved_across_a_spill(self):
        es = [entry("2026-09-14", "customers/A/p", 9.0),
              entry("2026-09-14", "customers/A/q", 7.0),
              entry("2026-09-15", "customers/A/p", 3.0)]
        before = sum(e["hours"] for e in es)
        out = quiet(rollup.spill_over_cap, es, WEEK)
        self.assertAlmostEqual(sum(e["hours"] for e in out), before, places=2)

    def test_no_customer_day_exceeds_the_cap_when_the_week_has_room(self):
        es = [entry("2026-09-14", "customers/A/p", 9.0),
              entry("2026-09-14", "customers/A/q", 7.0)]
        out = quiet(rollup.spill_over_cap, es, WEEK)
        for hours in self._cust_day(out).values():
            self.assertLessEqual(hours, rollup.DAY_CAP + 1e-9)

    def test_two_customers_on_one_date_are_capped_independently(self):
        es = [entry("2026-09-14", "customers/A/p", 10.0),
              entry("2026-09-14", "customers/B/q", 10.0)]
        out = quiet(rollup.spill_over_cap, es, WEEK)
        self.assertEqual(sorted(e["date"] for e in out), ["2026-09-14", "2026-09-14"])

    def test_identical_lines_landing_on_one_date_are_folded(self):
        es = [entry("2026-09-14", "customers/A/p", 13.0),
              entry("2026-09-15", "customers/A/p", 1.0)]
        out = quiet(rollup.spill_over_cap, es, WEEK)
        on_15 = [e for e in out if e["date"] == "2026-09-15"]
        self.assertEqual(len(on_15), 1)
        self.assertAlmostEqual(sum(e["hours"] for e in out), 14.0, places=2)

    def test_a_full_week_keeps_the_excess_where_it_was_measured(self):
        es = [entry(d, "customers/A/p", rollup.DAY_CAP) for d in WEEK]
        es.append(entry("2026-09-14", "customers/A/q", 2.0))
        before = sum(e["hours"] for e in es)
        out = quiet(rollup.spill_over_cap, es, WEEK)
        self.assertAlmostEqual(sum(e["hours"] for e in out), before, places=2)

    def test_zero_hour_lines_are_dropped(self):
        es = [entry("2026-09-14", "customers/A/p", 0.0),
              entry("2026-09-14", "customers/A/q", 1.0)]
        out = quiet(rollup.spill_over_cap, es, WEEK)
        self.assertEqual(len(out), 1)


class WeightedHours(unittest.TestCase):
    """The evidence behind a top-up, parsed back out of ops/time/value/<date>.md."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "value"))
        self._root = rollup.ROOT
        rollup.ROOT = self.tmp

    def tearDown(self):
        rollup.ROOT = self._root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, date, text):
        with open(os.path.join(self.tmp, "value", date + ".md"), "w", encoding="utf-8") as f:
            f.write(text)

    def test_missing_file_gives_no_evidence(self):
        self.assertEqual(rollup.weighted_hours("2026-09-14"), (None, None))

    def test_both_lines_are_read(self):
        self._write("2026-09-14",
                    "# Value 2026-09-14\n\n"
                    "**Billable:** 3.20 h keyboard -> 7.75 h\n"
                    "**Internal:** 1.00 h keyboard -> 2.50 h\n")
        self.assertEqual(rollup.weighted_hours("2026-09-14"), (7.75, 2.5))

    def test_a_file_with_only_one_line_reports_the_other_as_missing(self):
        self._write("2026-09-14", "**Billable:** 1.00 h keyboard -> 4.00 h\n")
        self.assertEqual(rollup.weighted_hours("2026-09-14"), (4.0, None))


if __name__ == "__main__":
    unittest.main()
