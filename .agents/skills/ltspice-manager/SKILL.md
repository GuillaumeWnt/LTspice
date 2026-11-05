---
name: ltspice-manager
description: >-
  Use this skill when launching, automating, batch-running, or troubleshooting LTspice simulations,
  extracting .meas parameters from logs, running parametric sweeps, or post-processing results with Python (uv).
---

# LTspice Simulation Manager Skill

This skill provides end-to-end procedures, CLI commands, and Python automation workflows for running and managing LTspice simulations headlessly, analyzing simulation logs, and extracting key performance metrics.

---

## 1. Quick Workflows

### Running Headless Simulations via CLI
1. Open PowerShell and run the schematic in batch mode:
   ```powershell
   & "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b <path_to_schematic.asc>
   ```
2. The simulation executes without opening a GUI window and generates:
   - `<name>.log`: Simulation log (contains operating point, run duration, solver warnings, and `.meas` results).
   - `<name>.raw`: Binary waveform data (ignored by Git).

### Extracting Figures of Merit from Log Files
1. Check the exit status of the run.
2. Read the `.log` file and search for `Measurement:` blocks:
   ```powershell
   Select-String -Path <path_to_log.log> -Pattern "Measurement:" -Context 0, 1
   ```
3. Or use the Python automation parser:
   ```powershell
   uv run python -m ltspice.runner <path_to_schematic.asc>
   ```

### Running Parametric Sweeps & Monte Carlo
1. Define parametric steps in the schematic or testbench:
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

