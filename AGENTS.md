# AGENTS.md — Global Directives for AI Agents

> **Project Purpose:** Professional, modular, and high-performance LTspice simulation & electronics engineering automation workspace.
> **Scope:** These directives apply to all AI coding assistants (Google Antigravity, Claude, GitHub Copilot, OpenAI Operator, etc.).

---

## 1. Core Principles

1. **Multi-Project Separation & Modularity:**
   - This workspace serves as a centralized hub managing multiple independent LTspice simulation projects.
   - All circuit subprojects reside in the dedicated directory `Projets/<project-name>/` (with `sim/`, `docs/`, `sim/blocks/`).
   - Shared third-party SPICE models (`.lib`, `.sub`, `.mod`), custom vendor symbols (`.asy`), and shared graphical hierarchical blocks (`.asc` + `.asy`) reside exclusively in `_Shared_Lib/` (`sym/`, `models/`, `common_blocks/`).
   - Heavy simulation generated outputs (`*.raw`, `*.log`, `*.fft`) are routed to `_Build_Temp/` and gitignored.
   - Reusable Python automation libraries reside in `src/ltspice/` and are packaged with `uv`.

2. **SPICE Simulation & Netlist Conventions:**
   - **Ground Reference:** Node 0 (`GND`) must always be explicitly defined and connected.
   - **SPICE Units & Notation Pitfall:**
     - Always remember: `1M` or `1m` denotes **milli** ($10^{-3}$).
     - **Mega** ($10^6$) must strictly be written `1Meg` or `1meg`.
     - Standard engineering prefixes: `f` (femto), `p` (pico), `n` (nano), `u` (micro), `m` (milli), `k` (kilo), `Meg` (mega), `g` (giga), `t` (tera).
   - **Component Categorization (The 3 Cases):**
     - *Case 1 (Simple `.MODEL`):* Standard LTspice symbol + `.mod` in `_Shared_Lib/models/` + `.lib nom.mod`.
     - *Case 2 (Manufacturer `.SUBCKT`):* Symbol `Cell` in `_Shared_Lib/sym/` with `Prefix: X`, `Value: <nom>`, `ModelFile: <fichier.lib>`, and `Netlist Order` matching the `.SUBCKT` line.
     - *Case 3 (Hierarchical Graphic Block):* Pair `.asc` + `.asy` with identical names in `_Shared_Lib/common_blocks/` or `sim/blocks/`. Symbol type `Block` with empty attributes and pin labels matching F4 ports.
   - **Explicit Node Naming:** Always label critical circuit nets (`VIN`, `VOUT`, `SW`, `FB`, `GATE`, `CLK`, etc.) rather than relying on auto-generated node numbers (`N001`, `N002`).
   - **Automated Validation (`.meas`):** Use `.meas` directives for extracting key figures of merit (efficiency, ripple, bandwidth, rise time, overshoot) directly into the simulation log.

3. **Python Automation with `uv` (`uv venv`):**
   - All Python automation, batch simulation scripts, parametric sweeps, and data analysis routines must run in the environment managed by **`uv`**.
   - Always invoke Python scripts via `uv run <script>.py` or `uv run python -m ...` or `uv run ltspice-run ...`.
   - Manage dependencies exclusively via `pyproject.toml` (using `uv add <dependency>`).
   - Python code must follow modern conventions (Python >= 3.12, strict type hints, PEP 8, formatted with `ruff`).

4. **Simulation Artifacts & Data Hygiene:**
   - **Never commit heavy binary raw simulation files (`*.raw`, `*.op.raw`, `*.fft`)** or backup files (`*.bak`, `*.tmp`, `*.swp`) to version control.
   - **Simulation logs (`*.log`)**: Stored either locally or in `_Build_Temp/`. They contain operating point solutions, `.meas` values, and critical convergence error diagnostics.

5. **Git Commit Suggestions on Changes:**
   - Whenever an AI assistant modifies, creates, or deletes files or directories, it **must always** propose a concise, meaningful Git commit message suggestion at the end of its response (preferably following Conventional Commits, e.g., `feat: ...`, `fix: ...`, `refactor: ...`, `docs: ...`).
   - *(Dès qu'une IA apporte des modifications à des fichiers ou dossiers, elle doit systématiquement proposer une idée de message de commit pour Git).*

6. **Rule Governance & Strict Centralization in `.agents/`:**
   - **Mandatory Prior User Approval:** Whenever any AI assistant (Claude, OpenAI/ChatGPT, Google Antigravity, GitHub Copilot, or any other) wishes to create, modify, or delete a rule, it **must always ask the user for explicit confirmation first**. Never add or alter rules unilaterally. *(Toute création ou modification de règle requiert l'accord préalable de l'utilisateur).*
   - **Strict Centralization in `.agents/`:** All rules, guidelines, and directives **must strictly and exclusively be written in the central `.agents/` directory** (under `.agents/rules/` or in the root `AGENTS.md`), regardless of which AI assistant is being used.
   - **No Dispersal into Client-Specific Folders:** Never write rules directly into client-specific directories (such as `.claude/`, `.gemini/`, `.vscode/`, etc.). Those directories serve solely as lightweight routers pointing back to `.agents/` to ensure a single source of truth and full portability when switching AI tools.
   - **Rule Adaptability (Feedback Loop):** If an AI agent encounters a situation where an existing rule, constraint, or guideline in this workspace is ill-adapted, overly rigid, contradictory, or preventing the best technical outcome:
     - **Never ignore or bypass the rule silently.**
     - **Escalate the issue to the user immediately:** explain clearly why the rule is problematic or ill-adapted in the current context, and suggest modifying or removing it.
     - **Update/remove the rule upon agreement:** with the user's validation, edit the relevant rule file in `.agents/rules/` or `AGENTS.md`.

---

## 2. Directory Navigation for Agents

Refer to the following `.agents/` resources when working on this repository:

| Path | Purpose | When to consult |
| :--- | :--- | :--- |
| [`SETUP_LTSPICE.md`](SETUP_LTSPICE.md) | Search Paths configuration, Build_Temp redirection & 3 component cases | When configuring LTspice or creating symbols/blocks |
| [`.agents/rules/architecture.md`](.agents/rules/architecture.md) | Multi-project tree layout (`Projets/`, `_Shared_Lib/`, `_Build_Temp/`) | When creating or organizing LTspice projects |
| [`.agents/rules/coding-style.md`](.agents/rules/coding-style.md) | SPICE netlist syntax, node naming & Python automation coding style | When drafting schematics, netlists or Python scripts |
| [`.agents/rules/testing.md`](.agents/rules/testing.md) | Headless simulation execution, convergence triage & test suite | When running simulations or debugging SPICE errors |
| [`.agents/rules/security.md`](.agents/rules/security.md) | SPICE model verification, Python sandbox isolation & secrets hygiene | When importing external `.lib`/`.sub` or executing scripts |
| [`.agents/rules/general.md`](.agents/rules/general.md) | Engineering principles, SPICE units, relative paths & reproducibility | Fundamental rules across all simulation projects |
| [`.agents/rules/gemini.md`](.agents/rules/gemini.md) | Antigravity / Gemini assistant specific operational guidelines | When interacting as the primary agent |
| [`.agents/workflows/simulation-workflow.md`](.agents/workflows/simulation-workflow.md) | Step-by-step procedures (headless run, parameter sweep, report) | When executing multi-step simulation pipelines |
| [`.agents/skills/`](.agents/skills/) | Reusable skills (LTspice manager, circuit review, memory, diagrams) | On demand for specialized automation workflows |
| [`.agents/subagents/`](.agents/subagents/) | Specialized subagent roles (simulation debugger, circuit QA, research) | When delegating focused electrical or automation tasks |
