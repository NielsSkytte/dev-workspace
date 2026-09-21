"""The not-invoiced register: "do not invoice this, under any circumstances".

Some work inside a customer folder is not that customer's to pay for -- registering the
time, fixing the setup, building the dashboard. The folder cannot know that, so it is
written down, and the point of writing it down is that it holds afterwards: through the
rollup deriving the day, through the entry page grouping it, through a correction, and on
a day that is still running with no timesheet file yet.

`ops/time/not-invoiced.md` is a register, like `absence.md` -- a decision only the owner
can make, applied by everything downstream. The register wins.
"""
import io
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
import dashboard
import rollup
from lib import noinvoice


class Register(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self):
        with io.open(noinvoice.path_for(self.tmp), encoding="utf-8", newline="") as f:
            return f.read()

    def test_the_first_record_writes_the_header(self):
        ok, msg = noinvoice.record("2026-09-15", "customers/W/p", why="registering time",
                                   root=self.tmp)
        self.assertTrue(ok, msg)
        text = self.read()
        self.assertIn("# Not invoiced", text)
        self.assertIn("| 2026-09-15 | customers/W/p | - | - | registering time |", text)

    def test_it_appends_and_never_rewrites(self):
        noinvoice.record("2026-09-15", "customers/W/p", root=self.tmp)
        noinvoice.record("2026-09-16", "customers/W/p", root=self.tmp)
        self.assertEqual(len(noinvoice.entries(self.tmp)), 2)
        self.assertEqual(self.read().count("# Not invoiced"), 1)

    def test_the_same_decision_twice_is_one_row(self):
        noinvoice.record("2026-09-15", "customers/W/p", root=self.tmp)
        ok, msg = noinvoice.record("2026-09-15", "customers/W/p", root=self.tmp)
        self.assertTrue(ok)
        self.assertIn("already", msg)
        self.assertEqual(len(noinvoice.entries(self.tmp)), 1)

    def test_a_pipe_in_the_reason_cannot_break_the_table(self):
        noinvoice.record("2026-09-15", "customers/W/p", why="a | b", root=self.tmp)
        self.assertEqual(noinvoice.entries(self.tmp)[0]["why"], "a b")

    def test_internal_work_is_refused(self):
        for p in ("Dev", "own/MetaAtomic"):
            ok, msg = noinvoice.record("2026-09-15", p, root=self.tmp)
            self.assertFalse(ok, p)
            self.assertIn("already not invoiced", msg)

    def test_a_bad_date_or_project(self):
        self.assertFalse(noinvoice.record("15-09-2026", "customers/W/p", root=self.tmp)[0])
        self.assertFalse(noinvoice.record("2026-09-15", "../../etc", root=self.tmp)[0])

    def test_no_file_is_no_entries(self):
        self.assertEqual(noinvoice.entries(self.tmp), [])
        self.assertIsNone(noinvoice.covers("2026-09-15", "customers/W/p", root=self.tmp))


class Covers(unittest.TestCase):
    """What a row matches. The common decision is about the work, not the dimension."""

    ROWS = [{"date": "2026-09-15", "project": "customers/W/p", "activity": "", "task": "",
             "why": "", "recorded": ""},
            {"date": "2026-09-16", "project": "customers/W/p", "activity": "", "task": "T-1",
             "why": "", "recorded": ""},
            {"date": "*", "project": "customers/W/admin", "activity": "", "task": "",
             "why": "", "recorded": ""}]

    def c(self, date, project, activity="", task=""):
        return noinvoice.covers(date, project, activity, task, self.ROWS)

    def test_date_and_project_alone_cover_the_whole_line(self):
        self.assertTrue(self.c("2026-09-15", "customers/W/p"))
        self.assertTrue(self.c("2026-09-15", "customers/W/p", "600003", "T-9"))

    def test_another_date_is_not_covered(self):
        self.assertIsNone(self.c("2026-09-17", "customers/W/p"))

    def test_another_project_is_not_covered(self):
        self.assertIsNone(self.c("2026-09-15", "customers/W/other"))

    def test_a_task_narrows_it(self):
        self.assertTrue(self.c("2026-09-16", "customers/W/p", "", "T-1"))
        self.assertIsNone(self.c("2026-09-16", "customers/W/p", "", "T-2"))

    def test_a_star_covers_every_date(self):
        for d in ("2026-01-01", "2026-12-31"):
            self.assertTrue(self.c(d, "customers/W/admin"), d)


class RollupApplies(unittest.TestCase):
    """The register reaches the hours before the day file is ever written."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._root = rollup.ROOT
        rollup.ROOT = self.tmp

    def tearDown(self):
        rollup.ROOT = self._root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def hbs(self, project):
        import datetime
        t0 = datetime.datetime(2026, 9, 15, 8, 0, tzinfo=datetime.timezone.utc)
        return [{"start": t0, "end": t0 + datetime.timedelta(minutes=30),
                 "project": project, "task": None, "session": "s1",
                 "date": "2026-09-15"}]

    def test_a_customer_line_is_billable_by_default(self):
        rows = rollup.rows_for(self.hbs("customers/W/p"))
        self.assertTrue(rows[0]["billable"])

    def test_and_is_not_once_it_is_on_the_register(self):
        noinvoice.record("2026-09-15", "customers/W/p", why="registering time",
                         root=self.tmp)
        rows = rollup.rows_for(self.hbs("customers/W/p"))
        self.assertFalse(rows[0]["billable"])
        self.assertEqual(rows[0]["hours"], 0.5)      # the hours are not lost, just not billed

    def test_another_day_is_untouched(self):
        noinvoice.record("2026-09-16", "customers/W/p", root=self.tmp)
        self.assertTrue(rollup.rows_for(self.hbs("customers/W/p"))[0]["billable"])

    def test_the_written_day_file_carries_it(self):
        noinvoice.record("2026-09-15", "customers/W/p", root=self.tmp)
        rows = rollup.rows_for(self.hbs("customers/W/p"))
        table, bill, intern = rollup.render_table(rows)
        self.assertIn("| 0.50 | no |", table)
        self.assertEqual(bill, 0.0)
        self.assertEqual(intern, 0.5)


class EntryApplies(unittest.TestCase):
    """And it wins over the timesheet file, so a decision taken after the day was written
    is honoured without rewriting it."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._root, self._comp = dashboard.ROOT, dashboard.read_companies
        self._rules, self._tr = dashboard.fno.rules, noinvoice.ROOT
        dashboard.ROOT = self.tmp
        noinvoice.ROOT = self.tmp
        dashboard.read_companies = lambda: [
            {"firma": "PING", "kunde": "W", "key": "w", "projektnr": "230-02",
             "aktivitet": "", "task_note": ""}]
        dashboard.fno.rules = lambda root=None: {}

    def tearDown(self):
        dashboard.ROOT, dashboard.read_companies = self._root, self._comp
        dashboard.fno.rules, noinvoice.ROOT = self._rules, self._tr
        shutil.rmtree(self.tmp, ignore_errors=True)

    def row(self):
        e = {"date": "2026-09-15", "project": "customers/W/p", "proj_id": "230-02",
             "activity": "", "fno_task": "", "hours": 3.0, "billable": True, "live": False}
        return dashboard.collect_entry([e], ["W"], "2026-09-21")["rows"][0]

    def test_the_file_says_billable_and_the_register_says_no(self):
        self.assertFalse(self.row()["no_entry"])
        noinvoice.record("2026-09-15", "customers/W/p", root=self.tmp)
        got = self.row()
        self.assertTrue(got["no_entry"])
        self.assertEqual(got["firma"], "INTERNAL")
        self.assertEqual(got["customer"], "W")       # still that client's cost


if __name__ == "__main__":
    unittest.main()
