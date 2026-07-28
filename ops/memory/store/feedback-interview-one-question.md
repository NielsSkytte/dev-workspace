---
id: feedback-interview-one-question
ts: 2026-07-23T00:00:00Z
type: semantic
scope: workspace
source: session:1f323a74
tags: [feedback]
status: distilled
description: "Interviews: ALWAYS one question at a time, ideally as an AskUserQuestion choice card (pregiven answers + Other to chat); never batched question lists"
---

When interviewing Niels (clarification rounds, requirement gathering, design questionnaires),
ask **one question at a time**, ideally as an **AskUserQuestion choice card** with pregiven
answers — he either picks one or uses it as a springboard to chat. Never deliver a batched
list of questions.

**Why:** 2026-07-23 (DataCompare architecture interview) — the assistant delivered 15 questions
in one message (5 parts x 3 questions). Niels: "i cant use 15 questions in one go ... this 5 part
with 3-5 questions is close to useless, cant address all 15 in one answer." A batch forces him to
hold the whole list in his head; a card with options lets him answer fast or open a discussion.

**How to apply:** all agents, all sessions. When a task needs N answers, sequence N single
questions and adapt later questions to earlier answers. Use AskUserQuestion with a recommended
option where one exists. This *refines* [[feedback-design-dialogue]] rather than contradicting
it: exploratory design/strategy framing stays prose-first, but once the discussion reaches
enumerable clarification points (an interview), switch to one-card-at-a-time. The /new-project
interview style (one question at a time) is the model.
