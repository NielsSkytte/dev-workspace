---
id: eval-2026-08-01-marketo-extraction
ts: 2026-08-01T00:00:00Z
type: evaluative
scope: project:customers/Carl-Ras/datahub
source: session:9ac996f0-d2cc-4caa-a6c8-e7f774f19536
tags: [evaluative, skills]
status: distilled
description: "evaluative: skills present in a project session and still silent on watermark/date-filter work; three self-inflicted overreach/overclaim failures the user caught"
---

**Skills: present, listed, and still did not fire.** This was a project-rooted session
(`customers/Carl-Ras/datahub`) after the 2026-08-01 harness-cascade fix, so the roster was
demonstrably loaded — the available-skills listing named them. The session's entire subject was
**watermarks and date filters sent to an external API** (`createdAt` vs `updatedAt` windows, UTC
handling, incremental cadence). `timestamp-timezone-pipelines` names exactly that in its
description ("watermarks, date filters sent to external APIs"); `medallion-migration-validation`
names "designing watermark and tracking table patterns". Neither fired, nor did any other.

**Why this matters:** it corroborates the 2026-07-31 workspace-level finding and removes the
remaining ambiguity. Absence was the explanation for project sessions before the cascade fix; it
is not the explanation now. This is a **trigger miss** with the skill present — the same failure
mode, now observed at both scopes. See [[eval-2026-07-31-skills-available-not-firing]],
[[hooks-subdir-session-gap]].

**Own-output failures the user caught, three of a kind — claiming or doing more than warranted:**

1. **Scope overreach on a general rule.** Asked to gitignore `data/`, I also added `.secrets/` and
   applied both to all nine unit repos. The unit repos are local-only backups where credentials
   *belong*; the correction: *"local repos can contain secrets of various types. if a repo is ever
   committed to a remote they must never be included."* Rule earned: **when generalising a rule the
   user asked for, generalise only the rule they asked for** — an adjacent one that "obviously"
   belongs is a separate proposal, not a free rider. Fixed in [[gitignore-data-folders]].
2. **A claim beyond its evidence.** Reported "this repo has no `.gitignore` at all" from a grep
   that had only searched it for the word "secret". The file existed. Same family as the repeated
   [[feedback-fact-only-language]] misses — *state what the check actually checked*.
3. **Ambiguous hand-off.** Closed a turn with "which do you want?" over two options whose stakes
   were never stated; the user replied "not quite sure what you are asking me to decide". When
   there is a defensible recommendation, **make the call and say why** rather than presenting a
   menu.

Plus the register failure recorded separately in [[feedback-response-style]]: asked to explain
something *plainly*, replied with bold headers, tables and `file:line` citations.

**Capture gap:** the `Stop` hook recorded 12 turns for this session, none after 13:03Z — roughly
the last third of the session (the Marketo custom-object extracts and the v0.2 doc rewrite) is
absent from `daily/`. The store records were written from the conversation, so nothing was lost
here, but the gap is unexplained and worth watching.
