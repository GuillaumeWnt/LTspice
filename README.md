# LTspice Simulation Hub & Python Automation Workspace

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Package Manager](https://img.shields.io/badge/uv-fast%20python-purple.svg)](https://docs.astral.sh/uv/)
[![LTspice](https://img.shields.io/badge/LTspice-ADI%2024%2B-red.svg)](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Integrated-green.svg)](https://modelcontextprotocol.io/)

A professional, modular multi-project repository designed for managing electronic circuit simulations with **LTspice**, backed by a high-performance **Python automation toolchain (`uv`)**, official **LTspice MCP integration**, and structured **AI agent directives (`.agents/`)**.

---

## 1. Overview & Architecture

This repository acts as an engineering hub for developing, testing, and archiving multiple electronic circuit designs (switch-mode power supplies, analog filters, signal conditioning, RF, mixed-signal).

### Directory Layout

```text
LTspice/
├── projects/                      # Individual circuit simulation subprojects
│   ├── <project_name>/            # Isolated subproject (e.g. buck_converter)
│   │   ├── README.md              # Circuit specifications & test procedures
│   │   ├── schematics/            # Schematics (*.asc), symbols (*.asy), plots (*.plt)
│   │   ├── models/                # Project-specific SPICE subcircuits (*.lib, *.sub)
│   │   ├── scripts/               # Python automation & parametric sweeps
│   │   └── data/                  # Exported measurements, CSVs, simulation logs (*.log)
├── shared/                        # Centralized cross-project assets
│   ├── models/                    # Verified manufacturer SPICE libraries
│   ├── symbols/                   # Shared custom schematic symbols (*.asy)
│   └── templates/                 # Ready-to-use schematic templates (*.asc)
├── src/ltspice/                   # Reusable Python automation package
│   ├── __init__.py                # Package exports
│   ├── runner.py                  # Headless batch execution CLI & helper
│   └── log_parser.py              # Log parser (*.log, .meas extraction, error triage)
├── pyproject.toml                 # uv configuration and Python dependencies
├── .agents/                       # Centralized AI directives, rules, skills & workflows
│   ├── rules/                     # Architecture, coding style, testing, security
│   ├── skills/                    # LTspice manager, circuit review, memory, diagrams
│   ├── subagents/                 # Specialized agent personas (debugger, reviewer, etc.)
│   ├── workflows/                 # Standard operational runbooks
│   └── scripts/sync-mcp.ps1       # MCP synchronization script across AI environments
├── .mcp.json                      # MCP configuration (Claude Code / Antigravity standard)
└── README.md                      # Repository documentation
```

---

## 2. Prerequisites & Installation

### Required Software
1. **LTspice (Analog Devices, version 24+)**: Installed in the standard directory (`C:\Users\<user>\AppData\Local\Programs\ADI\LTspice\LTspice.exe`).
2. **uv (Python Package & Environment Manager)**:
   ```powershell
   # Install uv on Windows (via winget or PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **Node.js (>= 18)**: Required to power the stdio Model Context Protocol (MCP) servers (`npx`).

### Synchronizing the Python Environment
Initialize and build the local virtual environment with `uv`:
```powershell
# Synchronize environment and install dependencies
uv sync

# Verify that the package and LTspice executable are detected
uv run python -c "import ltspice; print('LTspice located at:', ltspice.find_ltspice_executable())"
```

---

## 3. Running Simulations & Automation

### A. Headless Batch Execution via CLI
Simulate any schematic without opening the graphical interface:
```powershell
# Direct invocation via LTspice CLI
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b "projects/<project>/schematics/<circuit>.asc"

# Or via the built-in Python runner
uv run ltspice-run "projects/<project>/schematics/<circuit>.asc"
```

The runner monitors execution, verifies solver convergence, and parses all `.meas` values directly from the `.log` file into the terminal.

### B. Python Automation Scripts
Create project-specific sweep or post-processing scripts under `projects/<project>/scripts/`:
```python
from pathlib import Path
from ltspice import run_simulation

result = run_simulation("projects/buck_converter/schematics/buck.asc")

if result.success:
    print(f"Simulation completed in {result.elapsed_seconds:.2f}s")
    for name, value in result.measurements.items():
        print(f"  {name}: {value}")
else:
    print("Simulation failed:", result.errors)
```

Run your scripts using `uv`:
```powershell
uv run python projects/buck_converter/scripts/sweep.py
```

To install additional data analysis or plotting packages:
```powershell
uv add matplotlib numpy scipy pandas
```

---

## 4. SPICE Simulation Best Practices

To ensure circuits are portable, robust, and converge cleanly:

1. **Explicit Ground:** Node `0` (`GND`) must always be connected to provide a DC reference.
2. **The SPICE Multiplier Pitfall:**
   - `1M` or `1m` represents **milli** ($10^{-3}$).
   - **Mega** ($10^6$) must always be written **`1Meg`** or **`1meg`**.
3. **Relative Model Paths:** Always use relative paths in `.include` or `.lib` directives:
   ```spice
   .inc ./models/mosfet.lib
   .inc ../../shared/models/diodes.lib
   ```
4. **Automated Measurements (`.meas`):** Use `.meas` statements to record critical metrics (efficiency, ripple, rise time, bandwidth) directly into the simulation log.
5. **Convergence Tuning:** If transient simulations stall with `Time step too small`:
   - Add `.options solver=Alternate`
   - Switch integration method: `.options method=Gear`
   - Add minute parasitic ground capacitance: `.options cshunt=1e-15`

---

## 5. Model Context Protocol (MCP) Integration

This workspace integrates 5 Model Context Protocol servers configured in `.agents/mcp_config.json`:

| Server Name | Protocol / Command | Purpose |
| :--- | :--- | :--- |
| **`ltspice`** | `ltspice-mcp-bridge.exe` | Official Analog Devices bridge connecting AI agents to running or headless LTspice instances. |
| **`memory`** | `@modelcontextprotocol/server-memory` | Cross-session persistent knowledge graph for circuit specs, component models, and design trade-offs. |
| **`brave-search`** | `@modelcontextprotocol/server-brave-search` | Live web research for manufacturer datasheets, application notes, and SPICE models. |
| **`workspace-filesystem`** | `@modelcontextprotocol/server-filesystem` | Direct, secure workspace file navigation and inspection. |
| **`io.draw/mcp`** | Remote HTTP SSE (`https://mcp.draw.io/mcp`) | Generation and updating of electrical system block diagrams and architectures. |

### Synchronizing MCP Configurations
To synchronize MCP configurations across all AI tools (`.vscode/mcp.json`, `.claude/mcp.json`, `.gemini/config/mcp_config.json`, `.mcp.json`):
```powershell
powershell -ExecutionPolicy Bypass -File .\.agents\scripts\sync-mcp.ps1
```
*(In VS Code, this script is automatically triggered upon opening the folder via `.vscode/tasks.json`)*.

---

## 6. AI Agent Governance (`.agents/`)

All AI assistants (Antigravity, Claude, Copilot, ChatGPT) must adhere to the global directives defined in [`AGENTS.md`](AGENTS.md):
- **Rule Governance:** Any creation, modification, or removal of workspace rules requires **prior explicit confirmation from the user**.
- **Centralization:** All rules reside exclusively in `.agents/rules/` and `AGENTS.md`. Client folders (`.claude/`, `.gemini/`, `.github/`) act solely as lightweight context routers.
- **Git Commit Suggestions:** Every assistant response modifying files must propose a concise Conventional Commit suggestion at the end.

