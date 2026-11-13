---
id: feedback-start-sign-in-yourself
ts: 2026-11-04T12:00:00Z
type: semantic
scope: workspace
source: manual
tags: [feedback]
status: distilled
description: "When an Azure/Fabric sign-in is needed (az login, fab auth, expired token), start the sign-in command yourself and tell Niels which account to pick in the browser; never ask him to type it. Customer/non-default tenant: always az login --use-device-code, and check az account list for the tenant before saying signed in"
---

When a step needs an Azure or Fabric sign-in (`az login`, `fab auth login`, a token expired),
**start the sign-in command yourself** right away. Do not hand Niels a command to type.

- Say which account to pick in the browser window that opens.
- Pingala tenant `5e8d3c87-f9c4-4575-a670-d76860aa43e2`: `nchristensen@pingala.eu`.
- Customer tenant: the customer's account for Niels (from the customer node's `CLAUDE.md`);
  pass `--tenant <id>` so the right tenant is signed in (Guardrail 11).

**Customer / non-default tenant: device code, always (2026-11-11).**
1. Run `az login --tenant <id> --use-device-code` in the background, output to a file; read the
   code from the file. Give Niels the URL (`https://microsoft.com/devicelogin`), the code and the
   account in the "Next for you" block. Device code works in any browser and any profile.
2. A browser sign-in never signs in the az CLI; only completing the CLI's own flow does. Before
   saying "signed in", or acting on Niels's "I'm signed in", run
   `az account list --query "[?tenantId=='<id>']"`. Empty = the CLI did not get the token: say so
   and re-show the code (start a new flow if it expired). Never ask him to sign in again in the
   browser.
3. `fab auth login` (checked 2026-11-11, `--help`): flags are `-u -p -t -I --certificate`; no
   device-code option. For a customer tenant prefer `az` (device code) and Fabric REST via
   `az rest --resource https://api.fabric.microsoft.com`; if `fab` is required, run
   `fab auth login -t <id>` and verify with `fab auth status` before going on.

**Why:** Niels, 2026-11-04: make it a general rule for every session in `C:\Dev`.
2026-11-11 (DataCompare, Matas tenant): the interactive `az login` opened a browser/profile Niels
could not identify; he signed in in his own browser, `~/.azure` never got the Matas account. Two
rounds lost; Niels: "a major issue we need to fix".

**How to apply:** every sign-in prompt. Rule also in `C:\Dev\CLAUDE.md` > Behaviour.
See [[tenant-scoped-cli-auth]], [[fab-console-login-and-silent-sql-onelake-tokens]].

**Pingala tenant (2026-11-12):** device code is refused there ("not allowed", three codes lost).
For `5e8d3c87-...` run the browser flow `az login --tenant 5e8d3c87-f9c4-4575-a670-d76860aa43e2
--allow-no-subscriptions` in the background; it opens the default browser and returned exit 0.
Device code stays the rule for customer tenants.
