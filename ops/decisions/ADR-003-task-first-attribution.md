# ADR-003: Task-First Time Attribution

| Field       | Value                        |
|-------------|------------------------------|
| Status      | Accepted                     |
| Date        | 2026-07-28                   |
| Author      | Niels                        |
| Reviewers   | -                            |

Amends ADR-002 (*Per-Project Time Tracking*), which decided attribution by working directory.

---

## Context

ADR-002 set **attribution by the session's working directory**: the project is the folder the
session is rooted in, and a tagged task only *added* Activity/Task dimensions beneath it — a task
whose `project:` disagreed with the cwd was discarded as a stale or foreign tag.

That rule assumes one project == one folder. Carl Ras broke it in both directions at once, and the
break is structural rather than a one-off:

- **One project, several repos.** The Datahub implementation spans `Landingzone-ETL` and
  `Fabric-ETL` — two repos under the customer's single Azure DevOps project `Datahub`. They had been
  scaffolded as two workspace projects (`Carl-Ras/datahub`, `Carl-Ras/fabric`) purely because each
  held a repo. Both already carried `fno_code: 230-02`, i.e. they were never two billing units.
- **One repo, several tasks.** `Fabric-ETL` alone hosts the GTM inbound ingest, the capacity
  scale-up, and CapacityManager — distinct workstreams, each its own user story.

Under cwd-first attribution neither is expressible: the folder names the *code*, not the *work*.

Two further observations shaped the decision:

- **Forgetting the tag was cheap, and that is why nothing forced it.** Under ADR-002 an untagged
  session still produced the right Project ID; only the Activity/Task dimensions were blank. The
  cost was granularity, not correctness — so a rule that merely *instructed* the assistant to ask
  (the `CLAUDE.md` project walk) was routinely skipped with no visible consequence.
- **The marker had no owner.** `ops/time/active-task` held a bare slug with no session or
  timestamp, so it persisted indefinitely. It was safe only *because* cwd outranked it: the
  project-match guard discarded anything foreign. Remove cwd's primacy and that protection
  disappears with it.

## Decision

**The active task decides the project; the working directory is the fallback.** Per turn:

1. Active task set and passing both guards -> its `project:` is the project; heartbeat carries the tag.
2. Otherwise -> `project_from_cwd(...)`, no tag.

Two guards make the inversion safe. Both are load-bearing:

- **Same-customer cap.** A task may override cwd only within the same customer. A customer node
  (`customers/<Client>`) *is* overridden by a task on one of its projects — that is how node-level
  `UNSET` time resolves itself. **`Dev` and `own/…` are never overridden.** Re-attributing workspace
  time onto a customer is the direction that over-bills; it stays a deliberate judgement at the
  daily review gate, where ADR-002's `Dev` -> project override already lives.
- **Per-session marker.** `active-task` becomes
  `{"sessions": {<session-id>: {slug, set_at}}, "unclaimed": {slug, set_at}|null}`. A session reads
  only its own entry, so a task set in another session — earlier *or concurrent* — never applies.
  Slash commands, which cannot know the session id, write to `unclaimed`; the next turn adopts it
  only if the task passes the same-customer test. Entries older than 7 days are pruned on write.
  Legacy formats (the single record, a bare slug) are still read.

  > **Corrected 2026-07-28, same day.** This first shipped as a single shared record
  > `{slug, session, set_at}` where a session owning the marker caused any *newly opened* session to
  > clear it. That silently dropped the first session's tag whenever a second was opened — a real
  > failure for this workspace, where concurrent sessions on different projects are normal. Verified
  > by test before and after. The same-customer cap contained the damage to lost granularity (and,
  > for two sessions on one customer, a wrong task within that customer) — it never crossed
  > customers. Session-scoping the marker was right; making it a *single* record was not.

**Setting the task stops being a ritual.** A `SessionStart` hook (`.claude/hooks/session_task.py`)
resolves it deterministically: exactly one open task on the project -> set it and announce it;
several -> surface the list so the first reply asks; none -> offer to create one *or* to track at
project level. This is a hook rather than an instruction because instructions are exactly what got
skipped — the file write does not depend on model compliance.

**Forgetting to end a session is handled by a nudge, not machinery.** The same hook reports days
with tracked time whose `/log` never ran, for every workspace session. This is deliberately only a
reminder: leaving sessions open costs **nothing** in hours (the 15+5 model discards idle gaps,
ADR-002) and `rollup.py` already finalizes missed days in bulk at the next `/log`. What genuinely
decays is `CONTEXT.md` handoff and memory distillation, and neither can be reconstructed after the
fact — so the only honest remedy is to prompt while the conversation still exists.

**Task granularity is the user story / Azure DevOps work item** — what `fno_task:` points at.
Sub-steps of a story ("create the datastore", "type-2 history", "build the semantic model") are
deliberately not modelled: F&O has no dimension below Task, so modelling them would produce detail
nothing can receive. A task need not be finishable in one sitting; the tag is stamped **per turn**,
so `/switch-task` mid-session splits time exactly where the switch happened.

**A repo is not a project.** A project is one F&O Project ID; if two folders bill to the same ID
they are one project, and repos live inside it. Applied 2026-07-28: `Carl-Ras/fabric` merged into
`Carl-Ras/datahub`, both repos beneath it, the scale-up demoted from project to task.

### Substrate vs harness

Unchanged from ADR-002. The rules live in `ops/time/README.md` §2 and the data in `ops/time/`;
`track_time.py` and `session_task.py` are accelerators. Acid test still holds: with `.claude/`
deleted, the README's by-hand recipe still yields timesheets — the reader sets the task by editing
`active-task`, and the same-customer and ownership rules are stated there in prose.

## Consequences

### Positive
- One project can span many repos and one repo many tasks — the common shape of real delivery.
- Node-level `UNSET` time self-resolves whenever a task is active.
- Stale tags are structurally impossible, not merely unlikely.
- The unambiguous case (4 of 5 projects at time of writing had exactly one open task) needs no
  interaction at all.

### Negative / Risks
- **Mis-tagging now costs correctness, not just granularity.** A wrong task inside the right
  customer moves time between that customer's projects. Bounded by the same-customer cap, and the
  daily review gate remains the backstop.
- **More moving parts** — a second hook, and a marker format with a claim protocol. Both fail
  silent (exit 0) by design, so a breakage looks like untagged time rather than an error. The
  2026-07-28 `hooks-subdir-session-gap` incident is the precedent for how invisible that can be.
- **Registration is dual.** `session_task.py` must be registered in both `.claude/settings.json`
  and the user-level `~/.claude/settings.json` with byte-identical command strings, for the reasons
  in `README.md` §2. The workspace-root snapshot hook stays root-only by design.

## Alternatives Considered
- **A folder per task, repos as pure repo folders.** Rejected: task identity already lives in
  `ops/tasks/*.md`, so folders fork it into two places that drift; tasks needing no artifacts get
  folders anyway; and it answers "am I tracking correctly?" only at launch. The real requirement is
  continuous visibility, which belongs in the statusline, not the directory tree.
- **Block the prompt until a task is set.** Rejected: enforcement at the wrong severity. The
  failure it prevents is a coarser row, and it would fire on every `Dev` and `own/` session where
  task tracking does not apply.
- **Keep cwd first, mandate one folder per F&O code.** Rejected: it forces repos that belong to one
  project into one folder even when the customer's own repo layout says otherwise, and still cannot
  express several tasks inside one repo.

## Related
- ADR-002 — per-project time tracking (amended here).
- `ops/time/README.md` §2 — the operational rules and by-hand recipe.
- `AGENTS.md` > Time tracking — the tool-neutral routine.
