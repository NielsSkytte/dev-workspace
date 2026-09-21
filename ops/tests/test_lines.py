"""Line descriptions: the file a session writes at /log, and reading it back.

The table has the same key as the timesheet day beside it, so the two line up row for
row. That is the whole contract -- get the key wrong and a description silently attaches
to the wrong line, or to none, which is worse than not having one.

The file is written by hand (by a session), so the reader is deliberately tolerant: a
malformed row costs that row, not the day.
"""
import io
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
from lib import lines


class DimKey(unittest.TestCase):
    """The key is the F&O dimension, and a placeholder is the absence of a value."""

    def test_a_full_line(self):
        self.assertEqual(lines.dimkey("customers/Carl-Ras/datahub", "600003", "CarlRData-557"),
                         "customers/Carl-Ras/datahub|600003|CarlRData-557")

    def test_the_timesheet_dash_is_nothing(self):
        self.assertEqual(lines.dimkey("Dev", "-", "-"), "Dev||")

    def test_so_is_none(self):
        # `fno_task: none` is the task-file convention for "no work item yet"; it is the
        # same line as one with no task at all, and must key the same.
        self.assertEqual(lines.dimkey("Dev", "", "none"), lines.dimkey("Dev", "-", "-"))

    def test_whitespace_does_not_make_a_new_line(self):
        self.assertEqual(lines.dimkey(" Dev ", " 600003 ", " X "), lines.dimkey("Dev", "600003", "X"))


class RoundTrip(unittest.TestCase):

    ROWS = [
        {"project": "customers/Carl-Ras/datahub", "activity": "", "fno_task": "CarlRData-557",
         "hours": 2.25, "description": "Unify: worked through the lakehouse dependencies."},
        {"project": "Dev", "activity": "", "fno_task": "", "hours": 1.5, "description": ""},
    ]

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, date, text):
        path = lines.path_for(date, self.tmp)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return path

    def test_render_then_read(self):
        self.write("2026-09-18", lines.render("2026-09-18", self.ROWS))
        got = lines.read_day("2026-09-18", self.tmp)
        self.assertEqual(got, {
            "customers/Carl-Ras/datahub||CarlRData-557":
                "Unify: worked through the lakehouse dependencies."})

    def test_an_empty_description_is_absent_not_blank(self):
        # A line written as `-` has not been described. Reading it as an empty string would
        # make the coverage check say the day was done.
        self.write("2026-09-18", lines.render("2026-09-18", self.ROWS))
        self.assertNotIn("Dev||", lines.read_day("2026-09-18", self.tmp))

    def test_a_pipe_in_the_sentence_cannot_break_the_table(self):
        rows = [dict(self.ROWS[0], description="ran a | b | c through the view")]
        self.write("2026-09-18", lines.render("2026-09-18", rows))
        got = lines.read_day("2026-09-18", self.tmp)
        self.assertEqual(list(got.values()), ["ran a / b / c through the view"])

    def test_no_file(self):
        self.assertEqual(lines.read_day("2026-09-18", self.tmp), {})

    def test_a_malformed_row_costs_that_row_only(self):
        self.write("2026-09-18",
                   "| Project | Activity | Task | Hours | Description |\n"
                   "|---|---|---|---|---|\n"
                   "| Dev | - | - | 1.50 | kept |\n"
                   "| broken row with too few cells |\n"
                   "| own/MetaAtomic | - | - | 0.75 | also kept |\n")
        got = lines.read_day("2026-09-18", self.tmp)
        self.assertEqual(sorted(got), ["Dev||", "own/MetaAtomic||"])

    def test_the_header_names_its_own_day_and_month(self):
        text = lines.render("2026-09-18", self.ROWS)
        self.assertIn("2026-09-18 (Fri)", text)
        self.assertIn("timesheet/2026-09/2026-09-18.md", text)

    def test_read_month(self):
        for d in ("2026-09-17", "2026-09-18"):
            self.write(d, lines.render(d, self.ROWS))
        got = lines.read_month("2026-09", self.tmp)
        self.assertEqual(sorted(got), ["2026-09-17", "2026-09-18"])

    def test_the_path_follows_the_timesheet_shape(self):
        p = lines.path_for("2026-09-18", self.tmp)
        self.assertTrue(p.endswith(os.path.join("lines", "2026-09", "2026-09-18.md")), p)


if __name__ == "__main__":
    unittest.main()
