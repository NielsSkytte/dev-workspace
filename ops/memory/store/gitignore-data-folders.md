---
id: gitignore-data-folders
ts: 2026-07-31T00:00:00Z
type: semantic
scope: workspace
source: session:9ac996f0-d2cc-4caa-a6c8-e7f774f19536
tags: [convention, guardrail, privacy]
status: distilled
description: "data/ ignored in every unit repo; secrets barred only from repos with a remote, not from local-only ones"
---

Two rules with different boundaries — the distinction is the point.

**`data/` is git-ignored everywhere.** Written into every unit repo's harness-managed
`.gitignore` block by `ops/bin/heal-repos.ps1` > `Set-ManagedIgnore`. Whatever lands there is
either sensitive (customer personal data, API extracts) or bulky (samples, dumps).

**Secrets are barred from repos that go ONLINE, not from local ones.** The eight customer unit
repos and `own/` have **no remote** — they are the private backup, and credentials belong in
them; ignoring `.secrets/` there would leave secrets unbacked. Enforced at the real boundary
instead: `Ensure-Excludes` adds `.secrets/` to the local `.git/info/exclude` of every sub-repo
that has a remote (customer-facing *and* internal), and `C:\Dev` — which pushes to
`github.com/NielsSkytte/dev-workspace` — ignores `.secrets/` and `data/` in its own
`.gitignore`.

**Why:** caught 2026-07-31. A Marketo extract put ~1,000 real customer email addresses in the
Carl Ras repo, which prompted the `data/` rule. I then added `.secrets/` to the same managed
block on my own initiative; Niels corrected it — *"local repos can contain secrets of various
types. if a repo is ever committed to a remote they must never be included."*

**How to apply:** don't hand-write these patterns into a repo `.gitignore` — they belong in the
managed block or in `Ensure-Excludes`. Run `powershell -File C:\Dev\ops\bin\heal-repos.ps1`
(optionally `-Only <unit>`) to apply. Two caveats worth stating when this comes up: ignoring
never untracks — anything already committed stays committed, so `.gitignore` is no remedy after
a leak; and `.git/info/exclude` is per-clone and never committed, so it guards this machine, not
the repo. Before assuming a repo is safe to hold secrets, check `git remote -v` rather than
assuming from its role. See [[repo-vs-project-vs-task]], [[feedback-fact-only-language]].
