# ADR-004: Value-Based Billing (Keyboard Time + Weighted Hours)

| Field       | Value                        |
|-------------|------------------------------|
| Status      | Accepted, PROVISIONAL        |
| Date        | 2026-08-06                   |
| Author      | Niels                        |
| Reviewers   | -                            |

Extends ADR-002 (*Per-Project Time Tracking*) and ADR-003 (*Task-First Attribution*).
Neither is amended: attribution, the F&O dimensions and the timesheet are unchanged.
This ADR adds a **second number** alongside the hours, derived from the same substrate.

**Re-evaluate at the end of 2026-08.** The tier multipliers are not evidence-based
(see *What is derived and what is judgement*).

---

## Context

Time tracked under ADR-002 does not reflect what is delivered. Measured over
2026-07-07 to 2026-08-04 (23 working days, 579 turns, 98% matched to session transcripts):

- **13.8 h** of actual keyboard time on billable work produced **58.00 h** on the timesheet.
- The current model therefore already bills at **4.2x** measured production time, via idle
  gaps, the 5-minute tail buffer and the 0.5 h per-line floor. It does so blindly: no
  evidence, and no way to explain any individual number.
- The ElementLogic LineageDocumentation engine (14 Python modules, a T-SQL lineage parser,
  an 895-line TMDL parser, an HTML report generator, 3,018 lines in the first stretch alone)
  was built in **4.14 h of keyboard time across six days** and invoiced at **10.50 h**.
  Niels scopes the same deliverable at 60 h all-in, 40 h delivered so far.

Two defects in the existing capture were found while measuring, and both inflate today's
numbers independently of any value model:

1. **Phantom heartbeats.** The `Stop` hook does not always fire when a turn ends. On
   2026-08-03 a 1-minute turn recorded a 340-minute heartbeat because the hook fired only
   at the next prompt, 5.5 hours later. `ops/time/README.md` documented the
   many-heartbeats-per-turn case but not this one.
2. **Intra-turn dead time.** A 131-minute turn on 2026-07-23 contained **8.8 minutes** of
   activity: an 89.6-minute gap before a tool result (a pending permission prompt or a
   long-running call) and a 33-minute gap before the next assistant message. The
   between-turn idle rule cannot see gaps *inside* a turn.

## Decision

**Track two numbers per F&O line per day: keyboard hours (measured) and weighted hours
(derived).** The timesheet keeps owning what is invoiced; the value record is the evidence
for it.

### 1. Keyboard time is measured, not inferred

A turn runs from the user prompt to its last production event, **bounded by both the
transcript and the heartbeat**: the transcript ends a turn whose `Stop` never fired, the
heartbeat bounds a turn whose segmentation broke on a resumed session. Within a turn,
inter-event gaps are capped at 5 minutes, so dead time drops out. This is the same 5-minute
rule already used between turns, applied one level down.

Effect on the measured base: 3,052 raw heartbeat minutes become **1,245 active minutes**.

### 2. Five tiers, assigned from tool evidence

| Tier | Condition (per turn) | Multiplier |
|---|---|---|
| T1 Junior Assistant | no tools, or <=2 read-type calls | 2.0x |
| T2 Analyst | >=3 reads, or any web/docs search, or a subagent spawn | 3.0x |
| T3 Consultant | any state-changing execution, or a sub-20-line edit | 3.0x |
| T4 Senior Consultant | >=20 weighted changed lines written | 6.0x |
| T5 Principal Consultant | stretch total >=600 weighted lines, or one new file >=300 | 25.0x |

T5 is assigned per **stretch**, not per turn: building a subsystem does not fit in one turn.

The **file-count gate was dropped**. `files >= 8` fired twice in the measured month and was
wrong both times, catching many small config edits rather than a subsystem. Every genuine
T5 event was caught by the line or new-file gate alone.

### 3. Deliverable classes weight the line count

Knowledge is denser per line than code (Niels, 2026-08-05). Workspace bookkeeping is not a
customer deliverable. The weight scales the **changed-line count**, which feeds the tier
gates and the new/revision/adjustment call. It never scales hours directly.

| Class | Weight |
|---|---|
| `CONTEXT.md`, `README.md`, `CLAUDE.md`, `docs/`, `wiki/` | 2.00x |
| other `.md` | 1.50x |
| code, notebooks, everything else in a project | 1.00x |
| `ops/memory/` (curated records) | 0.50x |
| other `ops/` | 0.25x |
| `ops/tasks/`, `ops/time/` (bookkeeping) | 0.00x |
| `ops/memory/daily/` | 0.00x |

`ops/memory/daily/` is zero on fact, not judgement: those records are written by the local
Ollama summarizer in `capture_turn.py`, not produced by the engagement.

Before this rule, five of six "deliverables" on a Carl-Ras row were the workspace's own
memory records, and an ElementLogic row billed 0.75 h for writing them.

### 4. Repeat work is demoted

A **deliverable ledger** keyed by path decides whether a turn is original work:

| Situation | Result |
|---|---|
| path not seen before | `new` - full tier |
| >=150 weighted lines on a seen path | `rebuild` - full tier |
| >=30 weighted lines on a seen path | `revision` - full tier |
| <30 weighted lines on a seen path | `adjustment` - **tier drops one, no credit** |

The ledger is rebuilt from scratch on every run. Nothing is persisted that could drift out
of sync with the heartbeats.

### 5. Three caps, only one of them hard

| Level | Threshold | Type | Action |
|---|---|---|---|
| per **customer** per day | 9 h | hard | spill to another day, same customer, same month |
| all customers per day | 15 h | soft | review flag; never moves hours |
| all customers per day | 24 h | hard | assertion |

A day above 9 h **across customers is not a problem** - customers cannot see each other.
The only view a customer has is their own line, so that is the only cap that binds.
Scoping the cap this way halved the amount of date-shifting: 14.50 h moved under a single
cross-customer cap, 7.75 h under the per-customer cap.

Spill is `consolidate_week` (`rollup.py:270`) run backwards, with two guardrails that the
existing function does not need: **never cross a month boundary** (a closed month may
already be invoiced) and **distance beats the worked-day preference** outside the week.
Without the second, hours moved 13 days backwards.

**The 15 h flag counts weighted hours, not clock hours.** A flagged day may be 4 h at the
keyboard. It means "the classifier produced an implausible number, check it" - never "you
worked 15 hours."

### 6. T5 stays T&M

T5 work is **not** fixed price and is **not** removed from the hourly track. A T5 event is
evidence that a subsystem was built; it is not itself a deliverable. Measured: 8 genuine T5
events in the month mapped to **6 deliverables**, and the lineage engine alone accounted for
three of them. Pricing per event would bill one deliverable three times.

A scope floor per deliverable was considered and **rejected for now** as machinery that the
multiplier already covers, and that would need a judgement call per deliverable per month.

## What is derived and what is judgement

This distinction is the reason the ADR is marked PROVISIONAL.

**Derived from the transcript, reproducible, defensible:**
keyboard time; turn and stretch boundaries; tier assignment; changed-line counts;
deliverable classes; new/revision/adjustment; T5 event detection; caps and spill;
the audit record.

**Judgement, not evidence:**

- **T1-T4 multipliers (2/3/3/6).** Niels's estimate of how much longer the same work would
  take without the setup. Never tested against an outcome.
- **T5 multiplier (25x).** Fitted to a single completed deliverable. The lineage engine is
  the only finished deliverable in the dataset; a sweep of 6/10/15/20/25/30 was run *after*
  Niels independently estimated 40 h, and 25x was selected because it produced 40.00 h.
  **One equation, one unknown - exactly solvable and untestable.** The agreement is not
  evidence and must not be cited as validation.

An out-of-sample check against Niels's other two anchors was inconclusive: Carl-Ras GTM
derived 5.27 h against a 40 h anchor (13%), Marketo 7.69 h against 40 h (19%). Both
deliverables are unfinished, so those ratios neither confirm nor refute the multiplier.

**Known gap:** high-value, low-line work reads too cheap. A 40-line DAX fix that unblocks a
go-live scores T4, not T5. Nothing in the current evidence model can see this.

Additionally, **14% of billable weighted hours sit in stretches that wrote no file at all** -
advisory and analysis work. It carries no deliverable evidence, so no part of the tier model
can validate it either.

## Consequences

- **Guardrail 7 tension, accepted.** The value model reads Claude Code session transcripts
  from `~/.claude/projects/`. That is a Claude-specific artifact outside `C:\Dev`, and it is
  not covered by the OneDrive mirror. Mitigation: `ops/time/value/` is the durable record
  and **must be added to the backup**; the transcript is only the input. Another tool would
  need to produce its own equivalent evidence stream. `ops/time/README.md` section 7 states
  the model tool-neutrally so it can be re-implemented; `rollup.py`, the timesheet and F&O
  entry remain entirely independent of this file.
- **Transcript retention is a dependency.** Only 2026-07-07 onward exists today. Claude Code
  may prune older sessions. Days derived before pruning keep their record; days not yet
  derived are lost.
- **The timesheet is unchanged.** `rollup.py` still owns `ops/time/timesheet/` and F&O entry.
  Nothing here changes what is invoiced until that decision is made separately.
- **Nothing is auto-invoiced.** The value record is evidence for a conversation, not an
  instruction to bill.

Measured effect for 2026-07-07 to 2026-08-04, billable: **13.82 h keyboard, 58.00 h under
the current model, 115.25 h under this one** (8.3x keyboard, 1.99x the current model).

## Evaluation plan

Run both models through **2026-08** and compare at month end:

1. Does the effective factor stay near 8x, or does it drift with the type of work?
2. Do GTM or Marketo complete? Either gives the first genuine out-of-sample test of T5.
3. How often does the 15 h flag fire, and is it right when it does?
4. Where does the derived number disagree with Niels's gut? Record each instance at `/log` -
   that log is the evidence base for whether a scope floor is needed after all.

---

## Amendment 2026-08-14 — the timesheet is the floor, and the open commercial question

### Decided: the timesheet is always the floor

**Whatever the model says, the billed hours are never below the timesheet.** Keyboard time is an
input to the value model and is never a billing basis on its own.

Worked example that prompted this (Carl Ras, 2026-08-11/12/13):

| measure | hours | role |
|---|---|---|
| Keyboard | 6.97 | measured interaction, **never billed** |
| Timesheet | **19.75** | tracked working time, **the floor and the deliverable** |
| Weighted | 31.50 | provisional tier model, **not invoiced** |

Two directions this protects:

- **Downward.** A day of low-tier work can derive a weighted figure *below* tracked hours. That
  never reduces the bill. Time was worked; time is billed.
- **The keyboard fallacy.** 6.97 h of hands-on-keyboard across three days does not mean seven
  hours of work. It excludes thinking, reading, waiting on a 1h47m pipeline run, and everything
  done away from the session. Nobody bills keyboard time and nobody should be able to argue us
  down to it.

This makes explicit what the original ADR implied ("the timesheet is unchanged", "nothing is
auto-invoiced") but never stated as a rule.

### Open: how to capture value above the floor (Niels, 2026-08-14)

Niels wants to bill nearer the 31 than the 20, with 20 as the minimum. This is a **Pingala
question, not a Carl Ras one** — he is simply the first to hit it in practice.

**The hard constraint.** You cannot put 31 in the hours column of a time-and-materials agreement
that counts hours. It misstates the measure, and it does not even work: if the agreement caps
hours, inflating hours exhausts the cap sooner and the problem returns. *The number being sought
is not a better hours figure. It is a price.*

**Three routes, solving different problems:**

1. **Rate, not hours.** Bill the tracked hours at a higher rate. The only one of the three that
   fits *inside* an existing hours ceiling, because it adds no hours. Frame as capability, not
   speed — customers accept paying more for seniority and resent paying more for velocity.
2. **Fixed price on outcome.** Stop selling hours; the agreement holds scope and price, and hours
   become internal cost accounting. The structural answer, since the ceiling only binds while the
   unit of sale is the hour.
3. **Component licensing.** Charge for the asset, not the time to apply it.

**The reuse case breaks the multiplier model, and it is the important one.** Niels's observation:
sometimes weighted hours are *not enough*, e.g. when an already-built component is reused. Reusing
a component can deliver in 2 h what would otherwise take 200. No multiplier on 2 h reaches 200 —
that needs 100x and the tier table tops out an order of magnitude below.

So two problems are wearing the same coat:

- **Acceleration** — hours understate effort. A multiplier is a plausible instrument.
- **Reuse** — hours are near zero *regardless* of value delivered. A multiplier is structurally
  incapable of expressing it, because it scales hours and there are almost none.

The current model contemplates only the first. Acceleration is also the weaker long-term position:
it is a commodity every competitor acquires with the next model generation. Reuse is Pingala's own
IP and is the one an hours frame can never price.

**What the weighted number is actually for:** evidence at negotiation, not a line on an invoice.
"Delivered conventionally this was ~31 h" argues for a rate or a fixed price. Caution already on
record in `eval-2026-08-06-fitted-is-not-validated` — the multipliers are self-derived and untested
against a customer's own counterfactual, so 4.52x is a sound internal instrument and a thin
argument to someone who did not build the model. Concrete outcomes are the stronger case: this
session produced a measured 2.57x on the enriched build and surfaced three tables that had been
silently inflating their row counts since at least 2026-08-07 with nobody told — customer-legible
value with no reference to hours at all.

**Needs an owner.** This is a pricing decision above the scope of the time-tracking system. Carry
into the end-of-August re-evaluation as question 5.

### Evaluation plan — additional question

5. Does the weighted model have anything useful to say about **reuse of existing components**, or
   does that case need a separate instrument (licensing / fixed price) entirely? The answer
   determines whether the tier multipliers are the right long-term shape at all.
