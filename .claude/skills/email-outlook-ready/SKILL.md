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

The user renders the HTML **inside VS Code** (no browser) and copies from there:

> Open the `.html` in VS Code → press **Ctrl+Alt+V** (renders it in the embedded Live Preview) →
> click into the preview → **Ctrl+A** → **Ctrl+C** → paste into the Outlook message body
> (**Ctrl+V**). Set recipients and paste the subject line separately, then send.

After producing the file, **open it for the user** with `code -r "<path>.html"` so it's ready;
they press Ctrl+Alt+V. The embedded preview is a real browser render, so it puts rich text on
the clipboard — Outlook keeps the formatting. The explicit black-on-white styles in the template
matter here: a Markdown preview under a dark theme can paste invisible light-grey text.

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

- VS Code extension **`ms-vscode.live-server`** (Live Preview) — renders HTML inside VS Code.
- Keybinding in `…/Code/User/keybindings.json`: **Ctrl+Alt+V** →
  `livePreview.start.internalPreview.atFile`, scoped `when: resourceExtname == .html`.

If either is missing, install with `code --install-extension ms-vscode.live-server` and add the
keybinding. Note: Live Preview contributes no custom editor and no URI handler, so a file
**cannot be auto-rendered on open** from the CLI — the Ctrl+Alt+V keystroke is the closest to
"automatic" that's achievable.
