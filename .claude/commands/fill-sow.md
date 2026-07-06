# /fill-sow

Fill the Pingala SoW Word template from a content markdown file.

## Arguments
- `$ARGUMENTS` may contain: `<content.md> <output_name>`
- If not provided, ask the user for both paths before proceeding.

---

## Step 1 — Resolve paths

Ask the user:
1. Path to the content `.md` file (the source SoW content)
2. Desired output filename for the filled `.docx`
3. Path to the `.docx` template (default: `C:\Dev\own\SoWSkill\templates\Data_Statement of Work_work order.docx`)

---

## Step 2 — Read inputs

Read the content `.md` file in full. Parse it into named sections by matching `##` and `###` headings. The section names you will need to map are:

| MD section heading | Maps to template |
|---|---|
| `## Overview` | Overview table row 1 (Description/Extend), col 1 |
| `## Documents` | Overview table row 3, col 1 |
| `## Purpose` | Overview table row 4, col 1 |
| `## Vision & Goal` | Overview table row 5, col 1 |
| `## Criteria for Success` | Overview table row 6, col 1 |
| `## Workorder Scope` / `### Scope Details` | Workorder scope table row 1, col 0 |
| `## Activities` | Workorder scope table row 5, col 1 |
| `## ISVs` | Workorder scope table row 6, col 1 |
| `## [Customer] Specific Requirements` | Workorder scope table row 7, col 1 |
| `## Areas Not in Scope` | Workorder scope table row 8, col 1 |
| `## Organisation` | Organization table: map named contacts to the appropriate rows (see Organisation note below) |
| `## Further Definitions > Documentation` | Further definitions table row 1, col 1 |
| `## Further Definitions > Task System` | Further definitions table row 2, col 1 |
| `## Further Definitions > Output` | Further definitions table row 3, col 1 |
| `## Further Definitions > Prerequisites` | Further definitions table row 4, col 1 (append to existing intro text) |
| `## Estimates` | Estimates table rows 1–4 (activity + hours pairs) |
| `## High-Level Plan` | High-Level plan table rows 1–4 |

**Organisation table note:** The Organization table has multiple rows, each with a role label in col 0 and a name/contact placeholder in col 1. After filling the named contacts from Q3, **scan every row in the Organization table**. Any row whose col 1 still contains a `<...>` placeholder must be added to `unanswered` with the original placeholder text. Do not leave any `<...>` in the output — every placeholder must either be filled or flagged yellow.

For each section, extract the content as a list of plain-text lines:
- Strip markdown formatting: remove `**`, `*`, `_`.
- **Do NOT convert list markers to bullets.** Only use `•` if the source material explicitly uses `-` or `*` as a list item AND the content is genuinely enumerable. When in doubt, use plain line breaks instead.
- Preserve line breaks where the source has them. Do not collapse multi-line content into a single line.
- Do not invent or add any text that is not present in the source `.md` file. In particular, do not include any template instruction text (e.g. `<This template...>`, `<If Fixed Price...>`) — these are template artifacts, never content.

---

## Step 2b — Template discovery (scan for unmapped placeholders)

Run the following to list all `<...>` placeholders in the template:

```
python "C:\Dev\own\SoWSkill\sow_analyse_template.py"
```

From the output, identify any placeholder that:
1. Does NOT match the instruction patterns (i.e. not `<This template...>`, `<Please ...>`, `<If Fixed Price...>`, `<If need...>`, `<you might get inspiration...>`, `<The above is for inspiration...>`)
2. Is NOT already covered by the Step 2 mapping table above

For each such placeholder, ask the user:
> "I found `<placeholder text>` in [Table, row X col Y] — do you want to fill it, skip it (leave yellow), or ignore it (it will be removed)?"

Add any "fill" answers as extra `cells` entries in the mapping. Add any "skip" answers to `unanswered`. Do not proceed to Step 3 until all discovered placeholders are accounted for. If the discovery script is not available, skip this step and note it in the final report.

---

## Step 3 — Ask required questions

Apply these defaults silently unless the context suggests otherwise. Only ask if the answer is genuinely ambiguous or not determinable from the `.md` content.

**Q1 — Customer name** *(always ask — no default)*
"What is the customer's full legal name as it should appear in the document?"
→ Used to update all Company/Firma content controls.

**Q2 — Project type** *(default: Time & Material)*
Do not ask unless the `.md` explicitly mentions Fixed Price or the user raises it.
→ T&M (default): write `"Time & Material"` to Workorder scope row 2 col 1. The script's `clean_all_tables` call will remove the instruction placeholders in that cell automatically.
→ Fixed Price: replace with `"Fixed Price"` and keep the prerequisite note.

**Q3 — Named contacts** *(ask; mark unanswered if skipped)*
"Who are the named day-to-day contacts? Pingala contact name + Customer contact name."
→ Replaces `<apply name from customer and Pingala side>` in Organization row 1.
→ If skipped: add to `unanswered`.

**Q4 — Locations** *(ask; mark unanswered if skipped)*
"Onsite location for Pingala (city)? Onsite location for customer (city)?"
→ Replaces `<city, location>` and `<City>` in Further definitions row 4.
→ If skipped: add to `unanswered`.

**Q5 — Document History version bump** *(default: no)*
Do not ask unless the user raises it. Default is to NOT add a new Document History row.
→ If yes: ask for version number and brief description. Author = Pingala contact from Q3. Date = today's date.

**Q6 — Deliverables** *(pre-fill from .md; only ask if content is missing)*
→ Maps to Workorder scope table row 4, col 1.
→ If `## Workorder Scope` or `## Deliverables` is present in the .md, use that content directly without asking.
→ If absent: ask the user to provide it.

---

## Step 3b — Quality check each cell before writing

Before adding any cell entry to the mapping JSON, apply these checks:

1. **Coherence check**: Read the `content` array as if it were the final text in the Word cell. Does it make sense as standalone content — no dangling references, no half-sentences, no leftover template phrases? If not, revise.
2. **Formatting consistency**: All lines within a cell must follow the same style. Do not mix bullets and plain prose in the same cell. Do not mix numbered lists and bullets. Pick one style and apply it throughout.
3. **No stray placeholders**: Scan each line for any remaining `<...>` text. If found:
   - If it is a template instruction (matches `INSTRUCTION_PATTERNS` in the script) → exclude the line entirely.
   - If it is an unanswered data placeholder (e.g. `<city, location>`) → move the entire cell to `unanswered` instead of `cells`.
4. **No text injected between section heading and table**: The template has paragraphs between some headings and their tables. Do not add content to those paragraphs — only fill table cells.

---

## Step 4 — Build the mapping JSON

Construct a JSON object following this schema exactly:

```json
{
  "customer_name": "<answer to Q1>",
  "document_history": {
    "add_row": <true/false>,
    "new_row": {
      "version": "<new version>",
      "change": "<description>",
      "author": "<pingala contact>",
      "date": "<today YYYY-MM-DD>"
    }
  },
  "cells": [
    {
      "table": "<heading fragment matching the template section>",
      "row": <integer>,
      "col": <integer>,
      "content": ["line 1", "line 2", "..."]
    }
  ],
  "unanswered": [
    {
      "table": "<heading fragment>",
      "row": <integer>,
      "col": <integer>,
      "placeholder": "<original placeholder text>"
    }
  ]
}
```

**Table heading fragments** (must match the template exactly):
- `"Overview"` — for the pre-project overview table
- `"Workorder scope"` — for the scope table
- `"Organization"` — for the organisation table
- `"Further definitions"` — for the further definitions table
- `"Estimates"` — for the estimates table
- `"High-Level plan"` — for the plan table

**Important rules:**
- If a question was not answered, do NOT add a `cells` entry for it. Add it to `unanswered` instead.
- Always remove template instruction placeholders (lines starting with `<This template`, `<If Fixed Price`, `<you might get inspiration`, `<The above is for inspiration`, `<the section above is for inspiration`). Do this by not including them in `content` — the script removes them automatically.
- For Estimates: each line item is one entry in `content`, format: `"Activity description | X hours"`. The script maps these to the estimate table rows.
- If the .md has more estimate rows than the template has `<list>` rows, note this to the user — additional rows must be added manually.
- For Prerequisites row: prepend the standard intro text already in the template before adding content from the .md.

---

## Step 5 — Write mapping and run script

1. Write the mapping JSON to a temp file: `<output_dir>\sow_mapping_temp.json`
2. Run the fill script:
```
python "C:\Users\NielsSkytteChristens\.claude\tools\sow_fill.py" --template "<template_path>" --mapping "<temp_json_path>" --output "<output_path>"
```
3. Report what was filled, what was left unanswered (yellow), and any warnings from the script output.

---

## Step 6 — Report

Tell the user:
- Output file location
- List of sections filled successfully
- List of unanswered items (yellow-highlighted in the output)
- Any template rows that had no matching content in the .md (skipped)
- Reminder: open in Word and update the Table of Contents (Ctrl+A, F9) since TOC page numbers are field codes

---

## Design principles

- **Fill content, never touch formatting.** All text replacement happens inside existing runs or new runs that inherit the paragraph's formatting reference. Never modify styles, shading, borders, or column widths.
- **Unanswered = yellow highlight.** If a question is skipped or content is missing, the original `<placeholder>` stays with a bold yellow `NOT ANSWERED YET —` prefix. Never silently leave a blank.
- **Instruction placeholders are always removed.** Any `<...>` that starts with "This template", "If Fixed Price", "you might get inspiration", "The above is for inspiration", or "the section above is for inspiration" is removed from output — it is never client-facing.
- **Customer name via content controls only.** Never text-replace the customer name. Always use the Company content control update path in the script.
- **Template changes are handled by updating this skill file.** If the template gains a new row, add a new entry to the mapping table in Step 2. The script needs no changes.
- **No placeholder survives unflagged.** After building the full mapping, do a final pass: any `<...>` remaining in any `content` array that is not a template instruction must be moved to `unanswered`. A document with silent unfilled placeholders is worse than one with yellow highlights.
- **No bullets by default.** Use plain line breaks unless the source material explicitly lists items with `-` or `*`. Consistency within a cell is mandatory — never mix styles.
