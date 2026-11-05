# LTspice Simulation Testing, Verification & Diagnostics

## 1. Headless Simulation Commands

### Direct LTspice CLI Execution
Simulations can be executed in batch / headless mode on Windows using PowerShell:

```powershell
# Run simulation headlessly in batch mode (outputs to local folder or _Build_Temp if configured)
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b Projets/Ampli_Audio/sim/main_amp.asc

# Generate netlist from schematic without opening the graphical editor
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -netlist Projets/Ampli_Audio/sim/main_amp.asc
```

### Programmatic Simulation via Python & `uv`
Using the workspace automation runner (which automatically locates the `.log` in `_Build_Temp/` or the schematic folder):
```powershell
uv run ltspice-run Projets/Ampli_Audio/sim/main_amp.asc
```

---

## 2. Simulation Log (`*.log`) Forensics

When a simulation fails or halts prematurely, inspect the generated `.log` file (in `_Build_Temp/` or in the schematic directory):

1. **Fatal Errors & Convergence Failures:**
   - `Fatal Error: Analysis: Time step too small; initial timepoint = ...`:
     - The solver encountered severe non-linear derivative changes (e.g., instant diode switching, ideal opamp saturation).
     - Fixes: add a maximum timestep limit to `.tran` (e.g. `.tran 0 10m 0 1u`), set realistic rise/fall times on sources, or add `.options solver=Alternate method=Gear`.
   - `Fatal Error: Singular matrix: check node X`:
     - Node `X` has no DC conduction path to ground, or an inductor loop with zero resistance is present.
     - Fixes: ensure a ground connection exists; connect a $1\,\text{G}\Omega$ resistor from node `X` to `0`.
   - `Unknown subcircuit called in: ...`:
     - A SPICE model file is missing or not properly referenced.
     - Fix: check Search Paths or relative `.inc`/`.lib` file paths.

2. **Automated Measurement Parsing:**
   - Successful `.meas` statements output lines formatted as:
     ```text
     Measurement: vout_avg
       step 1:  3.30124  FROM 2e-03 TO 3e-03
     Measurement: vout_ripple
       step 1:  0.02451  FROM 2.5e-03 TO 3e-03
     ```
   - Use `_Tools/ltspice/log_parser.py` (or `uv run ltspice-run`) to parse these lines directly into structured dictionaries or pandas DataFrames.

---

## 3. Automated Regression Testing with `pytest`

Regression tests ensure circuit parameter changes or model updates do not degrade performance:

```powershell
# Execute all workspace tests
uv run pytest

# Execute tests for a specific project
uv run pytest Projets/Ampli_Audio/tests/
```

Test pattern example:
```python
def test_audio_amplifier_specs():
    results = run_simulation("Projets/Ampli_Audio/sim/main_amp.asc")
    assert results.success, f"Simulation failed: {results.errors}"
    assert results.measurements["gain_db"] >= 20.0, "Gain below 20 dB"
    assert results.measurements["thd"] < 0.01, "THD exceeds 1%"
```
