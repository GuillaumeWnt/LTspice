---
name: project-memory
description: >-
  Use this skill when recording or retrieving persistent project knowledge, circuit specifications,
  component models, design decisions, or researching datasheets using Memory MCP and Brave Search.
---

# Project Memory & Hardware Research Skill

This skill provides operational workflows, schema conventions, and search playbooks for maintaining persistent engineering knowledge across sessions using the `memory` MCP server, coupled with live component and datasheet verification via `brave-search`.

---

## 1. Quick Workflows

### Context Recall at Session Start
1. Query `read_graph` or `search_nodes` to recall:
   - Target circuit specifications ($V_{\text{in}}$, $V_{\text{out}}$, $I_{\text{max}}$, switching frequency).
   - Component selections, vendor part numbers, and SPICE model sources.
   - Pending optimization tasks, tolerance margins, or thermal constraints.
2. Verify that simulation setups align with recorded design decisions.

### Registering New Circuit Decisions or Component Parameters
1. Call `create_entities` with descriptive entity types:
   - `CircuitSpec` for operating requirements (e.g. input range, output ripple, target efficiency).
   - `ComponentSelection` for specific ICs, MOSFETs, diodes, or inductors with manufacturer part numbers.
   - `SimulationResult` for benchmark measurements and verified operating points.
2. Link entities to subprojects using `create_relations`.

### Live Datasheet & SPICE Model Research
1. Call `brave_web_search` with targeted queries:
   - `"<part_number>" datasheet filetype:pdf`
   - `"<part_number>" SPICE model download`
   - `"<part_number>" application note efficiency calculation`
2. Summarize key limits (absolute maximum ratings, RDS(on), gate charge, thermal resistance) and record validated parameters into `memory`.

---

## 2. Reference Documentation
- **[Memory Knowledge Graph Guide](./references/memory-graph-guide.md):** Entity schemas and relation conventions for hardware projects.
- **[Brave Search Playbook](./references/brave-search-playbook.md):** Query strategies for semiconductor datasheets and SPICE models.
