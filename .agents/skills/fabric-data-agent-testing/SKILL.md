---
name: fabric-data-agent-testing
bundle: custom
description: >
  How to test, evaluate, and regression-guard a Microsoft Fabric Data Agent using the
  `fabric-data-agent-sdk` Python evaluation harness. Use this skill whenever someone needs to
  measure whether a Fabric data agent answers correctly, build a validated ground-truth
  question/answer set, run `evaluate_data_agent`, score answers with an LLM judge, validate the
  agent's few-shot example queries, or set up regression testing so a change to the semantic
  model or the agent config doesn't silently break answers. Trigger on "test my data agent",
  "evaluate the data agent", "is the agent answering correctly", "ground truth for the agent",
  "regression test the agent", "did the model change break the agent", "validate my example
  queries / few-shots", "accuracy of the data agent", or any request about quality-gating or
  CI-ing a Fabric data agent. This is the companion to `fabric-data-agent` (design/build) and
  `fabric-data-agent-ops` (capacity, logging, git/CI). Use it even if the user only asks about
  one piece (e.g. just "how do I write a critic prompt" or "how do I check my few-shots").
---

# Testing & Evaluating a Fabric Data Agent

For a production data agent, "it looked right in the chat pane" is not a quality gate. Fabric
ships a Python evaluation harness in the `fabric-data-agent-sdk` that scores the agent against a
**validated ground-truth set** using an **LLM judge**. This skill covers building that set,
running the harness, reading results, validating few-shots, and wiring regression into the
lifecycle.

Companion skills: design/build → `fabric-data-agent`; capacity/logging/git → `fabric-data-agent-ops`.

## The two artifacts people confuse — keep them separate

| | Few-shots / verified answers (the agent's *crib sheet*) | Ground-truth test set (the *exam*) |
|---|---|---|
| What | question → **query** (few-shots) or question → **approved visual** (verified answers) | question → **expected final answer** |
| Purpose | **improve** the agent — retrieved at runtime and fed into generation | **measure** the agent — scored, never fed to it |
| Lives | in the agent/model config (Git) | in your test notebook (a DataFrame/CSV), held out |
| API | `datasource.add_fewshots(...)`; Prep-for-AI verified answers | `evaluate_data_agent(...)` |

**Why both, and why held-out:** few-shots and verified answers are *inputs the agent sees*. If
you evaluate against those same examples, you're grading the agent on its own crib sheet. A
**separate, held-out** ground-truth set is the only way to get an unbiased score across config
changes, model edits, deployments, and the periodic LLM updates Microsoft ships under the agent.

## Building the ground-truth set

- Pull from **real user questions** (the 15–30 you gathered when scoping — see `fabric-data-agent`).
- Each row: a clear, **unambiguous** question and the **correct final answer** (a number, a short
  string, a small set). Keep answers stable — pick questions whose answers don't drift daily, or
  pin a date range in the question.
- Make questions **distinct and non-overlapping**; cover the hard patterns (fiscal calendars,
  multi-source routing, disambiguated measures), not just easy lookups.
- Keep the test set **out of** the agent config. Version it next to the agent in Git so a
  reviewer can see test + config + model together.

> **Field practice — the first run debugs your *test set*, not the agent.** Luca Zavarella audited
> every `false`/`unclear` row in a 72-question benchmark and found most early "failures" were bad
> ground-truth values, ambiguous phrasing, or casing rules — not agent mistakes; after fixing the
> *benchmark*, accuracy reached 97.2%. Treat run #1 as a way to clean the exam: inspect every
> non-pass row before blaming the agent.
> ([Zavarella, 2026](https://medium.com/data-science-collective/we-built-the-benchmark-now-lets-evaluate-the-fabric-data-agent-for-real-a8ffef236693))

```python
import pandas as pd
ground_truth = pd.DataFrame(
    columns=["question", "expected_answer"],
    data=[
        ["Total sales for Canadian Dollar in January 2013", "46,117.30"],
        ["Total sales outside the US", "19,968,887.95"],
        ["How many active customers in Q1 FY2024?", "12,540"],
    ],
)
```

## Running the evaluation (Fabric notebook)

> **Pin the SDK version in any automation.** It ships as alphas (`0.1.xxaN`) and has shipped
> breaking changes: versions 0.1.12a0–0.1.14a0 broke `create_data_agent`/`add_datasource` (fix
> was downgrading to 0.1.11a0), and field names have been renamed across releases (see below). A
> blind `%pip install` can pull a broken or behavior-shifted build mid-pipeline.

```python
%pip install fabric-data-agent-sdk==0.1.25a0   # pin; latest verified at time of writing
from fabric.dataagent.evaluation import (
    evaluate_data_agent, get_evaluation_summary, get_evaluation_details,
)

evaluation_id = evaluate_data_agent(
    ground_truth,
    "ProductSalesAgent",            # data_agent_name (positional)
    workspace_name=None,            # optional: agent in another workspace
    table_name="agent_eval_run",    # output tables; default "evaluation_output"
    data_agent_stage="production",  # "production" (default) or "sandbox"
)

summary = get_evaluation_summary("agent_eval_run", verbose=True)
# -> total questions, counts of true / false / unclear, accuracy

details = get_evaluation_details(
    evaluation_id, "agent_eval_run",
    get_all_rows=False,   # False = only wrong/unclear; True = everything
    verbose=True,
)
# -> question, expected_answer, actual_answer, evaluation_result (true/false/unclear), message_url
```

> **Field correction — the column was renamed.** On SDK ≥ 0.1.17a0 (Jan 2026) the per-row link
> field is **`message_url`**, not `thread_url`. Older notebooks referencing `thread_url` return
> nothing on current SDKs — another reason to pin the version.

Outputs: two Delta tables — `<table_name>` (summary) and `<table_name>_steps` (per-step
reasoning/execution). The portal also has a **Diagnostics** button that downloads a full config +
execution snapshot for a run.

### The judge is an LLM, not exact-match

By default the harness uses a built-in **critic** prompt to decide whether the actual answer is
*equivalent* to the expected one — so `"46,117.30"` and `"46117.3 CAD"` can both pass. Override it
when your domain needs specific judging rules. The custom prompt **must** contain the three
placeholders `{query}`, `{expected_answer}`, `{actual_answer}`:

```python
critic_prompt = """
Given the query, expected answer, and actual answer, decide if the actual answer is
equivalent to the expected answer. Numbers within 0.5% are equivalent. Respond 'yes' or 'no'.
Query: {query}
Expected Answer: {expected_answer}
Actual Answer: {actual_answer}
"""
evaluation_id = evaluate_data_agent(ground_truth, "ProductSalesAgent", critic_prompt=critic_prompt)
```

**Casing and number/currency formatting are the #1 source of false negatives** — the default
critic is lenient but ambiguous about them. Practitioners who audited the default judge found
encoding explicit formatting rules in `critic_prompt` ("numbers within 0.5% are equal; ignore
casing and thousands separators") materially improved reliability *without* touching the agent
([Zavarella, 2026](https://medium.com/data-science-collective/we-built-the-benchmark-now-lets-evaluate-the-fabric-data-agent-for-real-a8ffef236693)).

Because the judge is itself an LLM, treat a single run as noisy: investigate `unclear` and `false`
rows via their `message_url`, and re-run borderline cases. The SDK exposes **no** "repeat N times"
parameter — call `evaluate_data_agent` repeatedly and aggregate yourself for a stability read.

> **Eval-validity trap — the SDK path can be "dumber" than the UI.** Microsoft support has
> confirmed that SDK/programmatic consumption *doesn't automatically pull in all the semantic-model
> context the Fabric UI injects*, so the same agent can answer **worse via the SDK than in the
> portal** (e.g. filtering by the wrong column). Since `evaluate_data_agent` runs through that same
> path, your eval can flag failures a real UI user would never hit — or miss issues UI users do.
> Make the eval representative of how users actually consume the agent, and if you ship SDK/MCP
> consumption, inject key model descriptions/filters into the client `instructions`.
> ([Fabric Community + MS CSS, 2025](https://community.fabric.microsoft.com/t5/Fabric-platform/Fabric-Data-Agent-answers-wrongly-through-SDK-but-not-through-UI/m-p/4834076))

## Validating the few-shots (the crib sheet) — separate check

Bad or conflicting example queries quietly degrade generation. Validate them **before** they ship,
independently of the end-to-end eval. The validator is **SQL-only** today.

```python
from fabric.dataagent.evaluation import evaluate_few_shot_examples, cases_to_dataframe
import openai

examples = [{"natural language": "How many employees?", "sql": "SELECT COUNT(*) FROM dbo.dimemployee"}]
result = evaluate_few_shot_examples(
    examples, llm_client=openai, model_name="gpt-4o",
    batch_size=20, use_fabric_llm=True,
)
print(result.success_rate, result.success_count, result.total)
failures = cases_to_dataframe(result.failure_cases)   # inspect + fix conflicts
```

Use this to catch contradictory pairs and low-clarity questions. Function name is
`evaluate_few_shot_examples` (not `evaluate_few_shots`).

Two SDK-versioning gotchas that bite few-shot work specifically:
- The validator's **judge model changed across releases** (gpt-4.1 → gpt-5.1 in 0.1.25a0), so a
  validation verdict can flip on an SDK upgrade alone — pin the version for reproducible results.
- `add_fewshots()` now **auto-renames duplicate questions with `[N]` suffixes** (fixed in
  0.1.23a0) instead of colliding — harmless, but the `[1]`/`[2]` suffixes show up in `fewshots.json`
  and can surprise a reviewer diffing the Git config.

## Regression: the gate that protects production

The agent's answers depend on three things that all change over time: the **semantic model /
Prep for AI**, the **agent config**, and the **platform LLM** Microsoft updates underneath you.
Any of them can silently move answers. So:

1. **Keep the ground-truth set in Git** beside the agent and model.
2. **Re-run `evaluate_data_agent` on every change** to the model or agent — this pairs with the
   "model changed → re-test before merge" rule in `fabric-data-agent-ops`. Compare the new
   accuracy and the per-question results to the last run.
3. **Schedule a periodic run** (e.g. weekly/monthly) even with no config change. Practitioners
   report **"mapping drift"**: an agent maps a question to the right columns for days, then —
   with no change to data, schema, or instructions — starts mapping it differently, apparently
   from Microsoft's underlying model updates. **There is no version pinning to lock agent
   behavior**, so a recurring baseline battery is the only way to catch drift before stakeholders
   do. ([Tejwani, 2026](https://pub.towardsai.net/fabric-data-agents-just-hit-ga-94f459c68dcc))
4. **Fail the gate** on accuracy regression or any previously-correct question flipping to
   `false`. Investigate via `message_url` / Diagnostics before merging or shipping.

Automate by running the eval notebook from a Fabric pipeline or an Azure DevOps pipeline (the
SDK runs in-notebook). Service principals are fully supported for ALM; SPN **runtime** querying
is now in **preview** (was user-identity-only) — see `fabric-data-agent-ops`. Note the evaluation
harness calls the agent, so the same Assistants-API → Responses-API deadline (**26 Aug 2026**)
applies to long-lived eval automation.

## Sources

- Evaluate your data agent: https://learn.microsoft.com/en-us/fabric/data-science/evaluate-data-agent
- SDK overview: https://learn.microsoft.com/en-us/fabric/data-science/fabric-data-agent-sdk
- Example queries / few-shot validator: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-example-queries
- fabric-toolbox checklist notebooks: https://github.com/microsoft/fabric-toolbox/tree/main/samples/data_agent_checklist_notebooks
