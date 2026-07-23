---
name: email-outlook-ready
bundle: custom
description: >
  Use this skill whenever drafting, writing, preparing, or "sending" an email for the user in
  ANY project. The deliverable for a drafted email is exactly ONE Markdown file (.md) with the
  subject line stated in the file - never chat text only, and never an HTML body or an Outlook
  launcher. The user opens the .md in VS Code preview, copies the rendered content, and pastes
  it into Outlook. Trigger on "draft an email", "write an email to X", "prepare the email",
  "send the email", "email about Y", or any request that produces email body text the user
  will send from Outlook.
---

# Email deliverable - one .md file

The user sends from Outlook. His workflow: open the `.md` in VS Code preview, copy the rendered
content, paste into Outlook. The rendered preview copies as rich text, so bold, bullets, and
links survive the paste. Nothing else is needed.

## The rule

Whenever you draft an email the user will send, emit **exactly one file**:

1. **`<basename>.md`** - the complete email as Markdown.
2. **State the subject in the file**, as the first line: `**Emne:** ...` (or `**Subject:** ...`
   in English). Then a blank line, then the body starting at the greeting.
3. Tell the user the file path. Do not open anything, do not produce `.html`, `.cmd`, or `.eml`
   files, and do not touch Outlook.

## Output location

- If the project has an `emails/` folder, write the file there: `emails/<nn>-<slug>.md`.
- Otherwise save at the project root and tell the user the path.

## Formatting

Keep to constructs that render cleanly in preview and paste well: paragraphs, `**bold**`,
bulleted lists, links. Bold "1." labels beat Markdown auto-numbering for numbered options.
Voice is governed by the `writing-voice` skill - use both.

Known caveat: copying from a preview under a dark theme can paste light-grey text into a white
Outlook body. If the paste comes out grey, switch VS Code to a light theme and re-copy.

## History

Until 2026-07-15 this skill produced an inline-styled `.html` body plus a `.cmd` launcher that
opened an Outlook draft via COM (`open-in-outlook.ps1`). Niels retired that pipeline: the .md
preview-and-paste route is easier. Do not reintroduce the HTML/COM path.
