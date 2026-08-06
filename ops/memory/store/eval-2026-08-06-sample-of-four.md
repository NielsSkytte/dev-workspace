---
id: eval-2026-08-06-sample-of-four
ts: 2026-08-06T09:05:00Z
type: evaluative
scope: project:customers/ElementLogic/LineageDocumentation
status: distilled
source: session:a77891ac
tags: [evaluation, method, memory-fidelity, llm-evaluation]
description: "Declared a causal conclusion from 4 uncontrolled observations, then disproved it myself one turn later; the memory record kept the retracted hypothesis as fact"
---

**The miss.** Four objects overlapped between a CPU and a GPU run of the same
model, and the CPU output was slightly better on both that differed. I wrote:
*"grouping is a quality lever, not just a throughput knob"* — a causal claim from
four observations, with **two variables changed at once** (group size 8→6 and
context 8192→16384). The next turn ran the controlled test: **18 of 20 outputs
byte-identical**. The claim was wrong and I retracted it.

Catching it one turn later is the process working — but the claim should not have
been stated as a finding in the first place. The honest form was available and
cheap: *"the CPU run differed on two of four overlapping objects; two variables
changed, so this needs a controlled run."* Same information, no false conclusion.

**Why it matters beyond the moment: the memory substrate kept the wrong version.**
`daily/2026-08-04.md` record 7 reads *"indicating grouping as a quality lever, and
the fabrication was confirmed"* — the retracted hypothesis, preserved as fact,
with no trace of the retraction. A future session reading that record inherits a
belief I disproved. **A per-turn summarizer captures claims, not their fate**, so
anything asserted and later withdrawn within a session survives only in its
asserted form. That is an argument for stating hypotheses as hypotheses in the
user-facing text, not just in the reasoning — the record is built from what was
said.

**Same session, related:** record 9 attributed my own name-matching bug to
*"Mistral's DAX implementation"*, inverting responsibility for a defect I had
explicitly called mine. Six of eleven records carried fidelity flags — the worst
rate logged so far, and the sixth consecutive `/log` containing a fabricated
completed action.

**Rule earned:** before writing a causal claim into user-facing text, check
whether more than one variable moved. If it did, the sentence is a hypothesis and
must be worded as one.
