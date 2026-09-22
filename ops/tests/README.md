# ops/tests

Tests for the `ops/` arithmetic that reaches an invoice or edits the substrate.

```
python -m unittest discover -s tests -t tests      # from C:\Dev\ops
```

Pure stdlib `unittest`, no server and no walk of the real workspace. A write path is tested
against a file it makes in a temp directory and throws away; nothing here touches `C:\Dev`. The
scripts under test are CLI tools rather than a package, so `_bootstrap.py` puts `ops/`,
`ops/time/` and `ops/bin/` on `sys.path`; none of them do work at import time.

| File | Covers |
|---|---|
| `test_rollup.py` | `time/rollup.py` - the 15+5 model, quarter rounding, the top-up distribution, week merge and the day cap |
| `test_value.py` | `time/value.py` - tiering, stretch grouping, the customer cap and the review flags |
| `test_frontmatter.py` | `dashboard.py` `_apply_fm` - the task-file write path |
| `test_lib.py` | `lib/` - the shared read layer: substrate parsing, project discovery, the heartbeat record |
| `test_dashboard.py` | the `ops/TODO.md` write path, the project band rule, the payload memos, the POST routing table |
| `test_fno.py` | `lib/fno.py` and the F&O entry surface - the readiness rule, the write paths (correct a line, split one between its sessions), the workbook |
| `test_lines.py` | `lib/lines.py` - the line-description file: its key, its round-trip, and a tolerant read |
| `test_audit.py` | `dashboard.line_rows` - the three-way join behind a week's F&O lines, and that every measured hour lands on exactly one of them |
| `test_attribution.py` | `lib/attribution.py` - whether a turn is about to produce a line that cannot be entered, and staying quiet when it is not |
| `test_fnotasks.py` | `lib/fnotasks.py` - what an F&O task id is called, and that the name never reaches a line |
| `test_noinvoice.py` | `lib/noinvoice.py` - the not-invoiced register, and that the rollup and the entry page both honour it |
| `test_reassign.py` | moving a line off the invoice, marking one not for registration, and the directions that are refused |
| `test_sessionlines.py` | `lib/sessionlines.py` - which line a session's time was split onto, and that the evidence follows the split |

Scope is deliberate: a documented rule and a number, or a write that has to leave a hand-maintained
file intact. Rendering and the HTTP layer are not covered here - the pages are checked under jsdom
against a running server, and a write path is driven end to end against a throwaway workspace.

Every write path is held to one standard: it changes the line it names and leaves every other byte
alone - indentation, inline comments, line endings, and whatever prose the file already carried.

Two invariants carry most of the weight, because they are what an invoice depends on:

- hours are **moved, never invented or lost** (`consolidate_week`, `spill_over_cap`, `apply_caps`)
- no customer-day exceeds the cap while the period still has room, and a period with no room
  leaves the hours where they were measured rather than dropping them
