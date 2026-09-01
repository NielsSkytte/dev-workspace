# Browser fallback - driving the F&O grid, guarded

**This is the fallback, not the path.** Take it only when the Excel add-in paste is unavailable and
Niels has agreed to it for this run. Every rule below is a defect that already reached a production
journal on 2026-09-01.

## Before you start

- **Grant the site once.** `pingprod.operations.dynamics.com` returns *"Permission denied for this
  action on this domain"* until the extension has site permission. Do this first; discovering it
  mid-sequence costs a rebuild of the tab group.
- **Agree the blast radius out loud.** You are typing into a production ERP. Name the journal and the
  number of lines before the first click.
- **Prepare the full row set first**, in order, in text. Never derive a value between two clicks.

## The three rules that stop the known defects

### 1. Coordinates are valid for exactly one action

The F&O page **rescales between screenshots**. A coordinate read from screenshot N is not valid after
any action. On 2026-09-01 a stale coordinate put `0,75` into **`Rolle-id`** - error *"Der kunne ikke
findes en entydig Resource category view-post"*. The line had to be deleted and re-entered.

- Re-screenshot immediately before **every** click. No exceptions, no reuse, no "the page did not
  move".
- Prefer targeting by **element/text lookup** over pixel coordinates wherever the tooling allows it.
- Never batch several coordinate clicks from one screenshot.

### 2. Verify after every write, before the next one

- After typing a value, read it back from the field. `Timer` is typed and does not recompute, so a
  value that failed to land leaves the line silently wrong.
- After `Ny`, confirm a **new empty row** exists. A failed `Ny` **appends to the existing row** - that
  is how `600003600003` was produced.
- Watch the toolbar. `Kopier` sits next to `Linjer` and **the toolbar shifts at narrow widths**;
  `Kopier` fired twice where `Linjer` was aimed. Widen the window rather than aiming at a narrow
  toolbar.

### 3. One journal at a time, reconciled before the next

Enter one week's journal, reconcile its total against the prepared rows, then move on. A close that
is interrupted halfway - and it will be: the extension dropped twice and the tab group was rebuilt
three times in one session - must leave behind whole, reconciled journals, never a half-entered one.

## When it goes wrong

- **A bad value landed:** delete the line and re-enter it. Do not edit around it.
- **The extension dropped / screenshots time out:** stop. Do not resume mid-journal from memory;
  re-read the journal's current lines first and reconcile against the prepared rows before adding
  anything.
- **Anything ambiguous about an id:** Rule 0 in `SKILL.md` - it goes back to Niels.

## Selecting and approving

F&O acts on the **active row**, not the checkbox. Click the journal row itself before
`Godkendelse -> Finished`. Confirm the *"Kladden har aendret status til Finished."* message; an
unconfirmed approval is an unapproved journal.
