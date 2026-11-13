---
id: sowskill-examples-not-anonymised
ts: 2026-11-13T08:40:00Z
type: semantic
scope: project:own/SoWSkill
source: session e7a5320e
tags: [sowskill, customer-names, publish]
status: distilled
description: "own/SoWSkill: examples/CustomerX_Data_Platform_SoW_v2.* and templates/Data_Statement*.docx contain a real customer's name; keep them out of any staff-facing publish"
---

Checked 2026-11-13 before publishing to Atomic Tools: `examples/CustomerX_Data_Platform_SoW_v2.md`
and `.docx` (35 hits) and `templates/Data_Statement of Work_work order*.docx` (25 and 40 hits) name
Joe & The Juice, despite the "CustomerX" name and CLAUDE.md calling the examples anonymised. The
other examples and the EN/DA templates have none. They are in own and AAI (both private), not in
Atomic Tools. A check of a .docx must decode `&amp;` first: the `&` in the name is escaped in the XML.
