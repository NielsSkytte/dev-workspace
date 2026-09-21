# dashboard.py — architecture review

**Question asked (2026-09-21):** Some elements have grown a lot like dashboard.py — have they been
developed using best practice? Is this the best approach for a system like this and what it is
evolving into?

---

## Verdict

The architecture is appropriate for what this is: a personal ops server with zero external
dependencies, derive-only access to the workspace substrate, and no install friction. The stdlib +
`ThreadingHTTPServer` choice is correct and should stay. The design principles (pure stdlib,
ASCII-safe, Guardrail 7 compliant) are sound.

The file has grown into three distinct concerns that are now tangled, and one specific area has a
latent correctness risk.

---

## What is solid

- **stdlib + `ThreadingHTTPServer`** — right call for an internal tool. No pip, no venv, just runs.
- **Derive-only philosophy** — Guardrail 7 is respected: delete the file and no knowledge is lost.
- **`rollup` and `daybrief` loaded via `importlib.util`** — unusual but deliberate. Avoids circular
  imports between sibling scripts. Works reliably.
- **`today.html` on its own endpoint** (`/api/today`) — the daybrief is already separated from the
  heavy `collect()` call. Good precedent.

---

## What is showing strain

### 1. `collect()` re-reads everything on every request (lines 908–1036)

Every `/api/data` load re-reads every task file, every CLAUDE.md and CONTEXT.md, every heartbeat,
re-parses the XLSX, and recomputes the full time audit. That is ~50–100 file reads per request now
and grows linearly with the workspace. Hitting Refresh on the overview page triggers a full
workspace walk each time.

**Fix:** 30-second TTL in-process cache on `collect()`. Zero architecture change, eliminates
repeated full walks between user interactions.

### 2. `_apply_fm` via regex (lines 1163–1178) — latent correctness risk

YAML frontmatter editing by regex works for single-line scalar values but will silently corrupt a
file that contains a multi-line value or a value with a bare `:` in it. Task files are currently
simple enough that this has not bitten, but it is a live hazard on every task mutation.

**Fix:** Proper round-trip — parse frontmatter into a dict, merge updates, serialize back. Still
stdlib, no pyyaml. About 20 lines to replace the current regex approach.

### 3. `do_POST` route matching via `startswith` (lines 1309–1312)

Works at 3 routes (`/api/launch`, `/api/reassign`, `/api/task`). Will become a maintenance problem
at 6+. A routing dict would handle it in 3 lines.

**Priority:** Low — note for next time a new route is added.

### 4. Three separate modules in one file

The file contains three independent layers that have grown together:

| Lines | What it is |
|---|---|
| 68–183 | Pure text/markdown utilities (`read`, `parse_frontmatter`, `sections`, `bullets`, `plain`, `field`, `first_para`, `iso_days_ago`) |
| 188–1036 | Data collection layer (`discover`, `collect_tasks`, `collect_time`, `collect_audit`, `collect_entry`, `collect_internal`, `memory_index`, …) |
| 1039–1358 | Server, process launcher, write paths (`Handler`, `serve`, `launch`, `reassign_dev`, `task_mutate`) |

None of these depend on each other at import time. Splitting into `dashboard_data.py` (layers 1+2)
and `dashboard.py` (layer 3, server only) would halve the file without changing the architecture or
the deploy model.

**Priority:** Medium — do it the next time a significant block is added to the data layer.

---

## Priority order

| # | Finding | Risk | Effort |
|---|---|---|---|
| 1 | `_apply_fm` regex frontmatter editor | Correctness — silent data corruption | ~20 lines |
| 2 | `collect()` no caching | Performance — full workspace walk per request | ~10 lines |
| 3 | Module split | Readability / maintainability | Refactor, no logic change |
| 4 | `do_POST` routing table | Maintainability | ~5 lines, next route addition |

---

## What was NOT found

- No security issues (localhost-only, no auth surface needed).
- No resource leaks (files opened with `with`, no persistent handles).
- The XLSX parsing via stdlib `zipfile` + `ElementTree` is unconventional but correct and has no
  dependency.
- `ThreadingHTTPServer` handles concurrent requests correctly; no shared mutable state outside
  the single `collect()` call.

---

# System-level: `ops/` as a whole (2026-09-21)

Scope of this section: the question was broader than one file. 5,265 lines of Python across
`ops/` (4,128) and `.claude/hooks/` (1,137).

## Verdict

The architecture choice is right and should stay: stdlib-only, file substrate, derive-only,
no install step. Nothing here argues for a framework, a database, or a package.

Two gaps are real, and both are consequences of the same thing — the scripts were each written
as a standalone tool, and there is now no shared layer underneath them.

## 1. No tests — anywhere in `ops/`

`find` over `C:\Dev` returns test files only under `customers/*` and `own/MetaAtomic`. There is
no test for any of the 5,265 lines in `ops/` + `.claude/hooks/`.

What that code does: `time/rollup.py` computes billable hours (the 15+5 model, the full-day
floor, the week cap), `time/value.py` scores and caps them, and `/fno` registers the result into
Dynamics 365 F&O. `dashboard.py` mutates task frontmatter in place.

So the untested code is the code that produces invoiced numbers and edits the substrate. The
customer projects are tested; the money path is not.

**Fix:** a `ops/tests/` with stdlib `unittest`, covering the arithmetic only — `stretch_hours`,
`distribute_hours`, `weighted_hours`, `consolidate_week`, `spill_over_cap`, `apply_caps`, and
`_apply_fm` round-trip. Pure functions, fixture in, number out. No server, no filesystem walk.
Perhaps 200 lines to cover every rule that has a number in it.

## 2. The substrate readers are reimplemented 3-4 times each

| Concern | Independent implementations |
|---|---|
| YAML frontmatter | `dashboard.py:90`, `bin/daybrief.py:72`, `time/rollup.py:193` |
| Heartbeat loading | `dashboard.py:653`, `time/rollup.py:99`, `time/value.py:281` |
| Project / customer resolution | `dashboard.py:188`, `bin/daybrief.py:211`, `time/rollup.py:412`, `time/value.py:182` |
| Markdown sections / bullets | `dashboard.py:102,118`, `bin/daybrief.py:85,107` |

Consequence: a change to the substrate format — a new task frontmatter key, a heartbeat field, a
project layout — needs three or four edits in three or four files, and a missed one fails
silently, because every reader is tolerant by design.

## 3. What the system is actually evolving into

It is no longer a dashboard plus some scripts. It is **one workspace data model with five
renderers**: the HTTP overview, the day brief text, the project resume cards, the timesheet, and
the F&O export. The model is implicit — it exists only as the same parsing logic repeated in
each renderer.

The shape that fits is a thin read layer, still stdlib, still derive-only:

```
ops/lib/substrate.py   frontmatter, sections, bullets, fields, dates
ops/lib/workspace.py   discover projects, customers, tasks, cards
ops/lib/heartbeats.py  load, group, split by local day
```

`dashboard.py`, `daybrief.py`, `rollup.py` and `value.py` then become what they already are in
intent: renderers over a shared model. This also delivers the module split proposed above for
`dashboard.py` as a side effect, and it makes the tests in item 1 possible to write once rather
than per script.

It does not change the deploy model, add a dependency, or violate Guardrail 7 — `ops/lib/`
derives, it stores nothing.

## 4. `dashboard.html` — noted, not urgent

2,101 lines, of which 1,685 are inline JavaScript, 273 CSS. 38 `innerHTML` assignment sites, 3
`fetch` calls. Hand-rolled rendering in a single file with no component boundary. It works and it
has no dependency, which is worth a lot. It is the next thing to hurt after the Python, not
before it.

## 5. Growth trajectory

`dashboard.py` by commit date: 540 (2026-07-28), 645 (08-01), 844 (08-03), 1,020 (08-20), 1,215
(09-01), 1,234 (09-16), 1,357 (working tree). Linear, no inflection. Inference, not fact: nothing
in the current structure creates a natural stopping point, so the file keeps absorbing whatever
is added next.

## Revised priority order

| # | Finding | Risk | Effort |
|---|---|---|---|
| 1 | No tests on the billing arithmetic | Money — a silent regression reaches an invoice | ~200 lines |
| 2 | `_apply_fm` regex frontmatter editor | Correctness — silent file corruption | ~20 lines |
| 3 | `ops/lib/` shared read layer | Substrate changes need 3-4 edits, misses are silent | Refactor, no logic change |
| 4 | `collect()` no caching | Performance | ~10 lines |
| 5 | `dashboard.html` structure | Maintainability | Later |

---

# Status 2026-09-21

| # | Finding | State |
|---|---|---|
| 1 | No tests on the billing arithmetic | done - `ops/tests/`, 131 tests |
| 2 | `_apply_fm` regex frontmatter editor | done - literal line replacement |
| 3 | `ops/lib/` shared read layer | done - `substrate`, `workspace`, `heartbeats` |
| 4 | `collect()` no caching | open |
| 5 | `dashboard.html` structure | open |

## What the read layer changed

`ops/lib/` (441 lines) holds the substrate parsers, project discovery and the raw heartbeat
reader. `dashboard.py`, `bin/daybrief.py`, `time/rollup.py` and `time/value.py` import them and
no longer carry their own copies; `dashboard.py` went from 1,357 to 1,248 lines.

The two customer-resolution functions that were silently different are now named for what they
answer and sit side by side: `billing_entity` returns `customers/<client>` for everything (the
timesheet needs a grouping key for every project) and `customer_name` returns the bare name or
None (the value model uses the None to decide whether the customer cap applies at all).

Behaviour is unchanged, verified rather than assumed: every rollup and value report was run
against a copy of the pre-refactor script at the same moment and is byte-identical, the day
brief is byte-identical across all five of its modes, and the dashboard payload differs only in
`generated` and the `idle_min` of live sessions.

## Still duplicated, deliberately left

`.claude/hooks/track_time.py` carries a third `customer_of` and its own `project_from_cwd`.
They are not the same question: the hooks resolve "where is this session" from a cwd, including
the customer-node case (`customers/<client>` with no project selected), and `customer_of` there
returns a lowercased name used as a matching key. Folding them into `lib/` would change the time
attribution on every turn, so it needs its own change with its own verification.
