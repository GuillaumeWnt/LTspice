# Draw.io MCP Guide (`io.draw/mcp`)

This guide explains how to generate, configure, and maintain Draw.io diagrams in this LaTeX workspace using the `io.draw/mcp` server.

---

## 1. Available Tools

### `create_diagram`
Generates a new Draw.io diagram model.
- **Input Parameters:**
  - Diagram title/name.
  - Structure nodes, connectors, hierarchy, and labels.
- **Output:** Valid Draw.io XML graph model (`<mxGraphModel>`).

### `search_shapes`
Searches standard Draw.io stencil libraries for specialized domain shapes:
- Cloud architectures: AWS, Azure, Google Cloud stencils.
- Software engineering: UML, ERD, Flowchart, BPMN stencils.
- Hardware & Networking: Routers, switches, databases.

---

## 2. Best Practices for LaTeX Integration

1. **Storage Location:** Store all `.drawio` / `.drawio.xml` source files in `images/diagrams/`.
2. **Vector Export:**
   - Draw.io diagrams should be exported to PDF or EPS vector format whenever possible (`images/diagrams/<name>.pdf`).
   - Vector PDFs scale infinitely without pixelation and retain sharp text and line weights.
3. **Typography Harmony:**
   - Set diagram font family to a neutral sans-serif (e.g., Arial, Helvetica) or matching serif to complement the document font.
   - Maintain font sizes between 9pt and 11pt relative to the intended figure scale.
4. **Color Harmony:**
   - Avoid saturated primaries (pure red `#FF0000`, pure green `#00FF00`).
   - Use soft muted fills (e.g., slate `#F1F5F9`, muted blue `#E0F2FE`, sage `#DCFCE7`) with dark borders (`#334155`).

