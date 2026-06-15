---
name: email-outlook-ready
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

The user composes in **Outlook (desktop, Windows)** by pasting. Markdown loses all formatting
on paste. So **every email you produce must also be emitted as a styled HTML file** whose
rendered content copies into Outlook with formatting intact.

## The rule

Whenever you draft an email the user will send:

1. Keep the readable source (Markdown in chat, and a `.md` file if the project tracks emails).
2. **Also write a standalone `.html` file** containing the **email body only**, using the
   inline-styled template below.
3. Tell the user the **subject line separately** as plain copyable text — do **NOT** put the
   subject inside the body HTML (they'd paste it into the message body by mistake).
4. Relay the copy workflow (below).

## Output location

- If the project has an `emails/` folder (or you're saving a `.md` source), write the `.html`
  **next to it with the same basename** — e.g. `emails/02-capacity-workspace-gateway.html`.
- Otherwise save it at the project root and tell the user the path.

## The copy workflow (relay this to the user)

> Open the `.html` file in a browser (Edge/Chrome) → **Ctrl+A** → **Ctrl+C** → click into the
> Outlook message body → **Ctrl+V**. Set the recipients and paste the subject line separately,
> then send.

The browser is what places rich text on the clipboard, so Outlook receives formatted content
rather than raw HTML.

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

## Note — direct-clipboard option (secondary, often unavailable)

A one-step "paste straight into Outlook" is possible by putting HTML on the Windows clipboard
via `System.Windows.Forms.Clipboard.SetText($html, [Windows.Forms.TextDataFormat]::Html)`
(requires an STA PowerShell session). This frequently fails from non-interactive / background
sessions, so the **HTML-file-and-copy workflow above is the reliable default**.
