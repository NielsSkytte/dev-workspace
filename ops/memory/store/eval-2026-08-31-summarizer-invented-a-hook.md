---
id: eval-2026-08-31-summarizer-invented-a-hook
ts: 2026-08-31T10:30:00Z
type: evaluative
scope: workspace
source: session:7ee7dd73
tags: [workspace, memory, sentinel, capture, summarizer, defect]
status: distilled
description: "The local summarizer asserted a PreCompact hook that was never added - the fifth consecutive fabricated completion - and sentinel traced the systemic cause to non-user turns being captured as User lines"
---

Sentinel vetted `daily/2026-08-31.md` (15 records) at `/log` and returned **9 flags: 5 safe as-is,
3 drop, 5 re-summarize, 8 user-line truncations.** None of the flagged records were distilled.

**The fabrication, fifth consecutive occurrence.** `daily/2026-08-31.md:94` asserts the session
"added a `PreCompact` hook" to settings.json. No `PreCompact` key exists in either settings file,
and nothing in the session went near one. The open TODO from 2026-08-03 recorded this as the
**fourth** consecutive `/log` with an invented completed action ("Entered internal time for July
2026" on a turn that entered nothing). The pattern is stable: the summarizer converts *subject
matter discussed* into *action performed*. Per-day vetting catches it, so nothing has reached the
store - but the sentinel gate is now the only thing standing between this and the snapshot.

**The systemic cause is upstream of the summarizer.** Sentinel traced most flags to turns that are
not user messages being captured as `User` lines:

- `:81-92` - the **expanded body of the `update-config` skill**, complete with directive lines like
  `"Before compacting, ask me what to preserve" -> PreCompact hook`. That is where the invented
  PreCompact hook came from: the summarizer read the skill's own example and reported it as done.
  README rule 4 says a command turn is recorded as its bare invocation, never expanded help text.
  This is the same defect as the open 2026-07-23 TODO and `eval-fabric-deployment-skill-missed-valueset-trigger`.
- `:124-130` and seven more - raw `<task-notification>` harness markup, each truncated mid-element
  so the tags open and never close, and each embedding an absolute temp path with a session GUID.

**Fixed this session:** `<task-notification` and `<local-command-stdout` added to
`_INJECTION_MARKERS` in `capture_turn.py`. The skill-help case is **not** fixed - the expanded
prompt does not carry `<command-name>`, so the existing detection misses it, and that remains the
open 2026-07-23 TODO.

**Two lessons.** Unbalanced harness markup in a record is not cosmetic: `daily/` feeds the snapshot,
so an unclosed `<task-notification>` is instruction-shaped text heading back into a prompt. And a
fabrication with a plausible mechanism is the dangerous kind - "added a PreCompact hook" is exactly
what a reader would expect from a session that invoked `update-config`, which is why only checking
it against the substrate caught it.
