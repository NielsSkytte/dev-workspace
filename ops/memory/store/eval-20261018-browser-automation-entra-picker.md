---
id: eval-20261018-browser-automation-entra-picker
ts: 2026-10-18T15:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [eval, chrome-automation, entra, sign-in, diagnosis]
status: distilled
description: "2026-10-18: an Entra sign-in loop looked like 'clicks have no effect' in browser automation; the Entra sign-in log (Graph beta auditLogs/signIns by appId) showed the real error AADSTS700054 at once. Read the sign-in log before blaming the browser."
---

- Context: testing a closed SWA sign-in on leita.dk. The account picker came back after every click; I reported
  "automation clicks have no effect" three times and asked the owner to click himself.
- Reality: every click had signed in; Entra refused the hybrid flow (`response_type 'id_token' is not enabled`).
  `az rest GET https://graph.microsoft.com/beta/auditLogs/signIns?$filter=appId eq '<id>'` showed it (works
  without P1 for user sign-ins; service-principal sign-ins need P1). Log lag about 2-5 minutes.
- Lesson: on a sign-in loop, read the sign-in log first. Sentinel 10-17/18 also re-flagged the capture
  mojibake (`â–¶` for the arrow) already recorded in eval-20261016-capture-assistant-mojibake.
