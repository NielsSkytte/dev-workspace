---
id: eval-2026-08-03-matas-part3
ts: 2026-08-03T12:00:00Z
type: evaluative
scope: project:customers/Matas/DataCompare
source: session:b6def628
tags: [evaluation, skills, claude-in-chrome, microsoft-docs, browser]
status: distilled
description: "Skill evaluation 2026-08-03: the claude-in-chrome skill was skipped in favour of loading its tools directly, and the browser-identification guidance it carries is exactly what the owner then had to ask for"
---

**Should have fired, didn't — `claude-in-chrome`.** Its description says to invoke it *before*
using any `mcp__claude-in-chrome__*` tool. I went straight to `ToolSearch` for the core tool set and
drove the browser without it. The cost was concrete: when the account picker showed the wrong
tenant, the owner had to ask "how can you identify which [Chrome] to use?" — the
`list_connected_browsers` → `select_browser` / `switch_browser` flow, and the rule that every
connected browser must be offered as a choice rather than picked for them, is guidance I only
reached for after being prompted. Loading a tool is not the same as loading the doctrine for using
it, and the tool list gives no hint that doctrine exists.

**Fired on request and helped — `microsoft-docs:microsoft-docs`.** Asked whether a hand-authored
`.platform` needs a `logicalId`. It came back grounded: write a fresh GUID (documented only for the
copy-a-directory case, so partly inference and labelled as such), duplicates fail Update-from-Git,
and the per-item-type pages contradict `source-code-format` on where `version` sits — copy what
Fabric emitted. It also caught that the item folder held only `.platform` at the moment it looked.

**Didn't fire, and that was right — `pingala-fabric-platform`.** Building a Fabric notebook is in
its territory, but the project's own Part 2 notebook was the better template (read/write helpers,
warning collection, slice-scoped writes), and matching it is what keeps the two parts legible as one
engine.

**Own process, one worth keeping:** the failing test on the first run was the test's expectation,
not the code — a cross-border pair scored 0.625 because the country mismatch enters the mean. I
checked the actual `token_sort_ratio` values before deciding which side was wrong. Cheap habit,
prevented "fixing" correct behaviour.

**Memory-capture vetting (sentinel not dispatched — standing no-subagents instruction, 8th
consecutive `/log`; the 5 records for this session in `daily/2026-08-03.md` were hand-vetted).**
Charset clean, in bounds. **One fidelity flag:** the record at `daily/2026-08-03.md:178` summarises
the turn as "Installed the extension, identified an issue with user permissions..., informed the
admin" — those are the *owner's* actions, written with the assistant as implied subject; the same
subject-conflation family already logged on 08-03 and 08-01. The remaining four are accurate.
