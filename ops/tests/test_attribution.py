"""Does what a session is producing match what it started with?

A turn writes a heartbeat with a project and, if one is held, a work-task. When the tag is
dropped the line is still written -- just without the dimension that customer requires --
and it surfaces weeks later at the month close. On 2026-09-21, twelve turns of customer
work were billed untagged and one stray `cd` into a customer node produced a line with no
Proj ID; none of it said anything at the time.

The rule has to be quiet where there is nothing wrong, or it will be ignored. Internal
time is never entered in F&O, so it can never be short of anything. A customer that
registers on nothing but a Proj ID is fine without a task. And holding a work-task is not
enough: `fno_task: none` is the convention for "no DevOps work item yet", so a correctly
tagged session can still be producing a line that cannot be typed.
"""
import io
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
from lib import attribution


NODE = ("# %(c)s\n\n## Customer\nname: %(c)s\nstatus: active\n%(extra)s\n\n"
        "## About\nx\n")
PROJECT = "# p\n\n## Identity\ntype: function\nstatus: active\nfno_code: %s\n"
TASK = ("---\ntitle: t\nproject: %(project)s\nstatus: open\n"
        "activity: %(activity)s\nfno_task: %(task)s\n---\n\n# t\n")


class Drift(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "ops", "tasks", "open"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def put(self, rel, text):
        p = os.path.join(self.tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def customer(self, name, extra="", code="901-01"):
        self.put("customers/%s/CLAUDE.md" % name, NODE % {"c": name, "extra": extra})
        self.put("customers/%s/p/CLAUDE.md" % name, PROJECT % code)

    def task(self, slug, project, activity="", task="none"):
        self.put("ops/tasks/open/%s.md" % slug,
                 TASK % {"project": project, "activity": activity, "task": task})

    def d(self, project, task_slug="", held="", held_project=""):
        return attribution.drift(project, task_slug, held, held_project, root=self.tmp)

    # ---- quiet where there is nothing wrong

    def test_the_workspace_is_never_reported(self):
        self.assertIsNone(self.d("Dev"))

    def test_nor_an_internal_project(self):
        self.assertIsNone(self.d("own/MetaAtomic"))

    def test_nor_a_customer_that_requires_nothing_extra(self):
        self.customer("Widget")
        self.assertIsNone(self.d("customers/Widget/p"))

    def test_nor_one_worked_under_a_task_that_carries_the_id(self):
        self.customer("Widget", "fno_requires: task")
        self.task("t1", "customers/Widget/p", task="WID-1")
        self.assertIsNone(self.d("customers/Widget/p", "t1"))

    # ---- the three ways a line comes out unenterable

    def test_no_task_where_the_customer_registers_on_one(self):
        self.customer("Widget", "fno_requires: task")
        got = self.d("customers/Widget/p")
        self.assertEqual(got["kind"], "no-task")
        self.assertIn("no task is held", got["why"])
        self.assertIn("/switch-task", got["fix"])

    def test_a_held_task_with_no_devops_id_is_still_short(self):
        # The loop this closes: hold the right work-task, and the line is STILL unenterable
        # because nobody has opened the work item yet.
        self.customer("Widget", "fno_requires: task")
        self.task("t1", "customers/Widget/p", task="none")
        got = self.d("customers/Widget/p", "t1")
        self.assertEqual(got["kind"], "no-task")
        self.assertIn("no DevOps id", got["why"])
        self.assertIn("Projects", got["fix"])

    def test_a_task_held_on_another_customer(self):
        self.customer("Widget", "fno_requires: task")
        self.customer("Other")
        got = self.d("customers/Widget/p", "", "t9", "customers/Other/p")
        self.assertEqual(got["kind"], "elsewhere")
        self.assertIn("customers/Other/p", got["why"])

    def test_a_customer_node(self):
        self.customer("Widget")
        got = self.d("customers/Widget")
        self.assertEqual(got["kind"], "node")
        self.assertIn("not a project", got["why"])

    def test_a_project_with_no_code_anywhere(self):
        self.customer("Widget", code="")
        got = self.d("customers/Widget/p")
        self.assertEqual(got["kind"], "no-task")
        self.assertIn("no Proj ID", got["why"])

    # ---- activity, and where it can come from

    def test_activity_required_and_nothing_supplies_one(self):
        self.customer("Widget", "fno_requires: activity")
        got = self.d("customers/Widget/p")
        self.assertEqual(got["kind"], "no-task")
        self.assertIn("registers on activity", got["why"])

    def test_the_customer_default_settles_it(self):
        self.customer("Widget", "fno_requires: activity\nfno_activity: 600003")
        self.assertIsNone(self.d("customers/Widget/p"))

    def test_so_does_the_work_tasks_own(self):
        self.customer("Widget", "fno_requires: activity")
        self.task("t1", "customers/Widget/p", activity="600003")
        self.assertIsNone(self.d("customers/Widget/p", "t1"))

    def test_and_so_does_the_sheet(self):
        self.customer("Widget", "fno_requires: activity")
        sheet = [{"firma": "PING", "kunde": "Widget", "key": "widget",
                  "projektnr": "901-01", "aktivitet": "datakilder", "task_note": ""}]
        self.assertIsNone(attribution.drift("customers/Widget/p", "", "", "",
                                            sheet=sheet, root=self.tmp))

    # ---- one finding, most specific first

    def test_a_node_reports_as_a_node_not_as_a_missing_task(self):
        self.customer("Widget", "fno_requires: task")
        self.assertEqual(self.d("customers/Widget")["kind"], "node")

    def test_a_task_held_elsewhere_beats_everything(self):
        self.customer("Widget", "fno_requires: task", code="")
        self.customer("Other")
        self.assertEqual(self.d("customers/Widget/p", "", "t9",
                                "customers/Other/p")["kind"], "elsewhere")


class TaskDims(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "ops", "tasks", "open"))
        with io.open(os.path.join(self.tmp, "ops", "tasks", "open", "t1.md"),
                     "w", encoding="utf-8", newline="") as f:
            f.write(TASK % {"project": "customers/W/p", "activity": "600003",
                            "task": "WID-1"})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_reads_both(self):
        self.assertEqual(attribution.task_dims("t1", self.tmp), ("600003", "WID-1"))

    def test_an_unknown_slug(self):
        self.assertEqual(attribution.task_dims("nope", self.tmp), ("", ""))

    def test_no_slug(self):
        self.assertEqual(attribution.task_dims("", self.tmp), ("", ""))


if __name__ == "__main__":
    unittest.main()
