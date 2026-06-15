# AGENTS.md — Tool-Neutral Source of Truth

This workspace is **LLM-agnostic**. Any capable LLM, pointed at this folder, must be able to operate it. This file — not `CLAUDE.md` — is the canonical description of how the workspace works. Tool-specific files (`CLAUDE.md`, `GEMINI.md`, …) are thin bootstraps that point here.

## Governing principle: LLM-agnostic substrate; harness is a non-load-bearing accelerator

1. **Substrate is portable.** All durable content — knowledge, inbox, tasks, decisions (ADRs), conventions — is plain markdown in tool-neutral locations, readable and usable by any LLM with no special harness.

2. **Harness is an accelerator, never load-bearing.** Tool-specific features (Claude Code slash commands & skills, `CLAUDE.md`, MCP servers, scheduled agents) are permitted *only* to speed up operations that are also fully described in plain prose — here, or in the relevant README. Remove the harness and the operation must still be performable by hand.

   **Portability is about *capability and knowledge*, not *determinism and triggering*.** Auto-triggers — hooks, scheduled agents, anything that fires on its own — are permitted accelerators. They may add what prose cannot: a guarantee that a routine runs, and an automatic trigger to run it. But they must hold **no decision logic or knowledge** that isn't also written in this substrate; a hook is a dumb executor of a documented routine, never the source of one. Test: porting to another LLM may lose *automation* (the routine now runs only when the LLM acts on the instruction), never *capability* (the routine is still here, still doable by hand). If a hook script contains a rule you'd lose by deleting it, that rule was welded to the tool — move it here.

3. **Acid test.** Delete every tool-specific file (`.claude/`, `CLAUDE.md`, …) and point a bare LLM at this folder + `AGENTS.md`: everything must remain intact and operable. If deleting the harness loses knowledge or capability, that capability was wrongly welded to the tool — fix it.

4. **Permitted exception — bootstrap / initialization.** Tool-specific *initialization* is fine: a thin `CLAUDE.md` / `GEMINI.md` that tells the tool to read this file; MCP / credential setup; command definitions that merely wrap operations already documented in prose. **Bootstrap may be tool-specific; the system it boots may not.**

## Why this matters here

This is the **tool-portability** half of the AtomicCortex portability constraint, applied to the whole workspace (not just AtomicCortex): *structure is the asset, the LLM is a replaceable worker.* It is what makes a future Claude→Gemini switch — or offloading parts to a local LLM — nearly free.

## Continuity loop

The workspace remembers across sessions through three plain-markdown artifacts in `ops/`, plus a routine M follows:

- `ops/TODO.md` — raw action capture (ICOR **Input**). Anything to act on later. (`/todo`)
- `ops/tasks/` — tracked work, state-by-folder: `open/ → in-progress/ → done/ | cancelled/` (ICOR **Output**). (`/task`)
- `ops/log/sessions.md` — chronological record of what happened/decided each session (ICOR **Refine**). (`/log`)

**Session start is context-scoped — read where you are, then surface what's open there:**

- **Workspace root (`C:\Dev`)** → the *workspace walk*: read `ops/tasks/in-progress` and `ops/tasks/open`, the unchecked items in `ops/TODO.md`, and the latest `ops/log/sessions.md` entry; surface open work and suggest a focus.
- **Inside a project (`customers/…` or `own/…`)** → the *project walk*: read that project's `CONTEXT.md` (plus any "Related contexts" it names) and surface unread `INBOX.md` entries before the first request. The workspace store is not re-walked here — the project is the frame.

**Session end — the log:** append a dated entry to `ops/log/sessions.md` — what was done, decided (link ADRs), tasks created/moved, and next focus.

This routine is tool-neutral: any LLM pointed at this folder can run it by reading the files — the scope is just "which folder did the session start in." The Claude harness only *accelerates* it: a `SessionStart` hook in `C:\Dev\.claude` fires the workspace walk automatically at root (it does not cascade, so it is naturally root-only), the cascading `CLAUDE.md` carries the project-walk rule into every project session, and `/todo` / `/task` / `/log` wrap the file edits. Remove the harness and the walk is still fully described here for any LLM to do by hand.

Note: `ops/TODO.md` (workspace action capture) is distinct from a project's `INBOX.md` (its curated cross-project knowledge feed, fed by `/brief`).

## Conventions

- **Scripts are ASCII-only.** Anything this workspace executes under Windows PowerShell 5.1 — `SessionStart` hooks, `.ps1` files, any script PS parses — must use ASCII punctuation: plain `-` (not `—`), straight quotes (not `“ ” ‘ ’`), `...` (not `…`). PS 5.1 reads BOM-less UTF-8 as Windows-1252, where an em-dash's bytes decode to a smart quote `”` that the tokenizer treats as a string delimiter, silently corrupting the parse. (Found 2026-06-15: the session-start hook had this latent bug and never ran.) Encoding-proof alternative if non-ASCII is unavoidable: save as UTF-8 *with* BOM. ASCII-only is simpler — prefer it.

## Status

Founding principle recorded 2026-06-11. Substrate relocated out of the harness folder to `ops/` (TODO capture + task store + session log) the same day. Remaining: the workspace conventions still live in `CLAUDE.md` and should migrate here so this file becomes the full operational doc a bare LLM can run from — tracked as a task. Until then, `CLAUDE.md` remains the fuller operational doc; this file is authoritative on portability.
