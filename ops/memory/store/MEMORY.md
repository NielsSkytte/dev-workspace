# Memory Store — Index

Distilled, curated memory records (`ops/memory/store/`). Grouped by `tags` category.
This index is rebuildable from the records' frontmatter (`id` + `description`). Newest jobs
and the record shape live in [`../README.md`](../README.md).

## User
- [user-work-profile](user-work-profile.md) — solo consultant, Fabric/data platforms, Pingala A/S, context-switches frequently

## Feedback
- [feedback-design-dialogue](feedback-design-dialogue.md) — in architecture/strategy talks, discuss in prose; don't force AskUserQuestion cards
- [feedback-response-style](feedback-response-style.md) — terse/brief/full sticky keywords; default brief; no edit narration unless asked; "plainly" = prose, no headers/bullets/citations
- [feedback-commit-to-test](feedback-commit-to-test.md) — proactively offer commit+push when a push unblocks testing/deploy; user still approves (convention canonical in AGENTS.md)
- [feedback-version-bump-revisions](feedback-version-bump-revisions.md) — on a major revision to a versioned client doc (SoW/offer), bump the version + add a Document History row, unprompted
- [feedback-time-attribution-dev-to-project](feedback-time-attribution-dev-to-project.md) — project-rooted time always stays; Dev-rooted time clearly a project's gets reassigned to it (out of Dev only)
- [feedback-wrapup-commit-policy](feedback-wrapup-commit-policy.md) — at wrap-up//log always commit internal (personal) repos; DevOps/customer-facing repos always ask first
- [feedback-fact-only-language](feedback-fact-only-language.md) — never imply; facts only, inference labeled as inference; check claims against recorded evidence; prefer the smaller true statement
- [feedback-interview-one-question](feedback-interview-one-question.md) — interviews: one question at a time as AskUserQuestion cards (options + Other); never batched question lists; refines design-dialogue

## Project
- [workspace-design](workspace-design.md) — two buckets (own/customers), two types (content/function), focus field, scale
- [customer-project-two-tier](customer-project-two-tier.md) — customers/ is two-tier: customer node (map, never billable) wraps projects (work unit); session walk three-scoped
- [agent-framework](agent-framework.md) — 7 agents (fabric-back/semantic/fabric-front + content, architect, M, Q); fabric split at the semantic model; frontmatter required for invocation; skill=verb vs agent=role
- [knowledge-flow](knowledge-flow.md) — /brief command + INBOX.md for cross-project knowledge transfer
- [atomiccortex-vision](atomiccortex-vision.md) — LLM second brain; full-ICOR, portability-first (tool + scale), markdown+git, three horizons (solo->team of 10->org of 150)
- [skill-usage-evaluation](skill-usage-evaluation.md) — core goal: capture which skills fire/don't-fire/help and feed back into skill revision; the evaluative layer this memory system enables
- [time-tracking-system](time-tracking-system.md) — per-project time tracking at ops/time/; heartbeat+15/5 idle model, deterministic rollup, F&O codes, data gitignored (ADR-002); attribution TASK-FIRST since ADR-003
- [gitignore-data-folders](gitignore-data-folders.md) — `data/` ignored in every unit repo; secrets barred only from repos WITH a remote (local-only unit repos may hold them); ignoring never untracks
- [repo-vs-project-vs-task](repo-vs-project-vs-task.md) — a project is ONE F&O Project ID (repos live inside, several allowed); distinct workstreams are TASKS at user-story/ADO-work-item granularity; folder-per-task rejected (ADR-003, Carl Ras merge)
- [time-backfill-from-transcripts](time-backfill-from-transcripts.md) — recovering untracked hours from Claude Code transcripts: POINT events not turns, additive-only (never re-roll a timesheet), dedupe on work identity not Proj ID
- [time-reassignment-method](time-reassignment-method.md) — moving tracked time between projects: relabel heartbeats + re-run the 15+5 model for the hours, apply the DELTA to existing rows (never regenerate), cap at zero not negative, period total is the invariant
- [fno-time-entry](fno-time-entry.md) — entering time in F&O: one timesheet per internal company (PING/PNO01/Power, mapped live from ops/tidsreginfo.xlsx), Proj ID precedence + `(sheet)`/`conflict` marking, internal tracked but never entered, 5 h entry-consolidation vs /time's 2 h, and the DAY_CAP fill fix
- [eval-2026-08-03-fno-entry-page](eval-2026-08-03-fno-entry-page.md) — evaluative: every user-reported defect was affordance/visibility, every self-caught one was logic found via an invariant; presentation ships broken because there is no invariant to test it against; `overflow-x:auto` promotes overflow-y to auto and eats the wheel
- [dashboard-internal-hours-triage](dashboard-internal-hours-triage.md) — dashboard panel joining each Dev/own stretch to its session + turn text so internal time can be traced and redistributed; derive-only, choices in localStorage; active-task liveness now from heartbeats (live/idle/stale)
- [eval-2026-07-28-timetracking-rework](eval-2026-07-28-timetracking-rework.md) — evaluative: no skill fired (correct); dry-run-then-diff caught 2 of 3 self-inflicted errors on billing data; 3rd consecutive /log with local-summarizer overstatement
- [workspace-v1-frozen](workspace-v1-frozen.md) — v1.0 tagged 2026-07-06; setup phase OVER; freeze rule binding (no new capability without a demonstrated failure); success metric = INTERNAL-RND share collapsing
- [eval-2026-07-06-artifact-design](eval-2026-07-06-artifact-design.md) — evaluative: artifact-design fired+helped at the v1 review; domain skills correctly silent on a setup day
- [skill-writing-voice](skill-writing-voice.md) — writing-voice skill (DA/EN); subtraction-first AI-smell removal; built from Niels's thesis + email voice
- [skill-pingala-offer](skill-pingala-offer.md) — pingala-offer skill; trusted-advisor doctrine (no questions/decisions, build out, customer-state interview, budget-holder altitude, no capacity location)
- [skill-fabric-licensing](skill-fabric-licensing.md) — fabric-licensing skill; broad MS-Learn-cited Fabric licensing; owns the licensing facts (replaces the voice-example single-source)
- [eval-2026-07-07-pingala-offer](eval-2026-07-07-pingala-offer.md) — evaluative: pingala-offer fired+helped as verification gates at the Aeven offer; /fill-sow recipe lacked a Word-open verify step; writing-voice not loaded (borderline)
- [hooks-subdir-session-gap](hooks-subdir-session-gap.md) — FIXED 2026-07-28 for time/capture: user-level hook registration + in-script C:\Dev guard, all depths roll up (project/customer-node/Dev); Element Logic + DataCompare back-hours still manual; agent roster + snapshot still don't cascade
- [eval-2026-07-22-lineage-viewer](eval-2026-07-22-lineage-viewer.md) — evaluative: dataviz+pingala-visual-identity fired+helped (validator caught real brand failures); pingala-fabric-platform gap: layer-ID conventions undocumented (candidate skill update)
- [eval-2026-07-23-fabric-licensing-quota-gap](eval-2026-07-23-fabric-licensing-quota-gap.md) — evaluative: fabric-licensing helped via manual grep (trigger bypassed) and lacks quota coverage; capture-hook sanitizer broke its own rule 4 on /handoff (sentinel caught it + a fabricated-password summary)
- [eval-2026-07-28-datacompare-build](eval-2026-07-28-datacompare-build.md) — evaluative: pingala-fabric-platform + Python-over-PySpark default fired+helped (DataCompare Parts 1–2); one-card interview worked for 15 decisions; workspace agent roster (sentinel) doesn't load in project-rooted sessions
- [carlras-marketo-source-findings](carlras-marketo-source-findings.md) - Marketo mechanics all proven (incl. updatedAt filter); blocked instead by empty account objects + no ERP key on the person; schema != data
- [gtm-medallion-build](gtm-medallion-build.md) — Carl Ras datahub GTM medallion: Raw Python lakehouse (full history) → Enriched warehouse (house standard) → shared Warehouse_Curated (13-mo windowed fact) → DirectLake model + freshness report
- [eval-2026-07-28-carlras-fabric-folders](eval-2026-07-28-carlras-fabric-folders.md) — evaluative: pingala-fabric-platform fired+helped (GTM medallion) but GAP on item folder placement (fab mkdir → root, fab ls hides folders) caused a real misplacement; patched into skill; 2nd conventions-gap after lineage-viewer
- [eval-2026-07-30-env-discovery](eval-2026-07-30-env-discovery.md) — evaluative: pingala-fabric-platform never fired across ~70 turns naming its own triggers (D365 F&O extraction / Dataverse integration) — workspace skills-cascade vs trigger-miss unresolved; two self-caught reports of superseded numbers
- [tooling-promotion-customer-to-own](tooling-promotion-customer-to-own.md) — promoting reusable tooling out of a customer project into own/: what moves vs stays (owner's call), and the four wiring steps (two-way lineage, VS Code task, route it from the skill that owns the QUESTION, back-pointer); cross-repo move = copy + git rm, heal-repos.ps1 owns unit init
- [eval-2026-08-01-marketo-extraction](eval-2026-08-01-marketo-extraction.md) - evaluative: skills PRESENT in a project session and still silent on watermark/date-filter work (trigger miss confirmed at both scopes); three overreach/overclaim failures caught by the user
- [eval-2026-08-01-harness-cascade](eval-2026-08-01-harness-cascade.md) — evaluative: the 07-30 "skills never fired" mystery was never a trigger problem in project sessions — 16 of 26 project roots had no `.claude/` at all and none had `agents/`; check a capability is PRESENT before tuning how it is described; period-total invariant caught a 3.50 h phantom from a dict that overwrote instead of aggregating
- [eval-2026-07-31-skills-available-not-firing](eval-2026-07-31-skills-available-not-firing.md) — evaluative: at Dev root skills ARE loaded (listing reflected a live edit) and still didn't fire on Link-to-Fabric/Dataverse → 07-30's cascade-vs-trigger question narrowed to trigger-miss at workspace level; project-rooted leg still untested; local summarizer turned labelled inference into a bare fact (sentinel-class, sanitizer can't catch)

## Reference
- [pingala-psi-context-library](pingala-psi-context-library.md) — pingala/ mount = shared Pingala skills repo (other employees contribute), first company shared-brain attempt; not a workspace project
- [memory-arch-three-jobs](memory-arch-three-jobs.md) — Simon Scrapes video; Storage/Injection/Recall framing, cherry-picks Hermes/MemArch/GBrain, company-brain RLS; our memory direction
- [skill-creator-trigger-eval-limitation](skill-creator-trigger-eval-limitation.md) — its description-optimization loop gives no valid triggering signal on this Windows setup; crashes on emoji in SKILL.md
- [claude-auto-memory-disable](claude-auto-memory-disable.md) — why we disable native auto-memory: stops its rogue writes (the real collision with ops/memory) but not the ~11-16k-token preamble (open bug #63903); we disable+replace, Simon layers
- [workflow-large-return-timeout](workflow-large-return-timeout.md) — Workflow synthesis returning two big files via schema times out; files write to disk first (recoverable); prefer agent-Write or smaller returns
- [sow-fill-toolchain](sow-fill-toolchain.md) — SoW template + sow_fill.py traps: empty w:tc = Word "corrupt", Company controls data-bound to docProps/app.xml, header literal <Customer>; all fixed (unversioned in ~/.claude/tools); verify via Word COM + PDF probe
- [atomic-lineage-engine](atomic-lineage-engine.md) — reusable Atomic lineage engine at customers/ElementLogic/LineageDocumentation (sqlglot static parse + online enrichment, HTML viewer, query CLI); portable rules in atomic_rules.py; first stop for "where does column X come from" at any Atomic customer
- [pingala-palette-dataviz-conflict](pingala-palette-dataviz-conflict.md) — Pingala brand palette fails the dataviz validator (teal chroma+dE); use the validated chroma-boosted brand-hue sets (light/dark hexes inside) or re-derive with the same method
- [fabric-cu-quota](fabric-cu-quota.md) — Fabric regional CU quota: per-sub/region ceiling, 400 BadRequest on scale/create, portal request can auto-deny → support ticket, reservations never block scaling; check headroom in customer-setup requirements
- [fabric-directlake-guardrails](fabric-directlake-guardrails.md) — DirectLake per-table row guardrail by SKU (F2–F32 all 300M, F64 1500M), per-table/per-query, one over → whole model to DirectQuery; must read materialized tables not views; drives fact windowing
- [fabric-warehouse-ddl-pyodbc](fabric-warehouse-ddl-pyodbc.md) — run T-SQL against a Fabric warehouse from local: pyodbc + ODBC Driver 18 + `az` token (database.windows.net audience) via attrs_before{1256}; cross-db `[Lakehouse_X].[dbo].[t]` works; workspace-first alt to hand-authoring sqlproj
- [dataverse-fno-link-discovery](dataverse-fno-link-discovery.md) — which Dataverse envs are F&O-backed (properties.finOpsMetadata) and whether the export link is real Azure Synapse (datalakefolder.isexternallake) or Link to Fabric (extendedproperties LinkedToFabric); two pac-only PowerShell scripts + the pac/PS 5.1 traps
- [fabric-git-author-item](fabric-git-author-item.md) — author a Fabric item in the repo instead of the UI: `.platform` v2 folder shape, logicalId rules, Update-from-Git matches displayName+type and creates if absent; a plain .py is invisible
- [fno-vendor-gab-link-scope](fno-vendor-gab-link-scope.md) — the 13 F&O tables a vendor extract needs (VendTable alone = blank names, the GAB holds them); live-verified columns + `fab table schema` as the pre-code check
- [nordic-vendor-entity-resolution](nordic-vendor-entity-resolution.md) — matching vendors with no shared key: Splink/DuckDB vs Zingg/Spark, why suffix-stripping is dangerous across DK/SE/NO/FI, CVR is neither a VAT number nor unique
- [eval-2026-08-01-matas-datacompare](eval-2026-08-01-matas-datacompare.md) — skills fire only when hand-invoked; twice asserted a setup state instead of querying it with `fab api` already in hand
- [datacompare-match-engine](datacompare-match-engine.md) — DataCompare Part 3: pins > deterministic > fuzzy; ambiguous keys match nothing, match_xref is sticky (only a pin repoints), fuzzy proposes only; equal-weight scoring gated on the leading field because cfg.match_rule has no weights column
- [eval-2026-08-03-matas-part3](eval-2026-08-03-matas-part3.md) — claude-in-chrome skill skipped in favour of loading its tools; the browser-identification doctrine it carries is what the owner then had to ask for
