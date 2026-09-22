"""Which line a session's time went to.

A day's timesheet groups by dimension, so several sessions with nothing tagged are one
line. Splitting that line is a correction to the day file; this register is what makes
the EVIDENCE follow, because the heartbeats behind it are immutable and still derive
the dimensions they always did.

Nothing here is billed or entered into F&O.
"""
import datetime
import io
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
import dashboard
from lib import sessionlines


class Register(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self):
        with io.open(sessionlines.path_for(self.tmp), encoding="utf-8", newline="") as f:
            return f.read()

    def test_the_first_row_writes_the_header(self):
        ok, msg = sessionlines.record("2026-09-09", "947f60fa", "customers/Carl-Ras/datahub",
                                      "", "CarlRData-555", "the cluster error", root=self.tmp)
        self.assertTrue(ok, msg)
        text = self.read()
        self.assertIn("# Session to F&O line", text)
        self.assertIn("| 2026-09-09 | 947f60fa | customers/Carl-Ras/datahub | - "
                      "| CarlRData-555 | the cluster error |", text)

    def test_a_blank_dimension_reads_back_blank(self):
        sessionlines.record("2026-09-09", "947f60fa", "customers/Carl-Ras/datahub",
                            "", "CarlRData-555", root=self.tmp)
        got = sessionlines.entries(self.tmp)[0]
        self.assertEqual(got["activity"], "")
        self.assertEqual(got["fno_task"], "CarlRData-555")

    def test_a_correction_is_another_row_and_the_later_one_wins(self):
        sessionlines.record("2026-09-09", "947f60fa", "p/x", "", "T-1", root=self.tmp)
        sessionlines.record("2026-09-09", "947f60fa", "p/x", "", "T-2", root=self.tmp)
        self.assertEqual(sessionlines.assigned(self.tmp)[("2026-09-09", "947f60fa", "p/x")],
                         {"activity": "", "fno_task": "T-2"})
        self.assertEqual(len(sessionlines.entries(self.tmp)), 2)

    def test_the_same_destination_twice_writes_nothing(self):
        sessionlines.record("2026-09-09", "947f60fa", "p/x", "", "T-1", root=self.tmp)
        ok, msg = sessionlines.record("2026-09-09", "947f60fa", "p/x", "", "T-1", root=self.tmp)
        self.assertTrue(ok)
        self.assertIn("already", msg)
        self.assertEqual(len(sessionlines.entries(self.tmp)), 1)

    def test_one_session_can_be_on_two_projects_the_same_day(self):
        # A session that switched customers is two stretches and two lines.
        sessionlines.record("2026-09-09", "947f60fa", "p/x", "", "T-1", root=self.tmp)
        sessionlines.record("2026-09-09", "947f60fa", "p/y", "", "T-9", root=self.tmp)
        a = sessionlines.assigned(self.tmp)
        self.assertEqual(a[("2026-09-09", "947f60fa", "p/x")]["fno_task"], "T-1")
        self.assertEqual(a[("2026-09-09", "947f60fa", "p/y")]["fno_task"], "T-9")

    def test_what_it_refuses(self):
        for args in (("2026-9-9", "947f60fa", "p/x"),
                     ("2026-09-09", "", "p/x"),
                     ("2026-09-09", "ab", "p/x"),
                     ("2026-09-09", "947f60fa", "")):
            ok, _ = sessionlines.record(*args, root=self.tmp)
            self.assertFalse(ok, args)
        self.assertFalse(os.path.exists(sessionlines.path_for(self.tmp)))

    def test_a_pipe_cannot_break_the_table(self):
        sessionlines.record("2026-09-09", "947f60fa", "p/x", "", "T-1",
                            "a | b\nc", root=self.tmp)
        self.assertEqual(len(self.read().rstrip().splitlines()[-1].split("|")), 9)
        self.assertEqual(sessionlines.entries(self.tmp)[0]["note"], "a b c")

    def test_no_file_is_no_rows(self):
        self.assertEqual(sessionlines.entries(self.tmp), [])
        self.assertEqual(sessionlines.assigned(self.tmp), {})

    def test_a_junk_row_is_skipped_not_fatal(self):
        os.makedirs(self.tmp, exist_ok=True)
        with io.open(sessionlines.path_for(self.tmp), "w", encoding="utf-8", newline="") as f:
            f.write(sessionlines.HEADER)
            f.write("| not a date | x | p/x | - | T-1 | - | - |\n")
            f.write("| 2026-09-09 | 947f60fa | p/x | - | T-1 | - | - |\n")
        self.assertEqual(len(sessionlines.entries(self.tmp)), 1)


class EvidenceFollowsTheSplit(unittest.TestCase):
    """The sessions shown under a line, once one of them has been split off.

    The heartbeats are immutable and still derive the dimensions they always did, so
    without the register both halves of a split line go on showing all of the day's
    sessions -- which is the thing the split was for."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._sl = dashboard.sessionlines.ROOT
        self._hb = dashboard.rollup.load_heartbeats
        self._mem = dashboard.memory_index
        dashboard.sessionlines.ROOT = self.tmp
        dashboard.rollup.load_heartbeats = lambda: self.HBS
        dashboard.memory_index = lambda: {}

    def tearDown(self):
        dashboard.sessionlines.ROOT = self._sl
        dashboard.rollup.load_heartbeats = self._hb
        dashboard.memory_index = self._mem
        shutil.rmtree(self.tmp, ignore_errors=True)

    @property
    def HBS(self):
        def hb(session, hour):
            start = datetime.datetime(2026, 9, 9, hour, 0, tzinfo=datetime.timezone.utc)
            return {"start": start, "end": start + datetime.timedelta(minutes=20),
                    "project": "Dev", "task": None, "session": session,
                    "date": "2026-09-09", "week": "2026-W37", "capped": None,
                    "raw_start": start}
        return [hb("947f60fa", 6), hb("96e67fec", 9), hb("a96a7c5d", 13)]

    def sessions(self, key):
        got = dashboard.collect_line_sessions("2026-09-09").get(key)
        return sorted(b["session"] for b in (got or {}).get("blocks", []))

    def test_untouched_they_are_all_on_the_one_line(self):
        self.assertEqual(self.sessions("2026-09-09|dev||"),
                         ["947f60fa", "96e67fec", "a96a7c5d"])

    def test_a_split_session_moves_to_its_own_line(self):
        dashboard.sessionlines.record("2026-09-09", "96e67fec", "Dev", "", "DEV-1",
                                      root=self.tmp)
        self.assertEqual(self.sessions("2026-09-09|dev||"), ["947f60fa", "a96a7c5d"])
        self.assertEqual(self.sessions("2026-09-09|dev||dev-1"), ["96e67fec"])

    def test_they_read_in_the_order_they_happened(self):
        got = dashboard.collect_line_sessions("2026-09-09")["2026-09-09|dev||"]
        self.assertEqual([b["from"] for b in got["blocks"]],
                         sorted(b["from"] for b in got["blocks"]))

    def test_a_register_row_for_another_day_changes_nothing(self):
        dashboard.sessionlines.record("2026-09-10", "96e67fec", "Dev", "", "DEV-1",
                                      root=self.tmp)
        self.assertEqual(self.sessions("2026-09-09|dev||"),
                         ["947f60fa", "96e67fec", "a96a7c5d"])


if __name__ == "__main__":
    unittest.main()
