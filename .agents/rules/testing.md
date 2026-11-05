# LTspice Simulation Testing, Verification & Diagnostics

## 1. Headless Simulation Commands

### Direct LTspice CLI Execution
Simulations can be executed in batch / headless mode on Windows using PowerShell:

```powershell
# Run simulation headlessly in batch mode (creates .log and .raw in the schematic directory)
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b projects/my_project/schematics/buck.asc

# Generate netlist from schematic without opening the graphical editor
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -netlist projects/my_project/schematics/buck.asc
```

### Programmatic Simulation via Python & `uv`
Using the workspace automation runner:
```powershell
# Run a specific testbench with automated log parsing and cleanup
uv run python -m ltspice.runner projects/my_project/schematics/buck.asc
```

---

## 2. Simulation Log (`*.log`) Forensics

When a simulation fails or halts prematurely, inspect the corresponding `.log` file in the schematic folder:

1. **Fatal Errors & Convergence Failures:**
   - `Fatal Error: Analysis: Time step too small; initial timepoint = ...`:
     - The solver encountered severe non-linear derivative changes (e.g., instant diode switching, ideal opamp saturation).
     - Fixes: add a maximum timestep limit to `.tran` (e.g. `.tran 0 10m 0 1u`), set realistic rise/fall times on sources, or add `.options solver=Alternate method=Gear`.
   - `Fatal Error: Singular matrix: check node X`:
     - Node `X` has no DC conduction path to ground, or an inductor loop with zero resistance is present.
     - Fixes: ensure a ground connection exists; connect a $1\,\text{G}\Omega$ resistor from node `X` to `0`.
   - `Unknown subcircuit called in: ...`:
     - A SPICE model file is missing or not properly referenced.
     - Fix: check `.inc` or `.lib` relative file paths.

2. **Automated Measurement Parsing:**
   - Successful `.meas` statements output lines formatted as:
     ```text
     Measurement: vout_avg
       step 1:  3.30124  FROM 2e-03 TO 3e-03
     Measurement: vout_ripple
       step 1:  0.02451  FROM 2.5e-03 TO 3e-03
     ```
   - Use `src/ltspice/log_parser.py` to parse these lines directly into structured dictionaries or pandas DataFrames.

---

## 3. Automated Regression Testing with `pytest`

Regression tests ensure circuit parameter changes or model updates do not degrade performance:

```powershell
# Execute all workspace tests
uv run pytest

# Execute tests for a specific project
uv run pytest projects/my_project/tests/
```

Test pattern example:
```python
def test_buck_converter_specs():
    results = run_simulation("projects/buck_converter/schematics/buck.asc")
    assert 3.25 <= results["vout_avg"] <= 3.35, "Vout out of tolerance"
    assert results["vout_ripple"] < 0.05, "Ripple exceeds 50 mV"
    assert results["efficiency"] > 85.0, "Efficiency below 85%"
```
