---
name: ltspice-manager
description: >-
  Use this skill when launching, automating, batch-running, or troubleshooting LTspice simulations,
  extracting .meas parameters from logs, running parametric sweeps, or post-processing results with Python (uv).
---

# LTspice Simulation Manager Skill

This skill provides end-to-end procedures, CLI commands, and Python automation workflows for running and managing LTspice simulations headlessly, analyzing simulation logs (both locally and in `_Build_Temp/`), and extracting key performance metrics.

---

## 1. Quick Workflows

### Running Headless Simulations via CLI
1. Open PowerShell and run the schematic in batch mode:
   ```powershell
   & "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b Projets/<Projet>/sim/<schema>.asc
   ```
2. The simulation executes without opening a GUI window and generates:
   - `<schema>.log`: Simulation log (located either in `_Build_Temp/` if redirected, or in `sim/`).
   - `<schema>.raw`: Binary waveform data (directed to `_Build_Temp/` if configured, and ignored by Git).

### Extracting Figures of Merit from Log Files
1. Use the Python automation runner to execute and parse:
   ```powershell
   uv run ltspice-run Projets/<Projet>/sim/<schema>.asc
   ```
2. The runner automatically checks `_Build_Temp/` and local paths, outputs execution time, and displays all `.meas` values.

### Running Parametric Sweeps & Monte Carlo
1. Define parametric steps in the schematic:
   ```spice
   .step param Rload list 5 10 20
   ; or Monte Carlo sweep:
   .param Rval=mc(100, 0.05)
   .step param run 1 50 1
   ```
2. Include `.meas` statements to record metrics across all steps.
3. Parse the tabular output in the log with Python into a pandas DataFrame.

---

## 2. Reference Documentation
- **[Headless CLI Guide](./references/headless-cli-guide.md):** Full list of LTspice CLI arguments (`-b`, `-netlist`, `-ascii`, `-run`).
- **[Log Analysis & .meas Reference](./references/log-analysis-meas.md):** Parsing syntax for `.meas` results and diagnostic triage.
- **[LTspice Setup Guide](../../../SETUP_LTSPICE.md):** Complete guide to Search Paths and temporary build folder redirection.
