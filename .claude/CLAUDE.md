# Claude Code Directives — AI Context Router

> **Single Source of Truth:** All project-specific guidelines, coding conventions, architectural rules, runbooks, and tools are centralized in [`AGENTS.md`](../AGENTS.md) and the [`.agents/`](../.agents) directory.

---

## 1. Operating Instructions for Claude
This workspace is self-documenting. Before performing any substantial task, discover and align with the project context:

1. **Understand the Project Context:**
   - Read [`AGENTS.md`](../AGENTS.md) at repository root for high-level project goals, language stack, and fundamental principles.
2. **Apply Standards & Constraints (`.agents/rules/`):**
   - Inspect [`.agents/rules/`](../.agents/rules/) for applicable domain rules (e.g., simulation conventions, architecture, security, testing).
3. **Execute Procedures & Runbooks (`.agents/workflows/`):**
   - For multi-step procedures (headless simulations, parameter sweeps, diagnostics), consult and follow the runbooks in [`.agents/workflows/`](../.agents/workflows/).
4. **Leverage Tools, Templates & Skills (`.agents/skills/`):**
   - Check [`.agents/skills/`](../.agents/skills/) to find specialized capabilities, templates, documentation references, and helper scripts.
5. **Utilize Project Automation (`.agents/scripts/`):**
   - Inspect [`.agents/scripts/`](../.agents/scripts/) for available maintenance and automation scripts.

---

## 2. General Principles
* **Never Assume Arbitrary Conventions:** Always inspect the `.agents/` structure of the current project to adopt its specific conventions.
* **Keep Schematics, Models & Code Clean:** Follow the multi-project modularity, relative model paths, and separation of concerns documented in the workspace rules.
