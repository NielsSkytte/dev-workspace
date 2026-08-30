---
id: eval-2026-08-30-marketo-write-path
ts: 2026-08-30T12:00:00Z
type: evaluative
scope: workspace
source: session:508d3307-4a64-434b-9dfe-a5ebf6eba693
tags: [evaluation, skills, fabric-warehouse-git, fabric-pipeline-notebook, marketo, capability-gap]
status: distilled
description: "Marketo write-back session: no skill fired for the destination system because none exists, and two skills that should have fired on the Fabric half did not - both hazards were caught by testing instead"
---

## Skills that should have fired and did not

**`fabric-warehouse-git`.** The session edited a warehouse view (`viewoutboundtransform.Marketo_Lead`)
and committed it. That is the skill's stated trigger surface, including "validating .sql files
before committing them" and the `-- Auto Generated` header hazard. It did not fire.

The hazard then materialised: a Python patch script read the file with `read_text` and wrote it with
`write_text`, which silently converted the whole file **CRLF -> LF**. The diff read 224 insertions /
179 deletions on a nine-line change. Caught from `git diff --stat` looking implausible, not from any
guidance — and this repo has already had an Update-from-git failure caused by exactly this class of
line-ending/header damage.

Lesson worth encoding: **when a script rewrites a file in a git-connected Fabric repo, check the
diff stat before the diff content.** An implausible line count is the cheapest possible detector.

**`fabric-pipeline-notebook`.** The session authored a new notebook + pipeline pair
(`NB_Outbound_Marketo` / `PL_Outbound_Marketo`). Squarely the skill's trigger, and it did not fire.
The house patterns had to be recovered by reading sibling items instead.

A defect of exactly the kind the skill describes ("notebook behaviour that differs") was then found
by testing rather than by guidance: `notebookutils.data.connect_to_artifact(...).query()` returns a
**pandas** frame, and pandas represents a SQL NULL in a numeric column as `NaN`. The three-state
omission policy tests `v is None` and would have missed every one, putting `NaN` into a JSON payload.
Fixed with `df.astype(object).where(df.notna(), None)`.

## The capability gap

**Nothing in the roster covers a destination system.** Every skill here is Fabric-side or
Pingala-process-side. Marketo — the API's failure semantics (HTTP 200 with `success: false`),
the field-type coercions, consent-field danger, rate limits, `updateOnly` vs Bulk Import — was
learned from five research subagents plus live probing against the customer's production instance.

That knowledge is now spread across a memory record, a task file, two tool modules and a notebook
docstring. It is durable but not *reusable*: a second reverse-ETL destination would start from zero.
Worth putting to Q as a candidate skill (reverse-ETL / destination-system integration), though the
honest counter-argument is that one instance of a pattern is not yet a pattern.

## What did work

Two habits caught three defects that no skill would have:

1. **Running the shipped code over real data before shipping it.** The `title = ''` bug (AX09 stores
   absent text as an empty string, so an OMIT field would have been sent as `''` and blanked the job
   title on every lead) is invisible to review and obvious the moment you print per-field counts.
2. **Measuring the destination instead of trusting its documentation.** Adobe documents none of the
   null coercion, the six-significant-digit float precision, or the datetime rendering offset. All
   three were found by writing one value to one synthetic lead and reading it back.

## Correction taken this session

Told mid-session that replies were over-explaining: *"we need focus on why and what, the deeper
explanation I'll ask for when required"* — then, minutes later, that the stripped-down version would
**not** have worked as an opening reply. The rule is **cut derivation, keep context**, right-sized to
what the reader already holds — not "be short". Both halves are recorded in
`feedback-response-style`; the second half matters more, because the first correction alone would
have produced an overcorrection.
