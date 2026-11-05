# Workspace Architecture & Multi-Project Layout

## 1. Multi-Project Directory Structure

This repository is designed as a structured hub for managing multiple LTspice circuit design and simulation projects, backed by Python automation with `uv`:

```text
LTspice/
├── projects/                      # Independent LTspice circuit projects
│   ├── <project_name>/            # Individual project directory
│   │   ├── README.md              # Circuit description, specs, and test definitions
│   │   ├── schematics/            # LTspice schematic files (*.asc, *.asy, *.plt)
│   │   ├── models/                # Local SPICE models (*.lib, *.sub, *.cir)
│   │   ├── scripts/               # Project-specific automation & sweep scripts (Python)
│   │   └── data/                  # Exported measurements, CSVs, simulation logs (*.log)
│   └── ...
├── shared/                        # Shared assets across multiple projects
│   ├── models/                    # Verified manufacturer SPICE libraries (*.lib, *.sub)
│   ├── symbols/                   # Common custom schematic symbols (*.asy)
│   └── templates/                 # Starter schematic templates (*.asc) with pre-tuned solvers
├── src/ltspice/                   # Reusable Python automation package (managed with uv)
│   ├── __init__.py
│   ├── runner.py                  # Headless simulation launcher (CLI & bridge)
│   ├── log_parser.py              # Log file parser (*.log, .meas extraction, error triage)
│   └── plotting.py                # Engineering waveform plotting utilities
├── pyproject.toml                 # uv package configuration and dependencies
├── README.md                      # Global repository documentation & getting started
├── .agents/                       # Centralized AI intelligence & directives
└── .mcp.json                      # MCP servers configuration (LTspice bridge, Draw.io, Memory...)
```

---

## 2. Subproject Anatomy & Guidelines

Each subproject under `projects/<project_name>/` must be autonomous and self-documenting:

1. **Schematics Directory (`schematics/`):**
   - Contains the primary testbenches and circuit schematics (`.asc`).
   - Plot setting files (`.plt`) save custom wave viewers and trace configurations.
   - Reusable subcircuit blocks are stored alongside their custom symbol files (`.asy`).

2. **Models Directory (`models/`):**
   - Holds vendor-provided SPICE models (`.lib`, `.sub`, `.cir`, `.mod`) specific to this circuit.
   - **Relative Paths Rule:** Every `.include` or `.lib` directive placed in a schematic **must use relative paths** (e.g., `.inc ./models/opamp.lib` or `.inc ../../shared/models/transistor.lib`). Never use absolute paths (`C:\...`) to guarantee cross-machine portability.

3. **Scripts Directory (`scripts/`):**
   - Python automation scripts for parameter sweeps, Monte Carlo analyses, tolerance sweeps, and automated plotting.
   - Executed using `uv run python scripts/<script_name>.py`.

4. **Data Directory (`data/`):**
   - Stores parsed `.meas` results, exported tables (CSV, JSON), and simulation log files (`*.log`).
   - Binary simulation outputs (`*.raw`, `*.fft`) are excluded from Git via `.gitignore`.

5. **Project Documentation (`README.md`):**
   - Circuit topology description.
   - Operating specifications (e.g. $V_{\text{in}}$, $V_{\text{out}}$, $I_{\text{load}}$, switching frequency, bandwidth).
   - List of simulation testbenches (Transient, AC, DC sweep, Monte Carlo) and instructions to execute them.

---

## 3. Shared Libraries Management (`shared/`)

- Common component models (diodes, MOSFETs, BJT arrays, passives parasitics) that are reused across several circuits should be placed in `shared/models/`.
- New models added to `shared/` should be documented with their source (e.g., manufacturer name, application note number, download link).
- Schematic templates with standard `.tran`, `.ac`, or `.step` setups are maintained in `shared/templates/` for rapid project prototyping.

---

## 4. Python Package (`src/ltspice/`) & uv Environment

- The root `pyproject.toml` defines the project environment.
- Python tools in `src/ltspice/` provide shared helpers for:
  - Batch execution of LTspice in headless mode (`LTspice.exe -b`).
  - Parsing simulation logs (`.log`) to extract `.meas` values into pandas DataFrames.
  - Generating publication-quality waveform figures with Matplotlib.
- New dependencies are added via `uv add <package>` (e.g., `uv add numpy scipy matplotlib pandas`).
