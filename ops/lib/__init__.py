"""Shared read layer for the ops scripts.

`dashboard.py`, `bin/daybrief.py`, `time/rollup.py` and `time/value.py` are renderers
over one workspace data model: markdown files with frontmatter, project folders, and
the heartbeat record. This package is that model's read side, single-sourced so a
change to the substrate format is one edit rather than four.

Derive-only, in the sense of Guardrail 7: nothing here stores knowledge, it only reads
what the substrate already holds. Pure stdlib, ASCII-only, no state.

  substrate   markdown + frontmatter parsing
  workspace   project and customer discovery, billing grain, task lookup
  heartbeats  the raw measurement record
"""
