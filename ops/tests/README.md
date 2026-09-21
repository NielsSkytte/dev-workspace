# ops/tests

Tests for the `ops/` arithmetic that reaches an invoice or edits the substrate.

```
python -m unittest discover -s tests -t tests      # from C:\Dev\ops
```

Pure stdlib `unittest`, no fixtures on disk, no server, no workspace walk. The scripts under test
are CLI tools rather than a package, so `_bootstrap.py` puts `ops/`, `ops/time/` and `ops/bin/` on
`sys.path`; none of them do work at import time.

| File | Covers |
|---|---|
| `test_rollup.py` | `time/rollup.py` - the 15+5 model, quarter rounding, the top-up distribution, week merge and the day cap |
| `test_value.py` | `time/value.py` - tiering, stretch grouping, the customer cap and the review flags |
| `test_frontmatter.py` | `dashboard.py` `_apply_fm` - the task-file write path |
| `test_lib.py` | `lib/` - the shared read layer: substrate parsing, project discovery, the heartbeat record |

Scope is deliberate: pure functions with a documented rule and a number. Rendering, file discovery
and the HTTP layer are not covered, and a test that needs the real workspace does not belong here.

Two invariants carry most of the weight, because they are what an invoice depends on:

- hours are **moved, never invented or lost** (`consolidate_week`, `spill_over_cap`, `apply_caps`)
- no customer-day exceeds the cap while the period still has room, and a period with no room
  leaves the hours where they were measured rather than dropping them
