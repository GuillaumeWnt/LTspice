"""LTspice simulation log parser module.

Extracts .meas directives, operating points, solver statistics, and error flags
from LTspice generated *.log files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SimulationLogResult:
    """Structured results parsed from an LTspice simulation log."""

    filepath: Path
    success: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    measurements: dict[str, Any] = field(default_factory=dict)
    elapsed_seconds: float | None = None


def parse_log(log_path: Path | str) -> SimulationLogResult:
    """Parse an LTspice simulation log file and return extracted metrics and status."""
    path = Path(log_path)
    if not path.exists():
        return SimulationLogResult(filepath=path, success=False, errors=[f"File not found: {path}"])

    content = path.read_text(encoding="utf-8", errors="ignore")
    result = SimulationLogResult(filepath=path)

    # 1. Detect fatal errors
    error_patterns = [
        r"Fatal Error:\s*(.+)",
        r"Singular matrix:\s*(.+)",
        r"Analysis:\s*(Time step too small.+)",
        r"Unknown subcircuit called in:\s*(.+)",
    ]
    for pat in error_patterns:
        for match in re.finditer(pat, content, re.IGNORECASE):
            result.errors.append(match.group(0).strip())
            result.success = False

    # 2. Detect solver warnings
    warning_pattern = re.compile(r"Warning:\s*(.+)", re.IGNORECASE)
    for match in warning_pattern.finditer(content):
        result.warnings.append(match.group(1).strip())

    # 3. Extract .meas measurement blocks
    # Format typically:
    # Measurement: vout_avg
    #   step 1:  3.30124  FROM 2e-03 TO 3e-03
    # Or LTspice 24/26 format:
    # i_loop_max: MAX(I(L_LOOP))=5.69998979568 FROM 0 TO 0.01
    meas_blocks = re.findall(
        r"Measurement:\s*(\w+)\s*\n((?:\s*(?:step\s*\d+:|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?).*?(?:\n|$))*)",
        content,
        re.IGNORECASE,
    )
    for name, data in meas_blocks:
        key = name.lower()
        values: list[float] = []
        for line in data.strip().splitlines():
            # match step lines: step 1: 3.30124
            step_match = re.search(r"step\s*\d+:\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", line)
            if step_match:
                try:
                    values.append(float(step_match.group(1)))
                except ValueError:
                    pass
            else:
                # Direct value line
                val_match = re.search(r"=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", line)
                if val_match:
                    try:
                        values.append(float(val_match.group(1)))
                    except ValueError:
                        pass
        if len(values) == 1:
            result.measurements[key] = values[0]
        elif len(values) > 1:
            result.measurements[key] = values

    # Also extract direct line measurements: name: ... = <val> [FROM/at ...]
    for line in content.splitlines():
        direct_match = re.match(r"^([a-zA-Z0-9_]+):\s+.*?=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", line)
        if direct_match:
            k = direct_match.group(1).lower()
            if k not in result.measurements:
                try:
                    result.measurements[k] = float(direct_match.group(2))
                except ValueError:
                    pass

    # 4. Extract total elapsed time
    time_match = re.search(r"Total elapsed time:\s*([0-9]*\.?[0-9]+)\s*seconds", content, re.IGNORECASE)
    if time_match:
        try:
            result.elapsed_seconds = float(time_match.group(1))
        except ValueError:
            pass

    return result

