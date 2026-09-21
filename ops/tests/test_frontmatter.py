"""Task-file frontmatter editing -- the dashboard write path.

`_apply_fm` is what every mechanical task mutation goes through (done, park,
wait, ask-sent). It rewrites a task file in place, so a round-trip that loses
or rewrites anything it was not asked to change is silent data loss.
"""
import unittest

import _bootstrap  # noqa: F401
import dashboard


TASK = (
    "---\n"
    "status: open\n"
    "project: customers/Carl-Ras/datahub\n"
    "waiting_on:\n"
    "resume_on:\n"
    "activity: Analysis   # the F&O activity\n"
    "---\n"
    "\n"
    "# A task\n"
    "\n"
    "## Progress\n"
    "- 2026-09-14 - something happened\n"
)


def fm_value(text, key):
    """The value of a top-level frontmatter key, read back off the raw line."""
    block = text.split("---\n")[1]
    for line in block.splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip()
    return None


def body_of(text):
    return text.split("---\n", 2)[2]


class ApplyFrontmatter(unittest.TestCase):

    def test_an_existing_field_is_replaced(self):
        out = dashboard._apply_fm(TASK, {"status": "done"})
        self.assertEqual(fm_value(out, "status"), "done")

    def test_an_empty_value_blanks_the_field(self):
        out = dashboard._apply_fm(TASK, {"status": ""})
        self.assertEqual(fm_value(out, "status"), "")

    def test_a_missing_field_is_appended(self):
        out = dashboard._apply_fm(TASK, {"customer_ask": "sent 2026-09-21"})
        self.assertEqual(fm_value(out, "customer_ask"), "sent 2026-09-21")

    def test_other_fields_and_their_comments_survive(self):
        out = dashboard._apply_fm(TASK, {"status": "done"})
        self.assertIn("activity: Analysis   # the F&O activity", out)
        self.assertEqual(fm_value(out, "project"), "customers/Carl-Ras/datahub")

    def test_the_body_is_untouched(self):
        out = dashboard._apply_fm(TASK, {"status": "done"})
        self.assertEqual(body_of(out), body_of(TASK))

    def test_field_order_is_stable(self):
        out = dashboard._apply_fm(TASK, {"status": "done"})
        keys = [l.split(":", 1)[0] for l in out.split("---\n")[1].splitlines()
                if ":" in l and not l.startswith(" ")]
        self.assertEqual(keys[:5], ["status", "project", "waiting_on", "resume_on",
                                    "activity"])

    def test_a_file_with_no_frontmatter_is_returned_unchanged(self):
        plain = "# Just a heading\n\nSome text.\n"
        self.assertEqual(dashboard._apply_fm(plain, {"status": "done"}), plain)

    def test_several_updates_apply_in_one_pass(self):
        out = dashboard._apply_fm(TASK, {"waiting_on": "customer", "resume_on": ""})
        self.assertEqual(fm_value(out, "waiting_on"), "customer")
        self.assertEqual(fm_value(out, "resume_on"), "")

    # ---- values the UI can actually produce ----

    def test_a_value_containing_a_backslash_is_written_literally(self):
        # `wait` takes free text from the day view; a Windows path is ordinary
        out = dashboard._apply_fm(TASK, {"waiting_on": r"file at C:\Dev\ops"})
        self.assertEqual(fm_value(out, "waiting_on"), r"file at C:\Dev\ops")

    def test_a_value_containing_a_group_reference_is_written_literally(self):
        out = dashboard._apply_fm(TASK, {"waiting_on": r"see \g<1> in the spec"})
        self.assertEqual(fm_value(out, "waiting_on"), r"see \g<1> in the spec")

    def test_a_value_containing_a_colon_is_written_literally(self):
        out = dashboard._apply_fm(TASK, {"waiting_on": "Ole: the export file"})
        self.assertEqual(fm_value(out, "waiting_on"), "Ole: the export file")

    # ---- shapes the regex editor reaches into by mistake ----

    def test_an_indented_key_inside_a_block_value_is_not_edited(self):
        text = ("---\n"
                "status: open\n"
                "notes: |\n"
                "  status: this is prose, not a field\n"
                "---\n"
                "\n# body\n")
        out = dashboard._apply_fm(text, {"status": "done"})
        self.assertIn("  status: this is prose, not a field", out)
        self.assertEqual(fm_value(out, "status"), "done")

    def test_a_matching_line_in_the_body_is_not_edited(self):
        text = ("---\n"
                "status: open\n"
                "---\n"
                "\n"
                "# A task\n"
                "status: mentioned in the body\n")
        out = dashboard._apply_fm(text, {"status": "done"})
        self.assertIn("status: mentioned in the body", out)


if __name__ == "__main__":
    unittest.main()
