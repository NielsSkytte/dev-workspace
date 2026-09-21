"""What an F&O task id is called.

`CarlRData-555` is what the time line carries and all F&O needs. It is also the thing you
have to pick correctly out of ten at entry time, and an id says nothing about itself. So a
name rides along in the picker -- from `ops/time/fno-tasks.md` if it has been recorded,
otherwise from the work-task carrying the id.

The name is display only. Nothing here may ever reach a timesheet line: a name in the Task
column is rejected by F&O, and would be wrong on an invoice if it were not.
"""
import io
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
from lib import fnotasks


def task(fno_task, title, slug="s"):
    return {"fno_task": fno_task, "title": title, "slug": slug}


class Register(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self):
        with io.open(fnotasks.path_for(self.tmp), encoding="utf-8", newline="") as f:
            return f.read()

    def test_the_first_name_writes_the_header(self):
        ok, msg = fnotasks.record("CarlRData-555", "Operational hardening", "Carl-Ras",
                                  root=self.tmp)
        self.assertTrue(ok, msg)
        text = self.read()
        self.assertIn("# F&O task names", text)
        self.assertIn("| CarlRData-555 | Operational hardening | Carl-Ras |", text)

    def test_a_correction_is_another_row_and_the_later_one_wins(self):
        fnotasks.record("CarlRData-555", "Old name", root=self.tmp)
        fnotasks.record("CarlRData-555", "Operational hardening", root=self.tmp)
        self.assertEqual(fnotasks.names(self.tmp)["CarlRData-555"]["name"],
                         "Operational hardening")
        self.assertEqual(self.read().count("CarlRData-555"), 2)

    def test_the_same_name_twice_writes_nothing(self):
        fnotasks.record("CarlRData-555", "Hardening", root=self.tmp)
        ok, msg = fnotasks.record("CarlRData-555", "Hardening", root=self.tmp)
        self.assertTrue(ok)
        self.assertIn("already", msg)
        self.assertEqual(self.read().count("CarlRData-555"), 1)

    def test_an_id_f_and_o_would_not_accept(self):
        for bad in ("CarlRData-555 (operation-hardening)",
                    "2026-09-09-carlras-metaatomic (ADO id pending)", "", "a|b"):
            ok, msg = fnotasks.record(bad, "x", root=self.tmp)
            self.assertFalse(ok, bad)

    def test_a_name_is_required(self):
        self.assertFalse(fnotasks.record("CarlRData-555", "   ", root=self.tmp)[0])

    def test_a_pipe_in_the_name_cannot_break_the_table(self):
        fnotasks.record("T-1", "a | b", root=self.tmp)
        self.assertEqual(fnotasks.names(self.tmp)["T-1"]["name"], "a b")

    def test_no_file_is_no_names(self):
        self.assertEqual(fnotasks.names(self.tmp), {})


class Resolve(unittest.TestCase):

    TASKS = [task("CarlRData-555", "Carl Ras - operation_hardening"),
             task("CarlRData-555", "Carl Ras - a second one on the same id"),
             task("none", "not an id"),
             task("", "no id at all")]

    def test_the_register_wins(self):
        got = fnotasks.resolve(["CarlRData-555"], self.TASKS,
                               registered={"CarlRData-555": {"name": "Operational hardening"}})
        self.assertEqual(got["CarlRData-555"]["name"], "Operational hardening")
        self.assertEqual(got["CarlRData-555"]["source"], "register")

    def test_and_the_work_task_stands_in(self):
        got = fnotasks.resolve(["CarlRData-555"], self.TASKS, registered={})
        self.assertEqual(got["CarlRData-555"]["name"], "Carl Ras - operation_hardening")
        self.assertEqual(got["CarlRData-555"]["source"], "work-task")

    def test_every_work_task_on_the_id_is_carried(self):
        # Four Carl Ras work-tasks share one id; which is the name is a judgement, but
        # losing the others would hide that they share it.
        got = fnotasks.resolve(["CarlRData-555"], self.TASKS, registered={})
        self.assertEqual(len(got["CarlRData-555"]["titles"]), 2)

    def test_an_id_with_nothing_behind_it(self):
        got = fnotasks.resolve(["CarlRData-999"], self.TASKS, registered={})
        self.assertEqual(got["CarlRData-999"]["name"], "")
        self.assertEqual(got["CarlRData-999"]["source"], "")

    def test_placeholders_are_not_ids(self):
        got = fnotasks.resolve(["none"], self.TASKS, registered={})
        self.assertEqual(got["none"]["titles"], [])

    def test_it_says_when_f_and_o_would_reject_the_id(self):
        got = fnotasks.resolve(["CarlRData-555", "CarlRData-555 (operation-hardening)",
                                "2026-09-09-carlras-metaatomic-implementation (ADO id pending)"],
                               self.TASKS, registered={})
        self.assertTrue(got["CarlRData-555"]["ok"])
        self.assertFalse(got["CarlRData-555 (operation-hardening)"]["ok"])
        self.assertFalse(got["2026-09-09-carlras-metaatomic-implementation (ADO id pending)"]["ok"])

    def test_a_slug_shaped_id_is_still_reported_not_dropped(self):
        # It is on real timesheet lines, so hiding it would hide the problem.
        got = fnotasks.resolve(["aeven-servicenow-offer-pdf"], self.TASKS, registered={})
        self.assertIn("aeven-servicenow-offer-pdf", got)
        self.assertTrue(got["aeven-servicenow-offer-pdf"]["ok"])   # shape is legal, meaning is not


if __name__ == "__main__":
    unittest.main()
