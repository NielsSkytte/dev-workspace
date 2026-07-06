# Memory — DEV Workspace

The workspace's memory substrate: plain markdown, git-tracked, tool-neutral. **Any LLM pointed
at this folder can run the whole system by reading this file.** The Claude harness (the
`SessionStart` snapshot hook, the per-turn capture hook, the `/log` and `/recall` commands) only
*accelerates* what is described here — delete the harness and the capability remains (Guardrail 7).

```
ops/memory/
  README.md            # this file — the spec + by-hand recipes
  daily/YYYY-MM-DD.md  # STORAGE tier 1 — raw stream, one record per turn (Stop hook, or by hand)
  store/*.md           # STORAGE tier 2 — distilled, curated records (durable knowledge)
  store/MEMORY.md      # human index of the store (rebuildable from frontmatter)
```

## The model — Storage / Injection / Recall + Evaluation

Memory does four jobs (Simon Scrapes' Storage/Injection/Recall framing, plus an evaluative layer):

1. **STORAGE** — capture what happens, two tiers: raw per-turn records in `daily/`, distilled
   keepers in `store/`. Raw->distilled mirrors the workspace's TODO->tasks pattern.
2. **INJECTION** — at session start, a **capped (~1.3k token) snapshot** of identity + behavioral
   preferences + the most relevant recent `store/` records + open work is surfaced. The
   `SessionStart` hook emits it; native Claude auto-memory is **disabled** so this is the *only*
   injection path.
3. **RECALL** — search `store/` + `daily/` by keyword; every answer **cites its source file**, and
   says so plainly when nothing matches (a confident answer with no source is worse than useless).
4. **EVALUATION** — skill observations (a skill that *should have fired and didn't*, or fired
   unhelpfully) are records with `type: evaluative`; periodically distilled into concrete skill edits.

## The record shape — one shape, markdown now, DB row later

Every record (daily or store) carries this frontmatter:

```yaml
---
id:            # stable slug (primary key)
ts:            # ISO 8601
type:          # episodic | semantic | procedural | evaluative
scope:         # workspace | project:<path> | client:<name>
source:        # turn-hook | session:<id> | manual | /log | distilled
tags: []       # freeform keywords (recall surface; future row-level-security tag)
status:        # raw | distilled | superseded
---
body markdown
```

- **type** — `episodic` = what happened; `semantic` = durable facts/conventions/preferences;
  `procedural` = how-to; `evaluative` = judgments about our own tools (skills).
- **scope** — `workspace` today. `project:`/`client:` scoping is what makes a future team
  "company brain" (row-level security, per `memory-arch-three-jobs`) a tag-and-filter, not a
  re-architecture. Present from day one.
- **source** — keeps provenance citable (the Recall "cite or admit" rule).
- **status** — `raw` (just captured) -> `distilled` (curated into `store/`) -> `superseded`.
- Store records also carry a `description:` (one-line gist) used by the index and recall.

This shape **is a database row** (id = PK; scope/tags/status = columns). When scale demands it, a
SQLite index (FTS first, vectors later) can be built FROM these files and rebuilt/thrown away at
will — it never becomes the source of truth. Semantic search is deferred until a *logged*
recall-miss proves keyword is insufficient.

## By-hand recipes — the capability the harness accelerates

**STORAGE / capture.** Append a record to today's `daily/<date>.md`. The `Stop` hook writes one
per turn automatically (`status: raw`, `source: turn-hook`) - keyed by (date, session, user
message), so repeated `Stop` firings within one turn **replace** that turn's record in place
rather than piling up duplicates. The assistant body is summarized by a **tiny local Ollama
model** (`MEMORY_SUMMARY_MODEL`, default `qwen3:1.7b`, zero cost / fully local); if Ollama is
unreachable it falls back to a deterministic truncated extract. By hand, write a record in the
shape above with `source: manual`.

**STORAGE / distill.** When a raw daily record is worth keeping, copy it into `store/<id>.md`
(`status: distilled`), refine the body, and add a line to `store/MEMORY.md`. `/log` does this for
the day at session end; by hand, review the day's `daily/` file and promote keepers.

**INJECTION / snapshot.** At session start, surface: identity + behavioral preferences (store
records tagged `user` / `feedback`) + the most relevant/recent store records + open work (in-progress
and open tasks, unchecked TODOs). Keep it capped (~1.3k tokens). The `SessionStart` hook emits this
to stdout; by hand, read `store/MEMORY.md` and the latest `daily/` entry.

**RECALL / search.** Grep `store/` then `daily/` for the query terms and `tags`. Return matches
**with their `source`/path**. If nothing matches, say so — never invent. (Future: a rebuildable
keyword/vector index; unnecessary at the current scale.)

**EVALUATION / skill review.** When a skill should have fired and didn't, or fired unhelpfully,
write an evaluative record (`type: evaluative`, tag the skill name). Periodically (e.g. via
`/update-skills`) group evaluative records by skill; N consistent observations -> a concrete skill
edit. See `store/skill-usage-evaluation.md`.

## Output validation — local-model output is untrusted input (decided 2026-07-06)

Memory records **feed future prompts** (snapshot injection, recall, distillation), so anything a
local model writes into them is a potential injection path into later sessions. Every summary from
the local summarizer is therefore validated **deterministically, per turn**, before it is written
(`capture_turn.py > sanitize_summary`). On any violation the summary is rejected and the record
falls back to a truncated verbatim extract (quoted session content, not novel model text).

The rules (the hook is the dumb executor; this list is the source of truth):
1. **Charset**: printable ASCII + Latin-1 letters (Danish covered) + en/em dash, curly quotes,
   ellipsis, nbsp. Any other script or control character -> reject. (Observed once 2026-07-06:
   `qwen3:1.7b` mixed a Chinese phrase into an otherwise-correct summary, `daily/2026-07-06.md`.)
2. **Injection markers**: instruction-like text ("ignore previous instructions", "you are now",
   `<system-reminder`, `<command-name`, "new instructions:") -> reject.
3. **Bounds**: empty or > 600 chars -> reject.
4. **Command turns** are recorded as the invocation (`/todo <args>`), never the command's expanded
   help text (that was the main daily-stream noise source pre-2026-07-06).

**Second layer — the `sentinel` agent** reviews the day's daily file at `/log` (before distillation)
and any other locally-generated LLM output on demand: language violations the charset rule can't
judge, instruction-like phrasing that dodges the marker list, summaries that contradict their turn,
anything odd however small. Verdicts are file+line specific; suspect records are re-summarized or
truncated, never distilled as-is. **By hand:** grep `daily/` for non-Latin characters and the
marker list above, and read the day's records before promoting any of them to `store/`.

## No duplicate functionality — how this relates to the rest of `ops/`

- `ops/TODO.md` (actions) and `ops/tasks/` (work-state) are **not** memory — untouched.
- `ops/log/sessions.md` stays the human session **narrative** (ICOR Refine); `/log` distills the
  day's `daily/` records into it and into `store/`. daily = atomic records; sessions.md = prose digest.
- Project `CONTEXT.md` / `INBOX.md` are project-scoped — untouched.
- `AGENTS.md` > Conventions stays **canonical** for operating conventions; store records
  cross-reference it rather than restating it.
- Claude's native auto-memory (`~/.claude/.../memory/`) is **disabled** (`autoMemoryEnabled: false`)
  so there is exactly one memory home: this folder. (The disable stops auto-memory's autonomous
  *writes* — the real collision — but not its ~11-16k-token system-prompt preamble, an open Claude
  Code bug #63903; see `store/claude-auto-memory-disable.md`.)
