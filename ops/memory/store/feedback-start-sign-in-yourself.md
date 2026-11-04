---
id: feedback-start-sign-in-yourself
ts: 2026-11-04T12:00:00Z
type: semantic
scope: workspace
source: manual
tags: [feedback]
status: distilled
description: "When an Azure/Fabric sign-in is needed (az login, fab auth, expired token), start the sign-in command yourself and tell Niels which account to pick in the browser; never ask him to type it"
---

When a step needs an Azure or Fabric sign-in (`az login`, `fab auth login`, a token expired),
**start the sign-in command yourself** right away. Do not hand Niels a command to type.

- Say which account to pick in the browser window that opens.
- Pingala tenant `5e8d3c87-f9c4-4575-a670-d76860aa43e2`: `nchristensen@pingala.eu`.
- Customer tenant: the customer's account for Niels (from the customer node's `CLAUDE.md`);
  pass `--tenant <id>` so the right tenant is signed in (Guardrail 11).

**Why:** Niels, 2026-11-04: make it a general rule for every session in `C:\Dev`.

**How to apply:** every sign-in prompt. Rule also in `C:\Dev\CLAUDE.md` > Behaviour.
See [[tenant-scoped-cli-auth]], [[fab-console-login-and-silent-sql-onelake-tokens]].
