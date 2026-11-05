# LTspice Log Analysis & .meas Parsing Guide

## 1. Structure of the LTspice Simulation Log (`*.log`)

A typical LTspice `.log` file is structured in sequential sections:
1. **Header:** LTspice version, date, circuit title, and expanded netlist.
2. **Operating Point Table:** DC voltages and branch currents (for `.op` or initial transient point).
3. **Solver Details & Warnings:** Convergence warnings, step size throttling, integration method used.
4. **Measurement Results:** All evaluated `.meas` statements.
5. **Footer:** Total elapsed simulation CPU time and transient speed.

---

## 2. Common Measurement Statements

- **Average Value:**
  ```spice
  .meas TRAN Vout_avg AVG V(VOUT) FROM 2m TO 3m
  ```
- **Peak-to-Peak Ripple:**
  ```spice
  .meas TRAN Vout_ripple PP V(VOUT) FROM 2m TO 3m
  ```
- **Maximum & Minimum:**
  ```spice
  .meas TRAN Iind_max MAX I(L1) FROM 1m TO 3m
  .meas TRAN Iind_min MIN I(L1) FROM 1m TO 3m
  ```
- **Rise Time (10% to 90%):**
  ```spice
  .meas TRAN Trise TRIG V(VOUT)=0.1*3.3 RISE=1 TARG V(VOUT)=0.9*3.3 RISE=1
  ```
- **Calculated Metric:**
  ```spice
  .meas TRAN Efficiency PARAM (Vout_avg * Iload_avg) / (Vin_avg * Iin_avg) * 100
  ```

---

## 3. Extracting Results via PowerShell & Python

### PowerShell Quick Extraction
```powershell
Get-Content "projects/my_project/schematics/circuit.log" | Select-String -Pattern "Measurement:" -Context 0, 1
```

### Python with `uv`
```python
import re
from pathlib import Path

def parse_meas(log_path: Path) -> dict[str, float]:
    results = {}
    content = log_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"Measurement:\s*(\w+)\s*\n\s*step\s*1:\s*([^\s]+)", re.IGNORECASE)
    for match in pattern.finditer(content):
        name = match.group(1).lower()
        try:
            results[name] = float(match.group(2))
        except ValueError:
            pass
    return results
```

