# Workflow: Headless Simulation, Diagnostics & Post-Processing

This runbook describes the standard procedure for executing an LTspice simulation headlessly, verifying output convergence, extracting measurements from the log file, and performing Python post-processing.

---

## Prerequisites
- LTspice installed and accessible at `C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe`.
- Python virtual environment synchronized with `uv` (`uv sync`).

---

## Procedure

### Step 1: Pre-Flight Schematic Verification
Before running the simulation, check:
1. Ground node `0` (`GND`) is placed and connected.
2. No `1M` resistor used when `1Meg` was intended (SPICE unit trap).
3. All `.include` and `.lib` directives use relative paths.
4. Transient directive `.tran` has a reasonable stop time and timestep.

### Step 2: Headless Simulation Execution
Run the simulation in batch mode from PowerShell:
```powershell
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b projects/<project_name>/schematics/<circuit>.asc
```
*(Or use the Python automation runner: `uv run python -m ltspice.runner projects/<project_name>/schematics/<circuit>.asc`)*.

### Step 3: Check Simulation Log & Measurement Extraction
Inspect `projects/<project_name>/schematics/<circuit>.log`:
- Check for `Fatal Error:` or solver abort messages.
- If errors are found, proceed to **Step 4: Diagnostics**.
- If completed successfully, extract all `.meas` values:
  ```powershell
  Get-Content projects/<project_name>/schematics/<circuit>.log | Select-String -Pattern "Measurement:" -Context 0, 1
  ```

### Step 4: Diagnostic Triage (If Failed)
1. Read the last 40 lines of the `.log` file to find the failure cause.
2. If `Time step too small`:
   - Add `.options solver=Alternate` to the schematic.
   - If still failing, switch to `.options method=Gear`.
   - Check switching edges on sources (`trise`, `tfall` > 0).
3. If `Singular matrix`:
   - Inspect the node named in the error.
   - Add a $1\,\text{G}\Omega$ bleeder resistor to ground from that node.
4. Apply the correction and re-run Step 2.

### Step 5: Post-Processing & Waveform Visualization
Run project post-processing scripts with `uv`:
```powershell
uv run python projects/<project_name>/scripts/analyze.py
```
This script reads the exported data, plots waveforms with engineering axes, and exports summary metrics.

