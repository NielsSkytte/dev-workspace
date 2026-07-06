---
id: eval-2026-07-06-artifact-design
ts: 2026-07-06T17:05:00Z
type: evaluative
scope: workspace
source: session:8b788acf
tags: [evaluative, skill-artifact-design]
status: distilled
description: "artifact-design fired and helped (v1 review artifact); first record of the committed evaluation layer; setup-day session so domain skills correctly stayed quiet"
---

First evaluative record of the committed evaluation layer (Gate 3, 2026-07-06).

- **Fired + helped:** `artifact-design` — loaded before building the v1-review artifact; its
  calibration guidance (utilitarian treatment, token-based dual-theme, no templated hero) shaped
  the deliverable. No correction needed afterwards.
- **Correctly silent:** domain skills (fabric-*, pingala-*, writing-voice) — this was a
  workspace-infrastructure session with no customer deliverable, no Fabric work, no prose for
  a customer. No misfires observed, no should-have-fired gaps observed.
- **Note:** a setup-day session is weak evidence either way; the meaningful signal starts with
  this week's project sessions (Tystofte/Matas/Carl-Ras).
- **Sentinel first run (same day):** 4 flags on 33 records, all correct on spot-check. Systematic
  summarizer failure mode identified: `qwen3:1.7b` states *intended* work as *completed*
  ("decided to scaffold", "Gate 2 fully completed", "Completed triage") in turns where the work
  had only been proposed or started — a fidelity error the deterministic sanitizer cannot catch.
  Watch whether this recurs; if it does, a prompt tweak ("describe only what THIS turn did") is
  the cheap fix before any model change.
