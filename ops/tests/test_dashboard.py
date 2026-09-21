"""The dashboard server's own logic: the TODO.md write path, the project band rule,
and the payload cache.

`ops/TODO.md` is hand-maintained prose, so a tick has to change one line and leave the
rest of the file byte-for-byte alone -- the same standard the task-file write path is
held to, and for the same reason.
"""
import io
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
import dashboard


TODO = (
    "# TODO\n"
    "\n"
    "## Captured\n"
    "- [ ] 2026-07-06 - ask Niels for the Matas activity number\n"
    "- [x] 2026-07-10 - already done\n"
    "  - [ ] an indented capture\n"
    "- [ ] Time: no date on this one\n"
    "\n"
    "Some prose that is not a list at all.\n"
)


def project(key, ctx_status="active", days_idle=0):
    return {"key": key, "ctx_status": ctx_status, "days_idle": days_idle}


class TodoMutate(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "ops"))
        self.path = os.path.join(self.tmp, "ops", "TODO.md")
        self._root = dashboard.ROOT
        dashboard.ROOT = self.tmp
        self.write(TODO)

    def tearDown(self):
        dashboard.ROOT = self._root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, text):
        with io.open(self.path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def read(self):
        with io.open(self.path, encoding="utf-8", newline="") as f:
            return f.read()

    def todos(self):
        return dashboard.collect_todos()

    def test_the_open_items_are_found_with_their_line_numbers(self):
        items = self.todos()
        self.assertEqual([t["line"] for t in items], [3, 5, 6])
        self.assertEqual(items[0]["date"], "2026-07-06")
        self.assertEqual(items[2]["date"], "")

    def test_tick_marks_the_line_done(self):
        t = self.todos()[0]
        ok, msg = dashboard.todo_mutate(t["line"], "tick", t["raw"])
        self.assertTrue(ok, msg)
        line = self.read().splitlines()[t["line"]]
        self.assertTrue(line.startswith("- [x] 2026-07-06 - ask Niels"))
        self.assertIn("(done ", line)

    def test_drop_strikes_the_line_through(self):
        t = self.todos()[0]
        ok, msg = dashboard.todo_mutate(t["line"], "drop", t["raw"])
        self.assertTrue(ok, msg)
        line = self.read().splitlines()[t["line"]]
        self.assertTrue(line.startswith("- [x] ~~2026-07-06"))
        self.assertIn("~~  (dropped ", line)

    def test_a_ticked_item_leaves_the_open_list(self):
        t = self.todos()[0]
        dashboard.todo_mutate(t["line"], "tick", t["raw"])
        self.assertNotIn(t["line"], [x["line"] for x in self.todos()])
        self.assertEqual(len(self.todos()), 2)

    def test_every_other_line_is_untouched(self):
        before = self.read().splitlines(keepends=True)
        t = self.todos()[0]
        dashboard.todo_mutate(t["line"], "tick", t["raw"])
        after = self.read().splitlines(keepends=True)
        self.assertEqual(len(before), len(after))
        for i, (a, b) in enumerate(zip(before, after)):
            if i != t["line"]:
                self.assertEqual(a, b, "line %d changed" % i)

    def test_indentation_is_preserved(self):
        t = [x for x in self.todos() if x["line"] == 5][0]
        ok, msg = dashboard.todo_mutate(t["line"], "tick", t["raw"])
        self.assertTrue(ok, msg)
        self.assertTrue(self.read().splitlines()[5].startswith("  - [x] an indented capture"))

    def test_a_crlf_file_stays_crlf(self):
        self.write(TODO.replace("\n", "\r\n"))
        t = self.todos()[0]
        ok, msg = dashboard.todo_mutate(t["line"], "tick", t["raw"])
        self.assertTrue(ok, msg)
        out = self.read()
        self.assertEqual(out.count("\r\n"), TODO.count("\n"))
        self.assertEqual(out.count("\n"), out.count("\r\n"))   # not one bare LF introduced

    def test_a_file_without_a_trailing_newline_keeps_its_last_line(self):
        self.write("- [ ] the only item")
        t = self.todos()[0]
        ok, msg = dashboard.todo_mutate(0, "tick", t["raw"])
        self.assertTrue(ok, msg)
        self.assertTrue(self.read().startswith("- [x] the only item  (done "))
        self.assertFalse(self.read().endswith("\n"))

    def test_a_stale_line_is_refused(self):
        t = self.todos()[0]
        self.write(TODO.replace("ask Niels", "ask someone else"))
        ok, msg = dashboard.todo_mutate(t["line"], "tick", t["raw"])
        self.assertFalse(ok)
        self.assertIn("refresh", msg)
        self.assertIn("ask someone else", self.read())

    def test_an_out_of_range_line_is_refused(self):
        self.assertFalse(dashboard.todo_mutate(999, "tick", "- [ ] x")[0])
        self.assertFalse(dashboard.todo_mutate(-1, "tick", "- [ ] x")[0])
        self.assertFalse(dashboard.todo_mutate(None, "tick", "- [ ] x")[0])
        self.assertFalse(dashboard.todo_mutate(True, "tick", "- [ ] x")[0])

    def test_a_line_that_is_not_an_open_item_is_refused(self):
        raw = TODO.splitlines()[8]                      # the prose line
        ok, msg = dashboard.todo_mutate(8, "tick", raw)
        self.assertFalse(ok)
        self.assertIn("not an unchecked item", msg)

    def test_an_already_ticked_line_is_refused(self):
        raw = TODO.splitlines()[4]
        self.assertFalse(dashboard.todo_mutate(4, "tick", raw)[0])

    def test_an_unknown_action_writes_nothing(self):
        before = self.read()
        t = self.todos()[0]
        ok, msg = dashboard.todo_mutate(t["line"], "delete", t["raw"])
        self.assertFalse(ok)
        self.assertIn("unknown action", msg)
        self.assertEqual(self.read(), before)


class ProjectBand(unittest.TestCase):
    """The rule the Projects page bands on. It used to live in the browser."""

    def test_the_workspace_is_not_a_project(self):
        self.assertEqual(dashboard.project_band(project("Dev")), "workspace")

    def test_worked_recently_is_in_flight(self):
        self.assertEqual(dashboard.project_band(project("own/x", days_idle=0)), "inflight")
        self.assertEqual(dashboard.project_band(
            project("own/x", days_idle=dashboard.INFLIGHT_DAYS)), "inflight")

    def test_active_but_untouched_is_quiet(self):
        self.assertEqual(dashboard.project_band(
            project("own/x", days_idle=dashboard.INFLIGHT_DAYS + 1)), "quiet")

    def test_never_worked_is_quiet_not_in_flight(self):
        self.assertEqual(dashboard.project_band(project("own/x", days_idle=None)), "quiet")

    def test_a_finished_context_is_dormant_however_recent(self):
        for status in ("complete", "Delivered 2026-09-01", "archived"):
            self.assertEqual(dashboard.project_band(
                project("customers/A/p", ctx_status=status, days_idle=0)), "dormant")

    def test_a_missing_status_does_not_make_it_dormant(self):
        self.assertEqual(dashboard.project_band(
            project("customers/A/p", ctx_status="", days_idle=2)), "inflight")


class PayloadCache(unittest.TestCase):

    def setUp(self):
        self.calls = []
        self._real = dashboard._collect
        self._real_brief = dashboard._daybrief_model
        dashboard._collect = lambda: (self.calls.append(1), {"n": len(self.calls)})[1]
        dashboard.invalidate()

    def tearDown(self):
        dashboard._collect = self._real
        dashboard._daybrief_model = self._real_brief
        dashboard.invalidate()

    def test_a_second_read_inside_the_window_is_served_from_the_memo(self):
        first = dashboard.collect()
        self.assertEqual(dashboard.collect(), first)
        self.assertEqual(len(self.calls), 1)

    def test_force_walks_again(self):
        dashboard.collect()
        dashboard.collect(force=True)
        self.assertEqual(len(self.calls), 2)

    def test_invalidate_makes_the_next_read_walk(self):
        dashboard.collect()
        dashboard.invalidate()
        dashboard.collect()
        self.assertEqual(len(self.calls), 2)

    def test_an_expired_memo_walks_again(self):
        dashboard.collect()
        dashboard._cache["data"]["at"] -= dashboard.CACHE_TTL + 1
        dashboard.collect()
        self.assertEqual(len(self.calls), 2)

    def test_the_two_payloads_are_memoised_apart(self):
        dashboard._daybrief_model = lambda: {"brief": True}
        dashboard.collect()
        dashboard.collect_daybrief()
        dashboard.collect()
        self.assertEqual(len(self.calls), 1)

    def test_invalidate_drops_both(self):
        dashboard._daybrief_model = lambda: {"brief": True}
        dashboard.collect()
        dashboard.collect_daybrief()
        dashboard.invalidate()
        self.assertIsNone(dashboard._cache["today"]["v"])
        self.assertIsNone(dashboard._cache["data"]["v"])


class PostRoutes(unittest.TestCase):
    """The routing table the server dispatches writes through."""

    def test_every_write_path_has_a_route(self):
        self.assertEqual(sorted(dashboard.POST_ROUTES),
                         ["/api/fno", "/api/fnotask", "/api/launch", "/api/noinvoice",
                          "/api/reassign", "/api/task", "/api/timesheet", "/api/todo"])

    def test_a_route_passes_the_body_through_to_its_function(self):
        seen = {}
        real = dashboard.todo_mutate
        dashboard.todo_mutate = lambda *a: (seen.update(args=a), (True, "ok"))[1]
        try:
            ok, msg = dashboard.POST_ROUTES["/api/todo"](
                {"line": 7, "action": "tick", "raw": "- [ ] x"})
        finally:
            dashboard.todo_mutate = real
        self.assertTrue(ok)
        self.assertEqual(seen["args"], (7, "tick", "- [ ] x"))

    def test_a_missing_body_is_refused_rather_than_raising(self):
        # every route, including /api/launch -- an empty path used to resolve to the
        # server's own working directory and start a session there
        for path in dashboard.POST_ROUTES:
            ok, msg = dashboard.POST_ROUTES[path]({})
            self.assertFalse(ok, path + " accepted an empty body")

    def test_an_empty_launch_path_is_refused(self):
        self.assertEqual(dashboard.launch("", "claude"), (False, "no path given"))
        self.assertEqual(dashboard.launch(None, "code"), (False, "no path given"))


if __name__ == "__main__":
    unittest.main()
