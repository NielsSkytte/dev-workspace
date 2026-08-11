---
id: skill-pingala-stream-maturity-matrix
ts: 2026-08-10T13:03:00Z
type: semantic
scope: workspace
source: user
tags: [skills, data-platform, maturity-matrix, architecture, pingala-visual-identity, M, Q]
status: distilled
description: "Created new general skill 'pingala-stream-maturity-matrix' for Agent M & Agent Q to track and report customer data platform progress across 6 Medallion stages with live data volume counts and DEV/TEST/PROD environment statuses."
---

**New Skill Created: `pingala-stream-maturity-matrix`**

**Location:** [`C:\Dev\.claude\skills\pingala-stream-maturity-matrix\SKILL.md`](file:///C:/Dev/.claude/skills/pingala-stream-maturity-matrix/SKILL.md)  
*(Linked to `.agents/skills` via NTFS junction for cross-tool discovery in Claude Code and Antigravity)*

### Key Capabilities & Rules:
1. **Per-Source Data Stream Isolation:** One matrix row per distinct origin system (e.g. separate `AX 2009 ERP` vs `CVR Register`).
2. **6-Stage Pipeline Standard:** `1. Source` $\rightarrow$ `2. Landing Zone` $\rightarrow$ `3. Raw (Bronze)` $\rightarrow$ `4. Enriched (Silver)` $\rightarrow$ `5. Curated (Gold)` $\rightarrow$ `6. Delivery & Activation`.
3. **Live Business Volume Metrics:** Displays actual data scale metrics (`324M Events`, `27.1M Rows`, `13 Tables`, `~450K Records`) on matrix nodes rather than internal engine code names.
4. **Environment Scope & Badging:** Top banner explicitly highlights workspace environment scope (`DEV & TEST WORKSPACES ONLY` vs `PROD LIVE`). Node badges use `TEST Live`, `Built & Staged`, `In Dev`, and `Planned`.
5. **State Persistence (`stream_matrix_data.json`):** Customer stream states and volume counts are stored in a lightweight JSON sidecar (`customers/<Customer>/<Project>/design/stream_matrix_data.json`) for zero-friction incremental updates.
6. **Pingala Branding Compliance:** Enforces `Aptos Display` headings, `Aptos` body text, Pingala color palette, prohibits cursive script fonts for technical callouts, and strictly bans internal agent persona names in deliverables.
