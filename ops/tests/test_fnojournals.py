"""The register of what F&O holds (ops/time/fno-journals.md)."""
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
from lib import fnojournals

HEAD = ("| Journal | Company | Status | Date | Customer | Proj ID | Activity | Task | Hours | Verified |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n")


class Entries(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, body):
        with open(fnojournals.path_for(self.tmp), "w", encoding="utf-8") as f:
            f.write("# F&O journals\n\n" + HEAD + body)

    def test_a_missing_file_is_empty(self):
        self.assertEqual(fnojournals.entries(self.tmp), [])

    def test_a_row_reads_with_dash_as_none(self):
        self.write("| PING-1 | PING | Finished | 2026-09-02 | Carl-Ras | 230-02 | - | CarlRData-557 | 9.50 | 2026-09-29 |\n")
        e = fnojournals.entries(self.tmp)
        self.assertEqual(len(e), 1)
        self.assertEqual(e[0]["activity"], "")
        self.assertEqual(e[0]["fno_task"], "CarlRData-557")
        self.assertEqual(e[0]["hours"], 9.5)
        self.assertEqual(e[0]["status"], "Finished")

    def test_unknown_status_and_bad_hours_are_skipped(self):
        self.write("| PING-1 | PING | Maybe | 2026-09-02 | C | 1 | - | - | 1.00 | x |\n"
                   "| PING-1 | PING | Created | 2026-09-02 | C | 1 | - | - | lots | x |\n")
        self.assertEqual(fnojournals.entries(self.tmp), [])


if __name__ == "__main__":
    unittest.main()
