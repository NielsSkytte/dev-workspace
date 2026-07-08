---
id: sow-fill-toolchain
ts: 2026-07-08T00:00:00Z
type: procedural
scope: workspace
source: session:003da8cc (/log distill, Aeven offer session)
tags: [sow, fill-sow, word, docx, tooling, pingala-template]
status: distilled
description: Pingala SoW Word template + sow_fill.py facts learned rendering the Aeven offer — three Word-breaking traps fixed, one still open
---

Facts about the `/fill-sow` toolchain (`~/.claude/tools/sow_fill.py` + the Pingala SoW template),
established 2026-07-07/08 while rendering the Aeven ServiceNow POC offer v1.0 (first end-to-end
run to a Word-verified output):

1. **Empty table cell = "corrupted" file.** A `w:tc` must contain at least one `w:p`. The
   instruction-placeholder cleaner could remove a cell's only paragraph; Word then refuses the
   whole file as corrupt (python-docx reopens it fine, so the defect is invisible without a Word
   open test). Fixed in `remove_instruction_paragraphs` (keep/append an empty `w:p`).
2. **Customer name is data-bound.** The template's 21 Company content controls bind to
   `docProps/app.xml` `<Company>` (store GUID `{6668398D-A668-4E3E-A5EB-62B293D839F1}`); Word
   refreshes them from there on open, silently reverting inline `w:t` edits. Fixed:
   `update_company_property` rewrites app.xml in the saved package.
3. **Page header holds a literal `<` `Customer` `>` run triplet** (not a control) — one
   occurrence, rendered on every page. Fixed: `update_customer_name` now sweeps headers/footers.
4. Still open: `C:\Dev\own\SoWSkill\sow_analyse_template.py` has a hardcoded stale template path
   (`c:\Dev\Projects\Joe\...`) — scan inline instead, or fix it next time it's needed.
5. `~/.claude/tools/` is **not a git repo** — the sow_fill.py fixes are unversioned.
6. Template estimates table has 4 `<list>` rows; more activities require row duplication
   (deepcopy `w:tr`), and `w:rPr` children are schema-ordered (e.g. `w:b` before `w:highlight`)
   — Word rejects out-of-order run properties.

Verification recipe that caught all of this: after fill, open the docx via Word COM
(`Documents.Open`), update fields/TOC, export PDF, then probe the PDF text (pypdf) for leftover
`<...>`, question marks, and the customer name.
