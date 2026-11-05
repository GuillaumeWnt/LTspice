# Gemini / Antigravity Operational Directives for LTspice

## 1. Interaction Guidelines

- **Autonomous Simulation Diagnostics:**
  - When an LTspice simulation fails or halts prematurely, systematically inspect the `.log` file in the schematic directory.
  - Identify the exact convergence issue (timestep too small, singular matrix, floating node, missing model path) and suggest targeted, non-destructive fixes.
- **Circuit Design Integrity:**
  - Always verify ground connectivity (`Node 0`) and check for the common SPICE unit trap (`1M` = milli vs `1Meg` = mega).
  - Prefer automated verification using `.meas` directives and Python post-processing over manual inspection.
- **Python Automation Workflow:**
  - Always execute Python commands using **`uv`** (e.g. `uv run python ...`, `uv run pytest`).
  - Do not introduce untracked external dependencies without adding them via `uv add`.
- **MCP Bridge Utilization:**
  - Leverage the integrated `ltspice-mcp-bridge` for programmatic simulation control and live instance monitoring.
  - Use `brave-search` to find semiconductor datasheets, SPICE models, and application notes.
  - Use `memory` to persist key design decisions, component specifications, and simulation findings across sessions.
- **Git Commit Suggestion Mandatory:**
  - In accordance with workspace rule 5, **always** propose a concise, meaningful Git commit message suggestion at the end of every response where files are modified.
- **Rule Governance & Escalation:**
  - Never alter or add rules unilaterally without explicit prior confirmation from the user (rule 6).
  - If a rule or constraint becomes counter-productive, escalate it clearly to the user with a proposed modification.

---

## 2. Pointers to Core Documentation
- Architecture: [`.agents/rules/architecture.md`](architecture.md)
- Coding & Simulation Style: [`.agents/rules/coding-style.md`](coding-style.md)
- Testing & Diagnostics: [`.agents/rules/testing.md`](testing.md)
- Security & Hygiene: [`.agents/rules/security.md`](security.md)
- Engineering Philosophy: [`.agents/rules/general.md`](general.md)
