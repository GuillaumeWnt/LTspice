---
name: visual-diagrams
description: >-
  Use this skill when creating, editing, or integrating technical diagrams, power stage flowcharts,
  and system architecture schematics using Draw.io MCP (io.draw/mcp).
---

# Visual Diagrams & System Architecture Skill

This skill provides procedures and templates for designing and embedding electronic system architectures, power stage flowcharts, and signal chain diagrams using Draw.io (`io.draw/mcp`).

---

## 1. Quick Workflows

### Generating System Block Diagrams via Draw.io MCP
1. Define the system architecture (input source, power stages, feedback loops, controllers, loads).
2. Call `create_diagram` or `edit_diagram` with diagram parameters or XML structure.
3. Save diagrams into the project documentation directory: `projects/<project_name>/docs/diagrams/<name>.drawio.xml`.
4. Export as SVG or PNG for inclusion in subproject READMEs.

### Electrical Flowcharts & Control Logic
1. Model state machines, protection logic (e.g. OVP, OCP, OTP), or test sequences.
2. Use standardized electrical symbols and color coding:
   - Power paths: thick lines / prominent colors.
   - Control / Feedback: thinner lines / dashed signals.
   - Ground and references: standard ground symbols.

---

## 2. Reference Documentation
- **[Draw.io MCP Guide](./references/drawio-mcp-guide.md):** Detailed guide to calling `create_diagram` and structuring system diagrams.
