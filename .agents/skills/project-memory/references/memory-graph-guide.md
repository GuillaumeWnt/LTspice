# Memory Knowledge Graph Guide (`@modelcontextprotocol/server-memory`)

This guide defines the conventions and schema for storing persistent project knowledge in this LaTeX workspace.

---

## 1. Entity Architecture

Use standardized entity types when invoking `create_entities`:

| Entity Type | Required Observation Fields | Example |
| :--- | :--- | :--- |
| `DocumentConfig` | Class, engine, language, font option | `{"name": "ThesisProject", "observations": ["Class: ClasseGuillaume.cls", "Font: Calibri", "Engine: LuaLaTeX"]}` |
| `GeometryPreset` | Margins, headheight, footskip, target scope | `{"name": "GeometrieWord", "observations": ["2.5cm all sides", "headheight=26pt", "footskip=30pt"]}` |
| `GlossaryTerm` | Acronym, expanded name, definition, scope | `{"name": "Term_CNN", "observations": ["Full: Convolutional Neural Network", "Defined in Chapter 1"]}` |
| `LiteratureEntity` | Citation key, authors, year, key takeaway | `{"name": "smith2024deep", "observations": ["Authors: Smith & Doe (2024)", "Key finding: 94% segmentation accuracy"]}` |
| `ChapterMilestone` | Chapter number, title, authoring status | `{"name": "Chapter_01", "observations": ["Title: Introduction & Contexte", "Status: Fully drafted, compiles code 0"]}` |

---

## 2. Standard Relation Types

Use standardized relations when invoking `create_relations`:

| From | Relation | To | Description |
| :--- | :--- | :--- | :--- |
| `DocumentConfig` | `uses_geometry` | `GeometryPreset` | Associates layout presets with master document |
| `ChapterMilestone` | `defines_term` | `GlossaryTerm` | Marks where a term was first introduced |
| `ChapterMilestone` | `cites` | `LiteratureEntity` | Maps bibliographical dependency per chapter |
| `LiteratureEntity` | `supports_claim` | `ResearchClaim` | Links empirical sources to written arguments |

---

## 3. Maintenance Cycle

1. **Session Warm-Up:** Query `read_graph` or `search_nodes` to verify active project settings before editing `.tex` files.
2. **Incremental Updates:** Whenever a new table, chapter, or citation is created, append corresponding nodes and relations.
3. **Pruning:** Remove outdated notes using `delete_observations` or `delete_entities` when drafting reaches final publication release.

