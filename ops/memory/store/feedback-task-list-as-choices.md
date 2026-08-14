---
id: feedback-task-list-as-choices
ts: 2026-08-14T09:00:00Z
type: semantic
scope: workspace
source: session:carlras-datahub-2026-08-14
tags: [feedback]
description: "Asking for the open tasks means: render them as an AskUserQuestion choice card he can pick from, not as prose bullets"
---

**When Niels asks what the open tasks are, the answer is a choice card, not a list to read.**
"What are the open tasks", "what's open", the session-start task prompt, `/switch-task`-shaped
questions - all of them are him picking the session's work, so the reply must end in an
**AskUserQuestion card whose options are the tasks themselves**. A markdown bullet list forces him
to type the answer back; the card is one click.

**Rules:**
- The card carries the **task titles**, one per option, with the status and the concrete next step
  as the description. Not abstract labels.
- Recommendation still goes first, per [[feedback-closed-questions]] - the recommended task is
  option 1, marked "(Recommended)".
- The card caps at 4 options. When there are more tasks than that, put the **full numbered list in
  the prose above the card** and let the card carry the live candidates; "Other" takes any number
  from that list.
- Selecting an option means: set the active task (`/switch-task`) and start it. Don't ask again.

**Why:** 2026-08-14 (Carl Ras / datahub). Niels, to agent M: *"when i ask for this you should give
them to me as a list i can choose from."* The reply had listed all 10 open tasks as prose bullets
and closed with a written question.

**How to apply:** All agents, all sessions - M owns it in the continuity loop (session-start task
prompt). Consistent with [[feedback-interview-one-question]] (one question, card as the vehicle);
[[feedback-design-dialogue]] is unaffected - architecture talk stays prose.
