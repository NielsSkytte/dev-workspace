"""The shared read layer.

These parsers are now single-sourced, so a change here reaches the dashboard, the
day brief, the timesheet and the value model at once. That is the reason for the
layer and the reason it is the most worth pinning.
"""
import datetime
import json
import os
import shutil
import tempfile
import unittest

import _bootstrap  # noqa: F401
from lib import heartbeats, substrate, workspace


CARD = """---
status: open
project: customers/Carl-Ras/datahub
activity: Analysis   # the F&O activity
---

# A task

## Goal
Prove the numbers.

**Done when:** the customer signs off.

## Where we stand - 2026-09-21
Waiting on the export.

## Open threads
- One thing
- ~~A resolved thing~~
- A thing that wraps
  onto a second line

## State
**Status:** active
**Last worked:** 2026-09-21 by Niels
**In progress:**
- Building the gate
**Blocked on:**
- Ole: the export file
"""


class Read(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, data):
        p = os.path.join(self.tmp, name)
        with open(p, "wb") as f:
            f.write(data)
        return p

    def test_a_missing_file_reads_as_empty(self):
        self.assertEqual(substrate.read(os.path.join(self.tmp, "nope.md")), "")

    def test_a_directory_reads_as_empty(self):
        self.assertEqual(substrate.read(self.tmp), "")

    def test_crlf_is_normalised(self):
        p = self._write("a.md", b"one\r\ntwo\r\n")
        self.assertEqual(substrate.read(p), "one\ntwo\n")

    def test_file_field_reads_the_first_match_and_strips_a_comment(self):
        p = self._write("c.md", b"## Identity\nfno_code: ABC-1   # the code\nstatus: active\n")
        self.assertEqual(substrate.file_field(p, "fno_code"), "ABC-1")
        self.assertEqual(substrate.file_field(p, "status"), "active")

    def test_file_field_on_a_missing_key_or_file_is_none(self):
        p = self._write("c.md", b"nothing here\n")
        self.assertIsNone(substrate.file_field(p, "fno_code"))
        self.assertIsNone(substrate.file_field(os.path.join(self.tmp, "x.md"), "fno_code"))

    def test_file_field_treats_an_empty_value_as_absent(self):
        p = self._write("c.md", b"fno_code:\n")
        self.assertIsNone(substrate.file_field(p, "fno_code"))


class Frontmatter(unittest.TestCase):

    def test_keys_values_and_body(self):
        fm, body = substrate.frontmatter(CARD)
        self.assertEqual(fm["status"], "open")
        self.assertEqual(fm["project"], "customers/Carl-Ras/datahub")
        self.assertTrue(body.startswith("\n# A task"))

    def test_an_inline_comment_is_stripped_from_the_value(self):
        fm, _ = substrate.frontmatter(CARD)
        self.assertEqual(fm["activity"], "Analysis")

    def test_no_frontmatter_returns_the_whole_text(self):
        fm, body = substrate.frontmatter("# Just a heading\n")
        self.assertEqual(fm, {})
        self.assertEqual(body, "# Just a heading\n")

    def test_an_indented_key_is_content_not_a_field(self):
        text = "---\nnotes: |\n  status: prose\n---\n\nbody\n"
        fm, _ = substrate.frontmatter(text)
        self.assertEqual(sorted(fm), ["notes"])

    def test_a_key_in_the_body_is_not_a_field(self):
        fm, _ = substrate.frontmatter("---\nstatus: open\n---\n\nproject: not a field\n")
        self.assertEqual(sorted(fm), ["status"])


class Identity(unittest.TestCase):

    CLAUDE = ("# Project\n\n## Identity\nfno_code: CARL-1\nstatus: active\n"
              "type: delivery   # a comment\n\n## Something else\nnot: a field\n")

    def test_the_block_is_read(self):
        ident = substrate.identity(self.CLAUDE)
        self.assertEqual(ident["fno_code"], "CARL-1")
        self.assertEqual(ident["type"], "delivery")

    def test_it_stops_at_the_next_heading(self):
        self.assertNotIn("not", substrate.identity(self.CLAUDE))

    def test_no_identity_block_is_an_empty_dict(self):
        self.assertEqual(substrate.identity("# A wiki mirror\n"), {})


class Sections(unittest.TestCase):

    def test_every_h2_is_returned_with_its_body(self):
        s = substrate.sections(CARD)
        self.assertIn("Goal", s)
        self.assertIn("State", s)
        self.assertTrue(s["Goal"].startswith("Prove the numbers."))

    def test_section_matches_a_heading_with_trailing_text(self):
        body = substrate.section(CARD, "Where we stand")
        self.assertIn("Waiting on the export.", body)

    def test_section_of_a_missing_heading_is_empty(self):
        self.assertEqual(substrate.section(CARD, "Nothing"), "")


class Bullets(unittest.TestCase):

    def test_struck_through_items_are_dropped(self):
        items = substrate.bullets(substrate.sections(CARD)["Open threads"])
        self.assertNotIn("A resolved thing", items)

    def test_the_limit_is_honoured_and_none_returns_all(self):
        body = "\n".join("- item %d" % i for i in range(10))
        self.assertEqual(len(substrate.bullets(body)), 6)
        self.assertEqual(len(substrate.bullets(body, limit=2)), 2)
        self.assertEqual(len(substrate.bullets(body, limit=None)), 10)

    def test_numbered_items_count_as_bullets(self):
        self.assertEqual(substrate.bullets("1. first\n2. second"), ["first", "second"])

    def test_bullets_joined_folds_a_wrapped_item(self):
        items = substrate.bullets_joined(substrate.section(CARD, "Open threads"))
        self.assertIn("A thing that wraps onto a second line", items)

    def test_bullets_joined_keeps_a_struck_through_item(self):
        items = substrate.bullets_joined(substrate.section(CARD, "Open threads"))
        self.assertEqual(len(items), 3)


class LabelledLines(unittest.TestCase):

    def test_field_reads_a_labelled_value(self):
        state = substrate.sections(CARD)["State"]
        self.assertEqual(substrate.field(state, "Status"), "active")
        self.assertEqual(substrate.field(state, "Last worked"), "2026-09-21 by Niels")

    def test_field_of_a_missing_label_is_empty(self):
        self.assertEqual(substrate.field("", "Status"), "")

    def test_labelled_collects_the_bullets_under_one_label(self):
        state = substrate.sections(CARD)["State"]
        self.assertEqual(substrate.labelled(state, "In progress"), ["Building the gate"])
        self.assertEqual(substrate.labelled(state, "Blocked on"), ["Ole: the export file"])


class TextNormalisation(unittest.TestCase):

    def test_plain_strips_inline_markdown_and_keeps_the_words(self):
        self.assertEqual(substrate.plain("a `code` and **bold** and ~~gone~~"),
                         "a code and bold and gone")

    def test_plain_unwraps_links(self):
        self.assertEqual(substrate.plain("see [the doc](http://x/y)"), "see the doc")
        self.assertEqual(substrate.plain("see [[wiki page]]"), "see wiki page")

    def test_clean_collapses_newlines_where_plain_keeps_them(self):
        self.assertEqual(substrate.clean("one\ntwo"), "one two")
        self.assertIn("\n", substrate.plain("one\ntwo"))

    def test_clean_truncates_with_an_ellipsis(self):
        self.assertEqual(substrate.clean("abcdefghij", 8), "abcde...")

    def test_clean_drops_html_comments(self):
        self.assertEqual(substrate.clean("keep <!-- drop --> this"), "keep this")

    def test_first_para_takes_the_first_paragraph_only(self):
        self.assertEqual(substrate.first_para("one\nline\n\nsecond para"), "one line")

    def test_first_sentence_stops_at_the_full_stop(self):
        self.assertEqual(substrate.first_sentence("One thing. Two things."), "One thing.")

    def test_first_sentence_without_punctuation_returns_all_of_it(self):
        self.assertEqual(substrate.first_sentence("no full stop here"), "no full stop here")


class Dates(unittest.TestCase):

    def test_parse_date_takes_a_leading_iso_date(self):
        self.assertEqual(substrate.parse_date("2026-09-21 by Niels"),
                         datetime.date(2026, 9, 21))

    def test_parse_date_of_rubbish_is_none(self):
        self.assertIsNone(substrate.parse_date("soon"))
        self.assertIsNone(substrate.parse_date(""))

    def test_days_ago_counts_whole_days(self):
        self.assertEqual(substrate.days_ago("2026-09-14", "2026-09-21"), 7)
        self.assertEqual(substrate.days_ago("2026-09-21", datetime.date(2026, 9, 21)), 0)

    def test_days_ago_of_an_unparsable_date_is_none(self):
        self.assertIsNone(substrate.days_ago("", "2026-09-21"))
        self.assertIsNone(substrate.days_ago("2026-09-21", "never"))


class WorkspaceLayout(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for rel in ("customers/Acme/alpha", "customers/Acme/beta", "customers/Beta/gamma",
                    "own/tooling"):
            d = os.path.join(self.tmp, *rel.split("/"))
            os.makedirs(d)
            with open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8") as f:
                f.write("## Identity\nstatus: active\n")
        # a folder with no CLAUDE.md is not a project
        os.makedirs(os.path.join(self.tmp, "customers", "Acme", "notes"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_customer_dirs_lists_the_clients(self):
        self.assertEqual([n for n, _ in workspace.customer_dirs(self.tmp)], ["Acme", "Beta"])

    def test_project_dirs_finds_every_project_and_skips_a_plain_folder(self):
        keys = [k for k, _ in workspace.project_dirs(self.tmp)]
        self.assertEqual(keys, ["customers/Acme/alpha", "customers/Acme/beta",
                                "customers/Beta/gamma", "own/tooling"])

    def test_a_branch_narrows_the_walk(self):
        self.assertEqual([k for k, _ in workspace.project_dirs(self.tmp, "Acme")],
                         ["customers/Acme/alpha", "customers/Acme/beta"])
        self.assertEqual([k for k, _ in workspace.project_dirs(self.tmp, "own")],
                         ["own/tooling"])

    def test_the_workspace_root_is_not_a_project(self):
        self.assertNotIn("Dev", [k for k, _ in workspace.project_dirs(self.tmp)])

    def test_task_file_finds_a_task_and_reports_its_state(self):
        d = os.path.join(self.tmp, "ops", "tasks", "in-progress")
        os.makedirs(d)
        open(os.path.join(d, "a-task.md"), "w").close()
        self.assertEqual(workspace.task_file("a-task", root=self.tmp)[0], "in-progress")
        self.assertEqual(workspace.task_file("missing", root=self.tmp), (None, None))


class HeartbeatRecord(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, lines):
        with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as f:
            for o in lines:
                f.write(o if isinstance(o, str) else json.dumps(o))
                f.write("\n")

    def test_parse_ts_reads_the_hook_format(self):
        got = heartbeats.parse_ts("2026-06-22T06:14:03Z")
        self.assertEqual(got, datetime.datetime(2026, 6, 22, 6, 14, 3,
                                                tzinfo=datetime.timezone.utc))

    def test_parse_ts_treats_a_naive_timestamp_as_utc(self):
        self.assertEqual(heartbeats.parse_ts("2026-06-22T06:14:03").tzinfo,
                         datetime.timezone.utc)

    def test_parse_ts_of_rubbish_is_none(self):
        self.assertIsNone(heartbeats.parse_ts("not a time"))
        self.assertIsNone(heartbeats.parse_ts(""))

    def test_records_are_read_in_file_then_line_order(self):
        self._write("2026-09-15.jsonl", [
            {"ts_start": "2026-09-15T08:00:00Z", "ts_end": "2026-09-15T08:30:00Z",
             "project": "customers/A/p", "session": "sess-2"}])
        self._write("2026-09-14.jsonl", [
            {"ts_start": "2026-09-14T08:00:00Z", "ts_end": "2026-09-14T08:30:00Z",
             "project": "customers/A/p", "session": "sess-1"}])
        got = heartbeats.records(self.tmp)
        self.assertEqual([r["session"] for r in got], ["sess-1", "sess-2"])

    def test_a_missing_project_becomes_the_workspace_bucket(self):
        self._write("d.jsonl", [{"ts_start": "2026-09-14T08:00:00Z",
                                 "ts_end": "2026-09-14T08:30:00Z"}])
        self.assertEqual(heartbeats.records(self.tmp)[0]["project"], "Dev")

    def test_an_end_before_its_start_is_clamped(self):
        self._write("d.jsonl", [{"ts_start": "2026-09-14T09:00:00Z",
                                 "ts_end": "2026-09-14T08:00:00Z"}])
        r = heartbeats.records(self.tmp)[0]
        self.assertEqual(r["start"], r["end"])

    def test_unparsable_and_blank_lines_are_skipped_not_fatal(self):
        self._write("d.jsonl", ["", "{not json", "{}",
                                {"ts_start": "2026-09-14T08:00:00Z",
                                 "ts_end": "2026-09-14T08:30:00Z"}])
        self.assertEqual(len(heartbeats.records(self.tmp)), 1)

    def test_a_missing_directory_reads_as_empty(self):
        self.assertEqual(heartbeats.records(os.path.join(self.tmp, "nope")), [])

    def test_nothing_is_bounded_or_split_here(self):
        # a 9 hour span crossing local midnight comes back whole
        self._write("d.jsonl", [{"ts_start": "2026-09-14T20:00:00Z",
                                 "ts_end": "2026-09-15T05:00:00Z"}])
        r = heartbeats.records(self.tmp)
        self.assertEqual(len(r), 1)
        self.assertEqual((r[0]["end"] - r[0]["start"]).total_seconds() / 3600.0, 9.0)


class SinglePromptSessions(unittest.TestCase):
    """Owner rule 2026-09-28: one prompt and closed is not work; two prompts is."""

    T = datetime.datetime(2026, 9, 28, 8, 0, tzinfo=datetime.timezone.utc)

    def rec(self, session, start_min, end_min):
        m = datetime.timedelta(minutes=1)
        return {"start": self.T + start_min * m, "end": self.T + end_min * m,
                "project": "customers/A/p", "task": None, "session": session}

    def kept(self, recs):
        return sorted({r["session"] for r in heartbeats.without_single_prompt(recs)})

    def test_one_prompt_is_dropped(self):
        self.assertEqual(self.kept([self.rec("aaaa1111", 0, 20)]), [])

    def test_two_prompts_are_work(self):
        self.assertEqual(self.kept([self.rec("aaaa1111", 0, 2), self.rec("aaaa1111", 5, 6)]),
                         ["aaaa1111"])

    def test_a_turn_that_stops_twice_is_still_one_prompt(self):
        self.assertEqual(self.kept([self.rec("aaaa1111", 0, 2), self.rec("aaaa1111", 0, 9)]), [])

    def test_a_point_heartbeat_is_not_a_prompt(self):
        # a `!` bash-input or a late background notification after the only prompt
        self.assertEqual(self.kept([self.rec("aaaa1111", 0, 20), self.rec("aaaa1111", 90, 90)]),
                         [])

    def test_a_resumed_session_counts_its_prompts_across_days(self):
        self.assertEqual(self.kept([self.rec("aaaa1111", 0, 2),
                                    self.rec("aaaa1111", 24 * 60, 24 * 60 + 3)]), ["aaaa1111"])

    def test_sessions_are_judged_one_by_one(self):
        recs = [self.rec("aaaa1111", 0, 2), self.rec("bbbb2222", 0, 2), self.rec("bbbb2222", 4, 6)]
        self.assertEqual(self.kept(recs), ["bbbb2222"])


if __name__ == "__main__":
    unittest.main()
