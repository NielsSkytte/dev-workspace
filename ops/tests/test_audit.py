"""The three-way join behind the week's F&O lines.

A timesheet row, the 15+5 recomputation and the value record are keyed three different
ways, and a correction at /log moves only the first of them. Before this was joined
properly the week showed two half-lines -- one with hours and no measurement, one with the
measurement and no hours -- so a line read `Measured 0` beside a real F&O entry.

The invariant that matters: **every measured hour lands on exactly one line.** An hour that
vanishes understates the control; an hour counted twice overstates it, and the control is
what says the rules and the meter have not drifted apart.
"""
import unittest

import _bootstrap  # noqa: F401
import dashboard


def sheet_row(project, activity="", task="", hours=1.0, proj_id="230-02"):
    return {"project": project, "activity": activity, "fno_task": task, "hours": hours,
            "proj_id": proj_id, "billable": project.startswith("customers/")}


def value(project, activity="", task="", weighted=0.0, keyboard=0.0, turns=0, files=()):
    return {"project": project, "activity": activity, "fno_task": task,
            "weighted_h": weighted, "keyboard_h": keyboard, "turns": turns,
            "stretches": 1, "t5_events": 0, "tiers": {},
            "deliverables": [{"path": f} for f in files]}


def rows(sheet, measured, values):
    return dashboard.line_rows("2026-09-07", sheet, measured, values)


def by_task(out):
    return {r["fno_task"]: r for r in out}


class ExactMatch(unittest.TestCase):
    """The ordinary day: nothing was corrected, everything lines up."""

    def test_one_line_carries_all_three(self):
        s = [sheet_row("customers/C/p", task="T-1", hours=3.0)]
        out = rows(s, [sheet_row("customers/C/p", task="T-1", hours=2.5)],
                   [value("customers/C/p", task="T-1", weighted=4.0, keyboard=1.0, turns=20)])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["claimed"], 3.0)
        self.assertEqual(out[0]["measured"], 2.5)
        self.assertEqual(out[0]["weighted"], 4.0)
        self.assertEqual(out[0]["turns"], 20)
        self.assertFalse(out[0]["shared"])

    def test_a_live_day_falls_back_to_the_recomputation(self):
        m = [sheet_row("customers/C/p", task="T-1", hours=2.5)]
        out = rows(None, m, [])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["claimed"], 2.5)
        self.assertTrue(out[0]["live"])


class CorrectedLine(unittest.TestCase):
    """The case that was broken: /log changed the task, so nothing matches the sheet."""

    def setUp(self):
        self.sheet = [sheet_row("customers/Matas/D", activity="111953", task="Task-65904",
                                hours=8.0)]
        self.meas = [sheet_row("customers/Matas/D", activity="111953", task="Task-65905",
                               hours=4.0)]
        self.vals = [value("customers/Matas/D", activity="111953", task="Task-65905",
                           weighted=7.5, keyboard=0.93, turns=30)]

    def test_one_line_not_two(self):
        out = rows(self.sheet, self.meas, self.vals)
        self.assertEqual(len(out), 1, [r["fno_task"] for r in out])

    def test_it_keeps_the_timesheet_dimensions(self):
        # The sheet is what gets typed into F&O; the evidence follows it, never the reverse.
        out = rows(self.sheet, self.meas, self.vals)
        self.assertEqual(out[0]["fno_task"], "Task-65904")
        self.assertEqual(out[0]["claimed"], 8.0)

    def test_and_gains_the_evidence(self):
        out = rows(self.sheet, self.meas, self.vals)
        self.assertEqual(out[0]["measured"], 4.0)
        self.assertEqual(out[0]["weighted"], 7.5)
        self.assertEqual(out[0]["turns"], 30)

    def test_and_says_the_number_is_a_share(self):
        self.assertTrue(rows(self.sheet, self.meas, self.vals)[0]["shared"])


class SplitAcrossLines(unittest.TestCase):
    """Several registered lines on one project-date, evidence that matches none of them."""

    SHEET = [sheet_row("customers/C/p", task="A", hours=3.0),
             sheet_row("customers/C/p", task="B", hours=1.0)]
    MEAS = [sheet_row("customers/C/p", task="Z", hours=4.0)]
    VALS = [value("customers/C/p", task="Z", weighted=8.0, keyboard=2.0, turns=40)]

    def test_in_proportion_to_the_registered_hours(self):
        out = by_task(rows(self.SHEET, self.MEAS, self.VALS))
        self.assertEqual(out["A"]["measured"], 3.0)      # 3/4 of 4.0
        self.assertEqual(out["B"]["measured"], 1.0)      # 1/4 of 4.0

    def test_the_evidence_splits_the_same_way(self):
        out = by_task(rows(self.SHEET, self.MEAS, self.VALS))
        self.assertEqual(out["A"]["weighted"], 6.0)
        self.assertEqual(out["B"]["weighted"], 2.0)
        self.assertEqual(out["A"]["turns"], 30)
        self.assertEqual(out["B"]["turns"], 10)

    def test_the_density_is_preserved(self):
        # turns per registered hour is what decides where in the band a line sits, so a
        # split must not move it.
        out = by_task(rows(self.SHEET, self.MEAS, self.VALS))
        self.assertAlmostEqual(out["A"]["turns"] / out["A"]["claimed"],
                               out["B"]["turns"] / out["B"]["claimed"])

    def test_hours_are_conserved(self):
        out = rows(self.SHEET, self.MEAS, self.VALS)
        self.assertAlmostEqual(sum(r["measured"] for r in out), 4.0, places=2)
        self.assertAlmostEqual(sum(r["weighted"] for r in out), 8.0, places=2)

    def test_both_lines_say_it_is_a_share(self):
        self.assertTrue(all(r["shared"] for r in rows(self.SHEET, self.MEAS, self.VALS)))

    def test_lines_with_no_registered_hours_split_evenly(self):
        sheet = [sheet_row("customers/C/p", task="A", hours=0.0),
                 sheet_row("customers/C/p", task="B", hours=0.0)]
        out = by_task(rows(sheet, self.MEAS, self.VALS))
        self.assertEqual(out["A"]["measured"], 2.0)
        self.assertEqual(out["B"]["measured"], 2.0)


class NoRegisteredLine(unittest.TestCase):
    """Work measured on a project that was registered somewhere else that day."""

    def test_it_keeps_a_line_of_its_own(self):
        out = rows([sheet_row("customers/C/p", task="A", hours=3.0)],
                   [sheet_row("own/MetaAtomic", hours=9.25)],
                   [value("own/MetaAtomic", weighted=25.0)])
        self.assertEqual(len(out), 2)
        mine = [r for r in out if r["project"] == "own/MetaAtomic"][0]
        self.assertEqual(mine["claimed"], 0.0)
        self.assertEqual(mine["measured"], 9.25)
        self.assertEqual(mine["weighted"], 25.0)
        self.assertFalse(mine["shared"])

    def test_the_registered_line_is_untouched(self):
        # Cross-project reattribution cannot be inferred, so it must not be guessed.
        out = rows([sheet_row("customers/C/p", task="A", hours=3.0)],
                   [sheet_row("own/MetaAtomic", hours=9.25)],
                   [value("own/MetaAtomic", weighted=25.0)])
        mine = [r for r in out if r["project"] == "customers/C/p"][0]
        self.assertEqual(mine["measured"], 0.0)
        self.assertEqual(mine["weighted"], 0.0)

    def test_a_move_inside_one_customer_takes_the_evidence_with_it(self):
        # 2026-09-12 Aeven: the line was moved ServiceNowPOC -> AtomicServiceNow at /log.
        out = rows([sheet_row("customers/Aeven/AtomicServiceNow", activity="1", hours=2.0)],
                   [sheet_row("customers/Aeven/ServiceNowPOC", task="none", hours=2.5)],
                   [value("customers/Aeven/ServiceNowPOC", task="none", weighted=6.0)])
        self.assertEqual(len(out), 1, [r["project"] for r in out])
        self.assertEqual(out[0]["project"], "customers/Aeven/AtomicServiceNow")
        self.assertEqual(out[0]["measured"], 2.5)
        self.assertEqual(out[0]["weighted"], 6.0)
        self.assertTrue(out[0]["shared"])

    def test_across_customers_nothing_moves(self):
        out = rows([sheet_row("customers/A/p", task="X", hours=2.0)],
                   [sheet_row("customers/B/q", task="Y", hours=1.0)], [])
        self.assertEqual(by_task(out)["X"]["measured"], 0.0)
        self.assertEqual(by_task(out)["Y"]["measured"], 1.0)

    def test_a_recorded_move_takes_the_evidence_to_the_named_lines(self):
        # 2026-09-09: a session rooted in own/MetaAtomic, moved to two Carl Ras tasks at /log.
        sheet = [sheet_row("customers/Carl-Ras/datahub", task="CarlRData-666", hours=4.25),
                 sheet_row("customers/Carl-Ras/datahub", task="CarlRData-555", hours=5.75),
                 sheet_row("customers/Carl-Ras/datahub", task="CarlRData-553", hours=1.5)]
        out = dashboard.line_rows(
            "2026-09-09", sheet, [sheet_row("own/MetaAtomic", hours=10.0)],
            [value("own/MetaAtomic", weighted=20.0)],
            [{"date": "2026-09-09", "from": "own/MetaAtomic",
              "to": "customers/Carl-Ras/datahub", "tasks": ["CarlRData-666", "CarlRData-555"]}])
        got = by_task(out)
        self.assertNotIn("", got)                        # no homeless MetaAtomic line left
        self.assertEqual(got["CarlRData-666"]["measured"], 4.25)
        self.assertEqual(got["CarlRData-555"]["measured"], 5.75)
        self.assertEqual(got["CarlRData-553"]["measured"], 0.0)
        self.assertAlmostEqual(got["CarlRData-666"]["weighted"] + got["CarlRData-555"]["weighted"],
                               20.0, places=2)

    def test_several_stale_keys_give_one_line_not_several(self):
        out = rows([], [sheet_row("customers/A/p", task="X", hours=2.0)],
                   [value("customers/A/p", task="Y", weighted=12.0)])
        self.assertEqual(len(out), 1, [(r["fno_task"], r["measured"]) for r in out])
        self.assertEqual(out[0]["measured"], 2.0)
        self.assertEqual(out[0]["weighted"], 12.0)


class Helpers(unittest.TestCase):

    def test_weights_by_hours(self):
        slots = {"a": {"row": {"hours": 3.0}}, "b": {"row": {"hours": 1.0}}}
        self.assertEqual(dict(dashboard._weights(slots, ["a", "b"])), {"a": 0.75, "b": 0.25})

    def test_weights_with_no_hours_at_all(self):
        slots = {"a": {"row": {"hours": 0.0}}, "b": {"row": {"hours": 0.0}}}
        self.assertEqual(dict(dashboard._weights(slots, ["a", "b"])), {"a": 0.5, "b": 0.5})

    def test_merge_agg_unions_the_files(self):
        a = dashboard._blank_agg()
        a["files"] = {"x"}
        b = dashboard._blank_agg()
        b["files"] = {"y"}
        b["turns"] = 4
        dashboard._merge_agg(a, b)
        self.assertEqual(a["files"], {"x", "y"})
        self.assertEqual(a["turns"], 4)

    def test_scale_agg_keeps_hours_exact_and_counts_whole(self):
        a = dashboard._blank_agg()
        a["turns"], a["weighted"] = 10, 5.0
        got = dashboard._scale_agg(a, 0.25)
        self.assertEqual(got["weighted"], 1.25)
        # Half a turn is not a thing, so counts are rounded. Python rounds a .5 to even,
        # which across a split biases neither line -- fine for a count that only feeds the
        # turns-per-hour density.
        self.assertEqual(got["turns"], 2)


if __name__ == "__main__":
    unittest.main()
