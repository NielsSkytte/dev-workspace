---
id: atomiccortex-vision
ts: 2026-06-10T08:49:43Z
type: semantic
scope: workspace
source: session:32ff9b4b-b739-4f3d-b024-73a217f9f77e
tags: [project]
status: distilled
description: "AtomicCortex second-brain project — three-horizon vision, governing portability constraint, and agreed charter direction"
---

Niels is building **AtomicCortex** (`own/AtomicCortex`), an LLM-driven "second brain" — a joined personal knowledge + project system. Direction agreed 2026-05-31 (charter still being ratified):

**Scope:** Full **ICOR / myPKA** model — knowledge AND project management, joined in one model (NOT a knowledge-only brain separate from projects). Essentially a more developed version of the existing workspace's own/customers × content/function split. See [[workspace-design]].

**Scope refinement (2026-06-10) — three distinct entities, two of them LLM systems:**
1. **Atomic** = the *customer product* Pingala sells: rapid Fabric data-platform deployment (Dynamics F&O first — prebuilt data structures, semantic models, soon standard reports; more sources later). NOT an LLM system — it's the subject matter.
2. **AtomicCortex** = an *internal LLM-driven system* whose purpose is to develop/operate Atomic. Team/business scope; shareable to the team of 10.
3. **Personal PKA** = Niels's own myPKA-like second brain, *separate* from AtomicCortex but able to interact with / utilise it. Private, never ships. Currently this **is** the DEV workspace (`.claude/` + memory + M/Q). Some DEV capabilities (notably certain skills) belong in AtomicCortex and will migrate later — deferred.
This SUPERSEDES the earlier "personal AND business joined in one brain" framing: personal and business are **peer systems**, not one model. The current DEV workspace (with M/Q etc.) is Niels's first attempt and currently *welds* the two — `own/AtomicCortex` is nested inside the personal workspace.
Answer (ratified 2026-06-10 in **ADR-0001**, `own/AtomicCortex/docs/decisions/0001-atomiccortex-is-a-system-not-a-project.md`): **one spec, many instances, federated at seams** — shared substrate spec + generic skills = the "one"; separate repos/scope/lifecycle = the "separate"; a selective federation seam (personal mounts Cortex, can dispatch into it) = the connection. The personal↔Cortex seam reuses the org-federation connector mechanism one scale early. Discipline now: stop welding (keep content separable, write skills to the shared spec), split repos only when the team horizon arrives.

**Governing constraint — PORTABILITY (two kinds):**
1. *Tool portability* — structure is the asset, the LLM is a replaceable worker. Must be able to switch Claude→Gemini and offload parts to a local LLM (cost + privacy).
2. *Scale portability* — same substrate must survive three horizons: (1) solo now; (2) a team of 10 Fabric specialists with "Atomic" as a product; (3) federate/plug into a ~150-person org's corporate LLM memory layer while retaining their own (selective skill sharing / memory connection).

**Key architectural decisions (proposed/agreed):**
- **Markdown-first, NO database as source of truth.** Optional rebuildable semantic index (Open Brain idea) kept on the shelf — never load-bearing. Open Brain's protocol idea is reserved for the *org-federation seam* only, not the core.
- **Substrate = markdown in git from day one** (not a plain folder) — this is what makes solo→team→org nearly free. Team = shared repo; org = federation connector at the seam.
- **Synthesis = Karpathy LLM-Wiki pattern** (pre-synthesize at ingest, cross-linked pages; not RAG-at-query). Already seeded in AtomicCortex.
- **Tool-neutral instruction/schema file** (AGENTS.md convention, NOT a load-bearing CLAUDE.md).
- **Substrate vs Harness split:** harness features (Claude Code skills, scheduled reflection, MCP) allowed only as NON-load-bearing accelerators. Acid test: delete the harness, point a bare LLM at the folder — knowledge must remain fully intact and usable.
- **Three-way separation enforced from day one:** Structure/Schema (= "Atomic" the product, shippable) · Skills/Harness (packageable capabilities) · Content (knowledge, layered personal/team/org). Cheap now, expensive to retrofit.
- **Discipline: "seams not welds."** Build only the solo layer now; never build team/org features until that horizon arrives, but never weld a seam shut.

**Inspirations studied (2026-05-31):** Karpathy LLM Wiki (pre-synthesis > RAG) · myPKA/ICOR by Tom (north star) · Ben AI / Ben van Sprundel (reflection cycles, skills, layered memory — but most Claude-locked) · Simon Scrapes Agentic OS (multi-file KB + automation) · Nate B Jones Open Brain/OB1 (DB+embeddings+MCP federation — used only at the org seam). Builds on [[knowledge-flow]] and [[user-work-profile]].
