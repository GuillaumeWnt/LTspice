# Workflow: Headless Simulation, Diagnostics & Post-Processing

This runbook describes the standard procedure for executing an LTspice simulation headlessly, verifying output convergence, extracting measurements from the log file (handling local or redirected `_Build_Temp/` outputs), and performing Python post-processing.

---

## Prerequisites
- LTspice installed and accessible at `C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe`.
- Search Paths and Waveforms output directory configured as described in [`SETUP_LTSPICE.md`](../../SETUP_LTSPICE.md).
- Python virtual environment synchronized with `uv` (`uv sync`).

---

## Procedure

### Step 1: Pre-Flight Schematic Verification
Before running the simulation, check:
1. Ground node `0` (`GND`) is placed and connected.
2. No `1M` resistor used when `1Meg` was intended (SPICE unit trap).
3. Component references:
   - Case 1 (`.MODEL`): `.lib <fichier.mod>` directive present.
   - Case 2 (`.SUBCKT`): Symbol type `Cell`, `Prefix: X`, `Value` matching `.SUBCKT` name, `ModelFile` specified.
   - Case 3 (`Block`): Symbol type `Block`, empty attributes, pin names match F4 port labels.
4. Transient directive `.tran` has a reasonable stop time and maximum timestep.

### Step 2: Headless Simulation Execution
Run the simulation in batch mode from PowerShell:
```powershell
# Direct CLI invocation
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b Projets/<Projet>/sim/<schema>.asc

# Or via the automated Python runner (locates log in _Build_Temp or local sim folder automatically)
uv run ltspice-run Projets/<Projet>/sim/<schema>.asc
```

### Step 3: Check Simulation Log & Measurement Extraction
Inspect the generated `.log` file (located either in `_Build_Temp/` or in `Projets/<Projet>/sim/`):
- Check for `Fatal Error:` or solver abort messages.
- If errors are found, proceed to **Step 4: Diagnostics**.
- If completed successfully, extract all `.meas` values:
  ```powershell
  # Using the runner
  uv run ltspice-run Projets/<Projet>/sim/<schema>.asc
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
uv run python Projets/<Projet>/scripts/analyze.py
```
This script reads the exported data, plots waveforms with engineering axes, and exports summary metrics.
