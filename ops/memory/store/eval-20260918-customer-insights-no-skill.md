---
id: eval-20260918-customer-insights-no-skill
ts: 2026-09-18T07:15:00Z
type: evaluative
scope: workspace
source: session:session_01P1qZjJ14dHz6gjhBLtip8t
tags: [evaluation, skills, customer-insights, writing-voice, microsoft-learn]
status: distilled
description: "Two days of Customer Insights - Data work fired no domain skill: none covers CDP/segmentation, so every product fact came from the Microsoft Learn MCP; writing-voice fired correctly for the Danish customer note"
---

Session 2026-09-16/18, Carl Ras, Customer Insights - Data proof (`carlras-customer-insights-poc`).

- **No domain skill fired, and none exists that should have.** `pingala-fabric-platform`,
  `fabric-deployment` and `fabric-warehouse-git` do not cover Dynamics 365 Customer Insights. Every
  product fact (OneLake connector limits, activity requirements, suggestion mechanics and their
  category caps, Journeys vs Data) came from the `microsoft-learn` MCP, cited in the answer.
  Cost: several round trips that a skill would have answered directly, and one wrong first
  recommendation (a lakehouse view as the CI source) that the docs then corrected.
- **Candidate, not yet justified.** A `customer-insights` skill is only worth building if Carl Ras
  buys a licence or a second customer asks. The knowledge that exists today is in
  `datahub/design/CUSTOMER_INSIGHTS_SETUP.md` and the record above, which is enough to rebuild.
- **`writing-voice` fired correctly** for the Danish note to Kasper. First draft was written in
  ASCII transliteration (`aa/oe/ae`), which is the `.sql`/`.ps1` rule leaking into a `.md`
  deliverable; caught and rewritten before hand-over.
- **Time tagging was wrong for most of the session.** Niels opened it as an untracked question, so
  7.6 measured minutes landed with no task before he confirmed the work belongs to
  `CarlRData-557`. The day-brief task prompt was skipped on his instruction, and nothing re-asked
  when the session turned into hours of delivery work.
