---
id: eval-20260907-matas-datacompare-skills
ts: 2026-09-07T12:00:00Z
type: evaluative
scope: workspace
source: distilled
tags: [eval, skills, dataviz, pingala-fabric-platform, fabric-project-access, email-outlook-ready, writing-voice, microsoft-docs, memory-capture]
status: distilled
description: "Skill checkpoint for a full day of Matas DataCompare work: dataviz fired but its validator needs node (absent); pingala-fabric-platform and fabric-project-access stayed silent through Fabric SQL database, API for GraphQL and Fabric Apps decisions because they hold nothing on them; microsoft-docs via MCP carried every platform fact; the writing-voice invocation was captured into the memory stream as its expanded body"
---

**Fired and helped:** `pingala-visual-identity` (palette and fonts for the report and the app),
`email-outlook-ready` + `writing-voice` (emails 05 and 06), `microsoft-docs` through the MCP server
(Fabric Apps / Rayfin, API for GraphQL auth model, address-format setup, region availability -
every architecture claim of the day was checked there, none from memory).

**Fired and half-helped:** `dataviz`. The method was applied (chips, one axis, labels not colour
alone) but `scripts/validate_palette.js` could not run: **no Node on this machine**. The chart
shipped with an unvalidated four-colour palette. Either install Node or give the skill a Python
fallback.

**Should have fired and did not:** `pingala-fabric-platform` and `fabric-project-access` were
on-topic for hours (creating a Fabric SQL database, Fabric API for GraphQL, Fabric Apps tenant
setting, app registration with a delegated Power BI permission, capacity region) and stayed
silent. Cause is content, not triggering: neither skill covers Fabric SQL database, API for GraphQL,
Fabric Apps, or the app-registration recipe for a browser app; the platform skill also lacks the
Atomic column-metadata and grouping conventions (its own "area to explore later"). The two
distilled records from today (`datacompare-shared-backend-two-hosting-tracks`,
`compare-user-maintained-fields-not-setup-renderings`) are the raw material for that update.

**Harness observation:** invoking `writing-voice` put the skill's expanded body into the memory
stream as a User line (sentinel flag :102), and six task notifications with temp paths landed the
same way. The verbatim capture path skips the sanitizer that the summarizer path has; the daily
stream is noisier than the store because of it. Not a skill defect, a capture-path one.
