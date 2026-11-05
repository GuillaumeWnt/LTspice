# SPICE Convergence Troubleshooting Guide

When LTspice aborts with `Fatal Error: Analysis: Time step too small` or hangs during simulation:

## 1. Systematic Triage Tree

```text
[Simulation Stalls or Fails]
           │
           ├─► Error: "Singular Matrix"
           │     └─► Fix: Floating node detected. Check node named in log.
           │              Add 1G resistor to ground or fix open circuit.
           │
           ├─► Error: "Time step too small"
           │     │
           │     ├─► Step 1: Switch to Alternate Solver
           │     │          Add: .options solver=Alternate
           │     │
           │     ├─► Step 2: Switch Integration Method
           │     │          Add: .options method=Gear
           │     │
           │     ├─► Step 3: Add Shunt Capacitance to Ground
           │     │          Add: .options cshunt=1e-15
           │     │
           │     ├─► Step 4: Add Transient Step Limit
           │     │          In .tran, define max step size:
           │     │          e.g. .tran 0 10m 0 100n
           │     │
           │     └─► Step 5: Smooth Switching Waveforms
           │                Ensure switches and diodes have smooth Ron/Roff transitions.
           │                Check PULSE sources for zero rise/fall times.
           │
           └─► Error: "Unknown subcircuit"
                 └─► Fix: Missing .lib or .inc path. Verify relative path.
```

## 2. Solver Option Cheat-Sheet

| Directive | Description | Default | Recommended Tweak |
| :--- | :--- | :--- | :--- |
| `.options solver=Alternate` | High-precision solver for switching circuits | Standard | Try Alternate first for SMPS |
| `.options method=Gear` | Damps numerical ringing from Trapezoidal | Trap | Use Gear for stiff systems |
| `.options cshunt=1e-15` | Adds 1 fF from all nodes to GND | 0 | Prevents node float in switches |
| `.options gmin=1e-10` | Minimum conductance across PN junctions | 1e-12 | Helps DC operating point find solution |
| `.options trtol=7` | Transient error tolerance multiplier | 1 | 2 to 7 eases transient time steps safely |

