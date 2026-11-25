---
id: feedback-start-sign-in-yourself
ts: 2026-11-19T19:00:00Z
type: semantic
scope: workspace
source: manual
tags: [feedback]
status: distilled
description: "When an Azure/Fabric sign-in is needed (az login, fab auth, expired token), start the sign-in command yourself and tell Niels which account to pick in the browser; never ask him to type it. NEVER device code (2026-11-19): browser flow az login --tenant <id> --allow-no-subscriptions for every tenant, then check az account list for the tenant before saying signed in"
---

When a step needs an Azure or Fabric sign-in (`az login`, `fab auth login`, a token expired),
**start the sign-in command yourself** right away. Do not hand Niels a command to type.

- Say which account to pick in the browser window that opens.
- Pingala tenant `5e8d3c87-f9c4-4575-a670-d76860aa43e2`: `nchristensen@pingala.eu`.
- Customer tenant: the customer's account for Niels (from the customer node's `CLAUDE.md`);
  pass `--tenant <id>` so the right tenant is signed in (Guardrail 11).

**Never device code, any tenant (Niels, 2026-11-19: "dont use the code login it almost NEVER
works").** It was refused in the Pingala tenant (2026-11-12, three codes lost) and blocked by
Conditional Access at Carl Ras (AADSTS530036, 2026-11-17).
1. Run `az login --tenant <id> --allow-no-subscriptions` in the background. It opens the default
   browser. Tell Niels the window is opening and which account to pick.
2. A sign-in in some other browser tab never signs in the az CLI; only completing the CLI's own
   browser flow does. Before saying "signed in", or acting on Niels's "I'm signed in", run
   `az account list --query "[?tenantId=='<id>']"`. Empty = the CLI did not get the token: say so
   and start the flow again.
3. If the browser opens a profile Niels cannot identify (2026-11-11, Matas), tell him to copy the
   URL from that window into his own browser profile; do not fall back to device code.
4. `fab auth login` (checked 2026-11-11, `--help`): flags are `-u -p -t -I --certificate`. Prefer
   `az` and Fabric REST via `az rest --resource https://api.fabric.microsoft.com`; if `fab` is
   required, run `fab auth login -t <id>` and verify with `fab auth status` before going on.

**Why:** Niels, 2026-11-04: make sign-in a general rule for every session in `C:\Dev`.
2026-11-11 (Matas): an interactive login opened a browser profile Niels could not identify, and
device code became the rule. 2026-11-19 (MetaAtomic): Niels reversed it; device code almost never
works for him.

**How to apply:** every sign-in prompt. Rule also in `C:\Dev\CLAUDE.md` > Behaviour.
See [[tenant-scoped-cli-auth]], [[fab-console-login-and-silent-sql-onelake-tokens]].
