# General Engineering Directives & SPICE Philosophy

## 1. Core Engineering Philosophy

- **Deterministic Reproducibility:**
  - Any circuit schematic or testbench in this repository must run out-of-the-box on a clean clone without requiring absolute paths or proprietary manual setup.
  - All external subcircuits, SPICE models, or parameters must be committed in `models/` or `shared/models/`.

- **Cross-Project Isolation:**
  - Individual subprojects under `projects/<project_name>/` must remain completely independent of one another.
  - Shared models, symbols, and templates must be placed strictly in `shared/` so that changes to one project cannot inadvertently break another.

- **Data Hygiene:**
  - Simulation binary raw files (`*.raw`, `*.op.raw`, `*.fft`) must never be committed to Git.
  - Distill raw simulation runs into lightweight artifacts: `.meas` log files, CSV summaries, and Matplotlib plots.

---

## 2. SPICE Convergence & Solver Discipline

Simulations that stall or fail to converge should be diagnosed systematically rather than patched arbitrarily:

1. **Root Cause Analysis First:**
   - Check for floating high-impedance nodes (add a $1\,\text{G}\Omega$ or $10\,\text{M}\Omega$ bleeder resistor to ground if necessary).
   - Check for instantaneous switching / zero rise-time sources: Always set realistic `trise` and `tfall` (e.g. $1\,\text{ns}$ to $10\,\text{ns}$) on `PULSE` sources.
   - Check for discontinuous diodes or switches: Ensure smooth transition parameters are active.

2. **Tuning `.options` Sensibly:**
   - Prefer solver changes over relaxing error tolerances:
     ```spice
     .options solver=Alternate
     ```
   - If convergence stalls during steep transients, consider Gear integration:
     ```spice
     .options method=Gear
     ```
   - For high-speed switching circuits with small parasitic nodes, add minute parasitic capacitance to ground:
     ```spice
     .options cshunt=1e-15
     ```
   - **Never** increase `reltol` above $0.01$ ($1\%$) without explicit engineering justification, as it can hide numerical oscillations or give inaccurate power calculations.

---

## 3. Real-World Parasitics & Fidelity

- **Passive Components:**
  - Power inductors must include Series Resistance (`Rser` / DCR).
  - Bulk filter capacitors must include Equivalent Series Resistance (`ESR`) and ideally Equivalent Series Inductance (`ESL`).
- **Semiconductors:**
  - Avoid ideal switches with $R_{\text{on}}=0$ and zero transition time; use vendor SPICE subcircuits or realistic parameters ($R_{\text{on}}$, $R_{\text{off}}$, $V_{\text{threshold}}$).
- **Thermal & Limits:**
  - Inspect peak voltages and currents to ensure components stay within Safe Operating Areas (SOA).
