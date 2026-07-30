---
id: eval-2026-07-30-env-discovery
ts: 2026-07-30T09:35:00Z
type: evaluative
scope: workspace
source: session:746d591b
tags: [evaluative, skills, pingala-fabric-platform, dashboard, sentinel, fact-only-language]
description: "evaluative: pingala-fabric-platform never fired across ~70 turns of Dataverse/F&O/Fabric-link work despite naming those exact triggers; two self-caught reporting failures on superseded numbers"
status: distilled
---

Session 746d591b, 2026-07-29 -> 07-30, ~70 turns building the Dataverse/F&O environment-discovery
scripts (see `dataverse-fno-link-discovery`).

## Skills that should have fired and did not

**`pingala-fabric-platform`** never loaded. Its own description says "Trigger on any question
about ... **D365 F&O extraction, Dataverse integration** ... OneLake". The entire session was
D365 F&O <-> Dataverse <-> Link to Fabric / Synapse Link. Not one of the 18 workspace skills fired
across the session. Two candidate causes, undistinguished:

1. Workspace `.claude/skills/` may not reach a project-rooted session — same family as
   `hooks-subdir-session-gap`. Evidence for: the only command that resolved from a *pointer* this
   session was `/dashboard`, which exists as a **user-level** copy; user-level `skills/` is empty.
   Evidence against: `/log` resolved fine and exists only at workspace level, so workspace
   `commands/` clearly do cascade.
2. Trigger miss — the phrasing was operational ("script for listing all dataverse environments")
   rather than architectural.

**Worth resolving before assuming a trigger problem**, because if (1) holds then every project
session runs without any domain skill and no amount of description tuning helps. Cheap test: at a
project root, ask something that names a skill's most explicit trigger and see whether it loads.

`sentinel` again not spawnable from a project-rooted session (known; 4th consecutive /log).
The agent roster remains the one unresolved leg of `hooks-subdir-session-gap`.

## Skills that fired and helped

`/dashboard` (user-level pointer) — worked. `/log` — worked from workspace level.

## Own-output failures the user caught

Both are `feedback-fact-only-language` violations of the same kind: **reporting a number without
its provenance.**

1. Quoted a "108 Dataverse tables" figure that came from a superseded run of superseded code, and
   had silently dropped the column that produced it when adding the Fabric columns. The user asked
   "where do you see 108 for CRM Test?" — the honest answer required citing the exact prior runs
   and admitting the column was gone.
2. Reported table counts as authoritative before scoping them to the profile; they were counting
   internal profiles.

**Rule this session earned:** when a column's definition changes, say the number it used to
produce is void — do not carry the old figure forward and do not remove the column silently.
Every count reported from a script under active edit needs the run it came from.

The corrective that worked, repeatedly: the user checked each number against the maker portal and
made the script match. Eight successive column definitions were wrong before the four in
`dataverse-fno-link-discovery` survived. Empirical verification against the product UI beat
reasoning about the schema every single time.
