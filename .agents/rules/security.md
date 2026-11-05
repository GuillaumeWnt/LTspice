# Security, Model Hygiene & Environment Guidelines

## 1. Third-Party SPICE Model Hygiene

When importing component SPICE models (`.lib`, `.sub`, `.cir`, `.mod`) from external manufacturers, forums, or distributors:

- **Source Verification:** Prefer encrypted or plain-text models downloaded directly from official semiconductor manufacturers (Analog Devices, TI, onsemi, STMicroelectronics, Infineon).
- **Text Inspection:** Always inspect third-party `.lib` and `.sub` text files prior to integration:
  - Check for proprietary licensing restrictions.
  - Verify that node pin mappings match standard component symbol footprints (`.asy`).
  - Ensure models do not contain malformed or unbounded equations that could crash the simulation engine.
- **Controlled Storage:** Store vendor models in dedicated `models/` or `shared/models/` directories with an accompanying source comment.

---

## 2. Python Execution & Environment Isolation

- **Virtual Environment Enforcement:**
  - All Python execution must strictly occur through **`uv`** (`uv run ...`).
  - Do not install packages globally in the system Python environment.
- **Subprocess Safety:**
  - When spawning LTspice CLI processes from Python, use explicit argument lists with `subprocess.run([...], check=True)` rather than shell strings (`shell=True`), to prevent command injection risks.
  - Validate and sanitize schematic file paths before passing them to the LTspice executable.

---

## 3. Secrets & API Key Hygiene

- **API Keys:** Never hardcode API keys (such as `BRAVE_API_KEY`) into scripts, netlists, or configuration files.
- **Exclusion Files:** Ensure `.env`, `.env.*`, and `*.local.json` are listed in `.gitignore`, `.aiexclude`, `.claudeignore`, and `.geminiignore`.
- **Clean Commits:** Verify `git status` before committing to avoid accidentally including temporary outputs or credential files.

---

## 4. Large Binary File Hygiene

- LTspice waveform files (`*.raw`, `*.op.raw`, `*.fft`) can grow to several gigabytes during long transient runs.
- They must remain excluded from Git to prevent repository bloat and ensure fast cloning.
- Use Python scripts to extract compact numerical metrics into CSV or JSON summaries.
