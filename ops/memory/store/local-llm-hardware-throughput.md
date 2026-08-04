---
id: local-llm-hardware-throughput
ts: 2026-08-04T00:40:00Z
type: semantic
scope: workspace
source: session:a77891ac
tags: [ollama, llm, local-model, gpu, hardware, capacity-planning]
status: distilled
description: "Measured local-inference throughput: Arc 140V runs CPU-only under stock Ollama (~1.25 tok/s on a 12B); generation is memory-bandwidth-bound; what actually fits 16GB VRAM"
---

Numbers for deciding whether a bulk local-LLM job is feasible, measured 2026-08-03 on the
lineage description workload (see `lineage-business-descriptions`).

**Stock Ollama on Windows accelerates NVIDIA and AMD only.** The laptop's **Intel Arc 140V**
was not used: `ollama ps` reported `100% CPU` for `gemma4:12b`. Intel Arc needs the
**IPEX-LLM** fork of Ollama, which is a driver-level install with real setup risk.
Measured CPU-only: **~50 prompt tok/s, ~1.25 output tok/s** — about **30 s per described
object**, or **~24 h** for 2,840 objects. Two independent extrapolations (per-object and
per-token against the real corpus) agreed.

**Token generation is memory-bandwidth-bound**, so bandwidth predicts speed better than
core count: an RTX 5060 Ti 16GB is ~448 GB/s (GDDR7, 128-bit) against DDR5 at roughly
100 GB/s shared with everything else, and holds the whole model resident instead of
streaming weights. Expect roughly **35x** over CPU for a 12B — the 24 h job becomes under
an hour.

**What fits 16GB VRAM** at Q4, leaving ~3 GB for KV cache: a 12–14B (~7–9 GB) runs fast; a
20–24B (~12–14 GB) fits comfortably; a **27–32B does not fit** with usable context, and the
Q3 quant that would fit tends to damage exactly the long-instruction adherence you would be
buying it for.

**The non-obvious payoff of speed is not wall-clock, it is iteration.** At CPU rates a full
run is a one-way commitment, so the prompt has to be right first time; at GPU rates the
full corpus becomes a feedback loop you can re-run for free. For a task whose failures are
prompt-adherence rather than knowledge, that is worth more than extra parameters.

Always confirm acceleration with `ollama ps` before trusting an estimate — the `100% CPU`
field is what exposed the Arc problem, and nothing else in the output hints at it.
