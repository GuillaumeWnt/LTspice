# LTspice Headless CLI Guide

## 1. Primary Command Line Flags

The Windows LTspice executable (`LTspice.exe`) supports several headless/batch CLI flags:

| Flag | Description | Typical Use Case |
| :--- | :--- | :--- |
| `-b <file.asc>` | Run simulation in batch mode (headless). | Automated sweeps, CI/CD, Python runner |
| `-netlist <file.asc>` | Generate the SPICE netlist (`.net`) without simulating. | Schematic auditing, ERC checks |
| `-ascii` | Output the raw data file in plain text ASCII instead of binary. | Exporting small datasets for direct text inspection |
| `-alt` | Force the Alternate solver. | Highly non-linear power electronics simulations |
| `-run <file.asc>` | Open LTspice GUI and immediately start the simulation. | Interactive visual debugging |

## 2. Headless Batch Execution Command
```powershell
& "C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b "projects/buck_converter/schematics/buck.asc"
```

## 3. Exit Codes & Diagnostics
- While `LTspice.exe` returns upon batch completion, always verify that the `.log` file was generated and does not contain fatal error flags such as `Fatal Error:` or `Analysis: Time step too small`.

