"""LTspice headless batch simulation runner.

Executes LTspice schematics via command-line interface, monitors execution,
and parses the generated simulation logs (supporting local or redirected _Build_Temp outputs).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from ltspice.log_parser import SimulationLogResult, parse_log

DEFAULT_LTSPICE_PATHS = [
    Path(r"C:\Users\guill\AppData\Local\Programs\ADI\LTspice\LTspice.exe"),
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ADI" / "LTspice" / "LTspice.exe",
    Path(r"C:\Program Files\ADI\LTspice\LTspice.exe"),
    Path(r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"),
]


def find_ltspice_executable() -> Path:
    """Locate the LTspice executable on the current system."""
    custom_path = os.environ.get("LTSPICE_EXE")
    if custom_path and Path(custom_path).is_file():
        return Path(custom_path)

    for candidate in DEFAULT_LTSPICE_PATHS:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "LTspice executable not found. Please set LTSPICE_EXE environment variable "
        "or ensure LTspice is installed in standard ADI location."
    )


def resolve_log_path(asc_path: Path, build_temp: Path | None = None) -> Path:
    """Determine the most likely path of the generated .log file.

    Checks redirected build directories (_Build_Temp, Build_Temp) as well as the
    schematic's local directory.
    """
    candidates: list[Path] = []

    # 1. Explicit build_temp argument or environment variable
    if build_temp:
        candidates.append(build_temp / asc_path.with_suffix(".log").name)
    env_build_temp = os.environ.get("LTSPICE_BUILD_TEMP")
    if env_build_temp:
        candidates.append(Path(env_build_temp) / asc_path.with_suffix(".log").name)

    # 2. Workspace root _Build_Temp or Build_Temp
    workspace_root = Path.cwd()
    candidates.append(workspace_root / "_Build_Temp" / asc_path.with_suffix(".log").name)
    candidates.append(workspace_root / "Build_Temp" / asc_path.with_suffix(".log").name)

    # 3. Local schematic directory
    candidates.append(asc_path.with_suffix(".log"))

    # Return the first candidate that exists, or fall back to local
    for cand in candidates:
        if cand.exists():
            return cand

    return asc_path.with_suffix(".log")


def run_simulation(
    schematic_path: Path | str,
    executable: Path | None = None,
    timeout: float | None = 300.0,
    build_temp: Path | None = None,
) -> SimulationLogResult:
    """Execute a schematic headlessly in batch mode and return parsed log results."""
    asc_path = Path(schematic_path).resolve()
    if not asc_path.exists():
        raise FileNotFoundError(f"Schematic not found: {asc_path}")

    exe = executable or find_ltspice_executable()

    # Pre-clean known log locations to ensure we don't read stale logs
    for candidate in [
        asc_path.with_suffix(".log"),
        Path.cwd() / "_Build_Temp" / asc_path.with_suffix(".log").name,
        Path.cwd() / "Build_Temp" / asc_path.with_suffix(".log").name,
    ]:
        if candidate.exists():
            try:
                candidate.unlink()
            except OSError:
                pass

    cmd = [str(exe), "-b", str(asc_path)]

    try:
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        target_log = resolve_log_path(asc_path, build_temp=build_temp)
        return SimulationLogResult(
            filepath=target_log,
            success=False,
            errors=[f"Simulation timed out after {timeout} seconds"],
        )

    # Locate and parse resulting log
    log_path = resolve_log_path(asc_path, build_temp=build_temp)

    if log_path.exists():
        result = parse_log(log_path)
        if proc.returncode != 0 and result.success:
            result.success = False
            result.errors.append(f"Process exited with non-zero code: {proc.returncode}")
        return result

    return SimulationLogResult(
        filepath=log_path,
        success=False,
        errors=[f"Simulation finished but no log file was found at {log_path} (checked local and _Build_Temp)"],
    )


def main() -> None:
    """CLI entry point for running a schematic headlessly."""
    if len(sys.argv) < 2:
        print("Usage: uv run ltspice-run <path_to_schematic.asc>")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    print(f"[*] Running LTspice simulation: {target_path}")

    try:
        result = run_simulation(target_path)
    except Exception as exc:
        print(f"[!] Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if result.success:
        print(f"[+] Simulation succeeded in {result.elapsed_seconds or 0.0:.2f}s")
        if result.measurements:
            print("--- Measurements ---")
            for k, v in result.measurements.items():
                print(f"  {k} = {v}")
        sys.exit(0)
    else:
        print("[-] Simulation failed or encountered errors:", file=sys.stderr)
        for err in result.errors:
            print(f"  [ERROR] {err}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
