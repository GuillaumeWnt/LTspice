---
name: circuit-design-review
description: >-
  Use this skill when auditing LTspice circuits, reviewing schematics/netlists for SPICE traps,
  checking ground reference, validating component ratings, or diagnosing convergence failures.
---

# Circuit Design & SPICE Review Skill

This skill provides comprehensive checklists, failure mode analysis, and convergence runbooks for auditing electronic circuits and LTspice schematics before or during simulation.

---

## 1. Quick Workflows

### Pre-Simulation Schematic Audit
1. Verify that **Node 0 (`GND`)** is connected.
2. Check component values for the **milli vs Mega** pitfall (`10M` vs `10Meg`).
3. Ensure pulse and clock sources have non-zero rise and fall times (`trise > 0`, `tfall > 0`).
4. Validate component integration mode against the 3 standard cases:
   - **Case 1 (.MODEL):** Standard symbol + `.mod` in `_Shared_Lib/models/` + `.lib nom.mod`.
   - **Case 2 (.SUBCKT):** Custom symbol `Cell` in `_Shared_Lib/sym/` + `Netlist Order` matching the `.SUBCKT` line.
   - **Case 3 (Block):** Pair `.asc` + `.asy` with identical names in `_Shared_Lib/common_blocks/` or `sim/blocks/` with `Symbol Type: Block`.
5. Check for floating nodes: every node must have a DC conduction path to ground.

### Resolving Simulation Convergence Failures
1. Identify the symptom from the log (located in `_Build_Temp/` or `sim/`):
   - `Analysis: Time step too small` -> Solver cannot resolve rapid dV/dt or dI/dt.
   - `Singular matrix` -> Floating node or loop of zero-impedance elements.
2. Follow the convergence troubleshooting guide to tune solver options systematically:
   - Switch solver to Alternate (`.options solver=Alternate`).
   - Switch integration method to Gear (`.options method=Gear`).
   - Add minute shunt capacitance (`.options cshunt=1e-15`).

---

## 2. Reference Documentation
- **[SPICE Audit Checklist](./references/spice-audit-checklist.md):** Complete checklist for schematic and netlist pre-flight review.
- **[Convergence Troubleshooting Guide](./references/convergence-troubleshooting.md):** Step-by-step diagnostic tree for resolving simulation stalls.
- **[LTspice Setup Guide](../../../SETUP_LTSPICE.md):** Search Paths and component creation reference.
