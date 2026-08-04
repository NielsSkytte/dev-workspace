---
id: ollama-remote-gpu-lan
ts: 2026-08-04T00:35:00Z
type: procedural
scope: workspace
source: session:a77891ac
tags: [ollama, llm, local-model, gpu, windows, networking, privacy]
status: distilled
description: "Run Ollama on another PC's GPU over the LAN: OLLAMA_HOST binding + tray restart + stale explorer env + firewall; Ollama has NO auth, so LAN-binding puts the payload on the wire"
---

Offloading local inference to a second machine's GPU. Server side, in order:

1. `ollama pull <model>`; check `ollama --version` — a 50-series card (Blackwell, sm_120)
   needs a build with CUDA 12.8+.
2. Ollama listens on **`127.0.0.1` only** by default and will silently refuse LAN clients.
   Set user env `OLLAMA_HOST`. Prefer the machine's own LAN address
   (`setx OLLAMA_HOST "192.168.x.y:11434"`) over `0.0.0.0` so it is not offered on VPN
   adapters and Hyper-V switches too.
3. **Fully quit Ollama from the system tray and relaunch** — it does not re-read the
   environment while running. Then verify in a *new* terminal with `echo $env:OLLAMA_HOST`:
   a running `explorer.exe` can hand a **stale environment block** to child processes, in
   which case sign out and back in. This is the step that looks done but isn't.
4. `New-NetFirewallRule -DisplayName "Ollama LAN" -Direction Inbound -Protocol TCP
   -LocalPort 11434 -Action Allow -Profile Private` (elevated).
5. `ollama ps` must report **`100% GPU`**, not `100% CPU`. This single field is the check
   that catches an unaccelerated card — see `local-llm-hardware-throughput`.

**Client side:** point at `http://<ip>:11434/api/chat`. Preflight any long run against
`/api/tags` — it proves reachability *and* that the model is pulled there, turning a
firewall block into an immediate actionable error instead of a silent stall an hour in.

> **Ollama has no authentication.** Binding it to the LAN lets anyone on that network use
> the API, and the request payload is whatever you are processing — for customer work that
> is customer data on the wire. Keep it on the `Private` firewall profile, never Public or
> guest. This does not undo a "keep it local" privacy argument, but it is a different
> posture from loopback-only and should be stated as such.
