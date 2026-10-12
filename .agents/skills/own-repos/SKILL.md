---
name: own-repos
bundle: custom
description: How work in C:\Dev\own (Pingala's own products and tools) relates to git and to the private GitHub repo atompower4us/AAI - one repo, one folder per product. Use it whenever you commit, branch, merge, sync, back up or hand over work in an own/ project (MetaAtomic, SoWSkill, Ontology, ...), when a cloud session or a colleague has worked in AAI, when a new own/ project should become an AAI folder, when a handover brings patches, or before building/deploying anything that leaves the repo for a customer (customer-name guard in build.py). Also use for "is AAI up to date", "pull the cloud work in", "where does this commit go", "git add did nothing on Windows". NOT for customer repos (customers/...) - those are never auto-committed or pushed.
---

# Working in own/ and AAI

## The model (decided 2026-10-12, Niels)
- `C:\Dev\own` is ONE local git repo for all own projects. It has no remote. Paths stay
  `own/<Project>`; never restructure them.
- `atompower4us/AAI` (private) is the product monorepo: one folder per product, history kept.
  MetaAtomic's repo IS AAI. Customer names are in the history, so it stays private.
- A new `own/` project becomes an AAI folder "if/when it makes sense": add its name to
  `FOLDERS` in `own/.git/hooks/post-commit`. The hook is Niels's to edit; do not write it.
- Customers get a BUILD, never the repo. Builds are checked by one name guard (below).
- Ontology currently lives only in AAI (branches `import-ontology`, `pitch-deck`,
  `servicenow-flow-ontology`, `app-hosting-adr`); the plan is for it to merge into MetaAtomic
  later, which in one repo is a folder move with history.

## Step 0 - always run the status script first
`powershell -NoProfile -File C:\Dev\ops\bin\own-status.ps1` (read-only). It reports branch,
whether the post-commit hook is installed and which folders it pushes, per folder IN SYNC /
BEHIND / UNCOMMITTED (tree-id comparison, not a guess), folders that exist only in AAI, and AAI
branches with PENDING work. Do not state the sync state from memory or from a doc; the script
is the source.

## Commit rules
1. **The hook pushes on every commit.** A commit touching a hooked folder is on GitHub within
   seconds, in the background (`%LOCALAPPDATA%\aai-sync\hook.log`). So: commit only what is final.
   `reset --soft` / amend afterwards cannot unpush; AAI keeps the abandoned commits, and removing
   them needs a force push (ask first). Measured 2026-10-12: one misstaged commit left three
   duplicate commits in AAI main.
2. **Stage with the tracked path case.** Folders are tracked as `MetaAtomic/`, not
   `metaatomic/`. On Windows `git add metaatomic/x` can stage some files and silently skip
   modified tracked ones. After `git add`, run `git status --short` and check every file you
   expect is in the index before committing.
3. Branch for work that needs review (`git switch -c <topic>`); fast-forward `master` after
   (`git merge --ff-only`). Direct commits to master are acceptable for small, tested work.
4. Internal repos are always committed at wrap-up; customer repos are never auto-committed.
5. Commit trailers per the session attribution reminder. Never `--no-verify`.

## Work done in AAI (cloud session, colleague) -> back into own
Use `sync-aai.ps1 -Pull`, never hand-applied patches:
`powershell -NoProfile -File C:\Dev\ops\bin\sync-aai.ps1 -Pull -Branch <aai-branch> <Folder>`
- Takes the commits on that branch since it left main that touch `<Folder>/`, applies them with
  `git am -3` on a new branch `pull/<Folder>-<aai-branch>` in own. Needs a clean tree.
- Does not merge, does not push. On a conflict it aborts and leaves the repo as it was.
- Then: run the project's tests, show Niels the result, merge only on his go.
- If a handover document says to clone and `git am` by hand, this replaces it (`-p2` only when
  a folder is a repo root; the script handles that).
- Already-applied patches are refused cleanly; PENDING in the status script is a signal, the
  `-Pull` result is the answer. Root files of AAI (`.claude/`, `handover/`) are not own's.

## Pushing by hand
`sync-aai.ps1 <Folder>...` (committed work only; `-NoPush` builds locally; `-List`; `Path=Name`
sets the AAI folder name). Normally unnecessary: the hook does it. Needs git, python
`git_filter_repo`, `gh` logged in. The sync is deterministic: same history, same commit ids.

## Nothing customer-specific may leave in a build
`build.py` (MetaAtomic) runs one guard, `_guard`, on all three outputs: `publish` (shared ADO
repo), `app` (the `.pyz`, scanned after assembly, deleted when refused) and `deploy` (notebooks,
pipeline template, and the `.pyz` with `--no-app`).
- Names come from `design/forbidden_names.txt` (committed, never in SHIP), the folder names in
  `C:\Dev\customers`, and `METAATOMIC_FORBIDDEN`. An EMPTY list refuses; it never passes.
- Add a new customer, person, domain or tenant id to that file when it appears. Avoid ordinary
  words (`impact`, `lars` matched real code).
- A product folder added to AAI needs the same pattern before anything ships to a customer.
- `--force` exists; use it only on Niels's word.

## Decisions already made - do not reopen
- Own structure stays; AAI is the repo; sync is hook-driven one way, `-Pull` the other.
- MetaAtomic does DQ in Fabric with its store (ADR 0017); customers' decisions go through
  GraphQL; only Pingala staff edit packs; page hosting is a data-free Azure Static Web Apps
  shell (SharePoint is out). See `own/MetaAtomic/CONTEXT_DECISIONS.md`.
- Everything under `own/` is private by default; customers see builds only.

## Failure modes seen
| Symptom | Cause | Do |
|---|---|---|
| `git add` ran, `status` shows files still unstaged | path case differs from tracked path | re-add with the tracked case |
| Duplicate/abandoned commits in AAI main | hook pushed before a reset/amend | accept, or ask Niels about a force push |
| `-Pull` says a patch did not apply | already applied, or own has diverged | read `git log` for the commit; do not force |
| `build.py app` REFUSING, no pyz in dist/ | a customer name in a shipped file | fix the file; do not `--force` |
| `build.py` REFUSING: no forbidden names | `design/forbidden_names.txt` missing | restore it |
| status shows folder BEHIND | hook not installed, failed, or folder not in FOLDERS | read `hook.log`; run `sync-aai.ps1 <Folder>` |
