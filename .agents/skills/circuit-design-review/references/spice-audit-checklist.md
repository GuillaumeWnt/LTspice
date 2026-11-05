# SPICE Pre-Flight Audit Checklist

Before executing long simulation sweeps, verify each item on this checklist:

## 1. Electrical & Topological Integrity
- [ ] **Ground Reference:** Node `0` is explicitly placed and connected.
- [ ] **DC Path to Ground:** Every node has a conductive path to ground (no floating capacitors or transformers without DC bias resistors, e.g., $1\,\text{G}\Omega$).
- [ ] **No Voltage Source Loops:** No two ideal voltage sources are wired in parallel.
- [ ] **No Inductor Cut-Sets:** No ideal inductors in series with open switches or ideal current sources.

## 2. SPICE Multipliers & Units
- [ ] **Mega vs Milli:** Resistors in mega-ohms use `Meg` or `meg` (e.g. `1Meg`, not `1M`).
- [ ] **Inductor Units:** Inductors use `u` or `m` (e.g. `10u`, `100u`), never `µ` (micro sign) which can cause encoding issues in ASCII netlists.
- [ ] **Capacitor Units:** Capacitors use `p`, `n`, `u` (e.g. `22u`, `100n`, `10p`).

## 3. Real-World Component Parasitics
- [ ] **Inductors:** DCR / series resistance is modeled (`Rser=...`).
- [ ] **Capacitors:** ESR is included (`ESR=...`).
- [ ] **Signal Sources:** Rise and fall times on `PULSE` sources are realistic (e.g. $1\,\text{ns}$ to $10\,\text{ns}$, never 0).

## 4. Model & Path Integrity
- [ ] **Relative Paths:** All `.include` and `.lib` directives use relative paths (`./models/...` or `../../shared/models/...`).
- [ ] **Pin Mapping:** Pin numbers in custom `.asy` symbols correspond exactly to `.subckt` arguments.

