# The value model and the entry figure

Sections 1-3 of the skill measure **time**. This file derives the second number - **weighted
hours** - and keeps a **keyboard time** figure beside it, so any charge can be justified. It
changes no timesheet and invoices nothing automatically. Status: provisional, by design.

**Evidence source.** Heartbeats give attribution (project, task). The **session transcript** gives
duration and evidence: which tools ran, which files were written, how many lines. This is the one
part of the whole system that depends on a specific tool - under Claude Code the transcripts live
in `~/.claude/projects/**/*.jsonl`, and they are kept roughly **30 days**. The derived records in
`ops/time/value/` are therefore the durable copy and **must be backed up**. Another LLM would need
to emit an equivalent per-turn evidence stream.

## 1. Keyboard time (measured)

A turn runs from the user prompt to its **last production event** - an assistant message or a tool
result - bounded by *both* the transcript and the heartbeat. The transcript ends a turn whose end
hook never fired; the heartbeat bounds a turn whose segmentation broke on a resumed session. Both
cases are real: a 1-minute turn on 2026-08-03 recorded a 340-minute heartbeat, and a 131-minute
turn on 2026-07-23 contained 8.8 minutes of activity.

- **Within** a turn, each inter-event gap is capped at **5 minutes**. A pending permission prompt or
  a long-running tool call is not keyboard time.
- **Between** turns the cap is **15 minutes**, matching the rollup's idle timeout. A gap under 15
  minutes is the owner thinking and writing the next prompt; the timesheet already bills it, so the
  value ceiling must not discard it.

Raising the between-turns cap from 5 to 15 min on 2026-08-31 moved billable value time from 155.25
to 167.50 h (+7.9%) over the 25 days whose transcripts survived, and cut stretches from 421 to 243.
Keyboard time was unchanged. **Forward only** - existing records were not re-derived, because
transcripts before that point had aged out and a re-derive would have emptied those days.

## 2. Tiers (derived from tool evidence)

| Tier | Condition | Multiplier |
|---|---|---|
| T1 Junior Assistant | no tools, or <= 2 read-type calls | 2.0x |
| T2 Analyst | >= 3 reads, or a web/docs search, or a subagent spawn | 3.0x |
| T3 Consultant | state-changing execution, or a sub-20-line edit | 3.0x |
| T4 Senior Consultant | >= 20 weighted changed lines written | 6.0x |
| T5 Principal Consultant | **per stretch**: >= 600 weighted lines, or one new file >= 300 | 25.0x |

**The multipliers are judgement, not evidence.** T1-T4 are the owner's estimate of the
acceleration; T5 was fitted to one completed deliverable and is therefore exactly determined and
untested. **Do not cite the fit as validation.** Everything else here is derived and reproducible.

Weighted hours = sum over turns of `keyboard minutes x multiplier`, plus gaps (capped at 15 min)
and a 5-minute tail per stretch **at 1.0x**, then rounded to 0.25 h with the same 0.5 h floor as
the rollup.

## 3. Deliverable classes

The weight scales the **changed-line count** - which feeds the tier gates and the repeat-work call -
never the hours directly. Knowledge is denser per line than code.

| Class | Weight |
|---|---|
| `CONTEXT.md`, `README.md`, `CLAUDE.md`, `docs/`, `wiki/` | 2.00x |
| other `.md` | 1.50x |
| code, notebooks, anything else inside a project | 1.00x |
| `ops/memory/` | 0.50x |
| other `ops/` | 0.25x |
| `ops/tasks/`, `ops/time/`, `ops/memory/daily/` | 0.00x |

The zeroes are bookkeeping: those records are written by a hook, not by the engagement.

## 4. Repeat work

A ledger keyed by file path, rebuilt from scratch on every run so nothing persisted can drift:

| Weighted lines on a path already seen | Verdict |
|---|---|
| path not seen before | `new` |
| >= 150 | `rebuild` |
| >= 30 | `revision` |
| < 30 | `adjustment` - **tier drops one and nothing is credited** |

## 5. Caps

| Level | Threshold | Type |
|---|---|---|
| per **customer** per day | 12 h | hard - spills to another day, same customer, same month |
| all customers per day | 15 h | soft - review flag only, never moves hours |
| all customers per day | 24 h | hard - assertion |

A day over 9 h across *different* customers is fine: customers cannot see each other, so the only
cap that binds is the one on their own line. Spill is the weekly consolidation run backwards, plus
two guardrails: **never cross a month boundary** (it may be invoiced), and distance beats the
worked-day preference outside the week.

**The 15 h flag counts weighted hours, not clock hours.** It means "check the classifier", never
"you worked 15 hours."

## 6. The audit record

`value/<date>.md` is what you show when asked to justify a charge. Per F&O line: keyboard time,
turn and stretch counts, the tier table with multipliers, and every file touched with its line
count, kind and class. `value/<date>.jsonl` is the same data machine-readable.

Each project block also carries a one-line **`Focus:`** - the dominant files by share of weighted
lines, with two or more files from one directory collapsed into that directory. It answers "what
was this time actually for" without reading the whole deliverables table. It exists because that
question was only asked after a day had already been billed: 2026-08-04 charged a customer for a
stretch that was `describe.py 64%, ops/memory/store/ 28%` - capability development, not the
customer's deliverable. Corrected two days later.

> **Read `Focus:` as a prompt, not a verdict.** It is computed from file writes only, so a stretch
> of advice, analysis or review that wrote nothing contributes hours but no focus - and a line
> reading `ops/memory/store/ 100%` means those were the only *files written*, not that the whole
> line was bookkeeping. Use it to decide what to look at, then read the tier table and the
> transcript.

## 7. The entry figure, again

```
entry = work + (1 - e^-x) * (value - work)        x = turns/(10*work) + files/(8*work)
```

- rounded to 0.25 h, **floored at work time**, **capped at value time**
- 10 and 8 are p90 turn- and file-densities per work hour
- the block total is spread across the block's consolidated rows, so the rows sum to it exactly
- the month filter clips the whole page before anything is derived, splitting a straddling ISO week
  at the month boundary. An early version clipped only the entry blocks and leaked one month's
  hours into the next.

**It is computed in the entry page and nowhere else.** The command-line week and month reports give
work time. Quoting one as the other under-registers.

## 8. By hand

For each turn: note the active minutes, excluding any gap over 5 minutes; classify the turn against
the tier table using what it actually did; multiply; sum per project per day. Add the gaps under 15
minutes and a 5-minute tail per stretch at 1.0x. Round to 0.25 h with a 0.5 h floor.
