# Brave Search Playbook for Academic LaTeX Workspaces

This guide outlines precision search queries using the `brave-search` MCP server (`brave_web_search`).

---

## 1. Query Patterns

### Locating Missing DOIs & BibTeX Records
When an incomplete reference is encountered:
- `"<paper title>" author:<last_name> doi`
- `"<paper title>" site:crossref.org`
- `"<paper title>" site:semanticscholar.org bibtex`

### Verifying LaTeX Package Documentation & CTAN Options
When encountering unknown macros or options:
- `site:ctan.org <package_name> documentation manual pdf`
- `site:tex.stackexchange.com <package_name> <macro_name>`

### Fact-Checking Claims & Citations
When validating quantitative statements in text:
- `"<claim keywords>" peer reviewed study statistics`
- `"<method name>" benchmark accuracy dataset`

---

## 2. Formatting Results for Inclusion in LaTeX

1. Extract verified parameters (e.g. publication year, DOI, volume, page range).
2. Clean strings according to project rules:
   - Wrap special terms in braces `{NASA}`, `{RNA}`.
   - Remove URL prefixes from DOIs (`10.xxxx/...`).
3. Store verified entities in `memory` or directly in `bib/references.bib`.

