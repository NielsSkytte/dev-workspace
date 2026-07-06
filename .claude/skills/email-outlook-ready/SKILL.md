---
name: email-outlook-ready
bundle: custom
description: >
  Use this skill whenever drafting, writing, preparing, or "sending" an email for the user in
  ANY project. The user pastes email content into Outlook and needs the formatting (bold,
  bullets, headings, links, tables) to survive the paste. Plain Markdown does NOT — it pastes
  as literal asterisks and dashes. This skill makes every email deliverable an Outlook-ready
  HTML file the user can open and copy. Trigger on "draft an email", "write an email to X",
  "prepare the email", "send the email", "email about Y", or any request that produces email
  body text the user will send from Outlook.
---

# Email — Outlook-ready output

The user sends from **Outlook (classic desktop, Windows)**. The elegant path is to open the email
as a **ready-to-send, fully-formatted Outlook draft** with one double-click — no copy-paste. This
is done by rendering a styled HTML body into an Outlook draft via COM (`MailItem.HTMLBody` +
`.Display()`).

## The rule

Whenever you draft an email the user will send, emit **two files** next to the email source
(same basename) and open nothing yourself (see the background-session note):

1. Keep the readable source (Markdown in chat, and a `.md` file if the project tracks emails).
2. **`<basename>.html`** — the **email body only**, using the inline-styled template below.
3. **`<basename>.open-in-outlook.cmd`** — a one-line launcher that calls the shared
   `open-in-outlook.ps1` with this HTML and the subject (template below). The subject lives in
   the `.cmd`, NOT in the body HTML.
4. Tell the user to **double-click the `.cmd`** → an editable Outlook draft pops up → set
   recipients → Send.

## Output location

- If the project has an `emails/` folder (or you're saving a `.md` source), write both files
  **next to it with the same basename** — e.g. `emails/02-x.html` + `emails/02-x.open-in-outlook.cmd`.
- Otherwise save at the project root and tell the user the paths.

## The `.cmd` launcher template

```bat
@echo off
REM Double-click to open this email as a ready-to-send Outlook draft.
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Dev\.claude\skills\email-outlook-ready\open-in-outlook.ps1" -HtmlPath "%~dp0\<basename>.html" -Subject "Your subject here"
if errorlevel 1 pause
```

## IMPORTANT — do not run the launcher yourself

A Claude **background session has no interactive desktop**, so launching Outlook via COM from
here fails with `0x80080005 CO_E_SERVER_EXEC_FAILURE`. The launch must happen in the **user's**
session — i.e. the user double-clicks the `.cmd`. Don't try to demo it from the tool; just
produce the files and tell the user to double-click.

## Fallback — VS Code Live Preview (new Outlook / no COM)

The "new Outlook" app exposes no COM. If the draft launcher fails, fall back to copy-paste:

> Open the `.html` in VS Code → **Ctrl+Alt+V** (embedded Live Preview) → click in → **Ctrl+A** →
> **Ctrl+C** → paste into the Outlook body. Subject + recipients set manually.

The explicit black-on-white styles in the template matter here: a Markdown preview under a dark
theme can paste invisible light-grey text.

## HTML template (inline styles — body only)

Use inline styles only (Outlook ignores `<style>` blocks and CSS classes). Calibri matches the
Outlook default. Keep it simple: `<p>`, `<strong>`, `<ul>/<li>`, `<a>`, and `<table>` if needed.

```html
<!doctype html>
<html>
<head><meta charset="utf-8"></head>
<body>
<div style="font-family:Calibri,'Segoe UI',Arial,sans-serif; font-size:11pt; color:#000000; line-height:1.45;">

  <p style="margin:0 0 10px 0;">Hi all,</p>

  <p style="margin:0 0 10px 0;">Intro paragraph. Inline emphasis uses <strong>strong</strong>.</p>

  <p style="margin:0 0 4px 0;"><strong>1. Section heading</strong></p>
  <p style="margin:0 0 6px 0;">Section text.</p>
  <ul style="margin:0 0 10px 0; padding-left:22px;">
    <li style="margin:0 0 4px 0;">First bullet</li>
    <li style="margin:0 0 4px 0;">Second bullet</li>
  </ul>

  <p style="margin:0 0 10px 0;">Closing line.</p>

  <p style="margin:0 0 2px 0;">Thanks,</p>
  <p style="margin:0;">[Name]</p>

</div>
</body>
</html>
```

## Formatting rules

- Emphasis → `<strong>`. Bulleted items → `<ul><li>`. Numbered sections → bold `<p>` labels
  (Outlook auto-numbering is fragile on paste; explicit "1." text in a bold paragraph is safer).
- Links → `<a href="...">text</a>`.
- Tables → `<table style="border-collapse:collapse;">` with inline `border:1px solid #999; padding:4px 8px;` on `<td>/<th>`. Avoid for simple lists.
- No external CSS, no `<style>` blocks, no classes, no web fonts.
- Sizes in `pt`, not `px`.

## One-time prerequisites (already set up on this machine)

**Primary (Outlook draft):**
- Classic **Outlook desktop** (COM). Verify the class is registered; the "new Outlook" app has no COM.
- Shared helper **`open-in-outlook.ps1`** in this skill folder — reads the HTML, sets
  `HTMLBody`/`Subject`/`To`, and `.Display()`s an editable draft (never `.Send()`, so no security prompt).

**Fallback (VS Code Live Preview):**
- Extension **`ms-vscode.live-server`** — `code --install-extension ms-vscode.live-server`.
- Keybinding in `…/Code/User/keybindings.json`: **Ctrl+Alt+V** →
  `livePreview.start.internalPreview.atFile`, scoped `when: resourceExtname == .html`.
- Live Preview contributes no custom editor and no URI handler, so HTML **cannot be auto-rendered
  on open** from the CLI — Ctrl+Alt+V is the closest to "automatic" there.
