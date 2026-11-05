"""LTspice simulation automation package."""

from ltspice.log_parser import SimulationLogResult, parse_log
from ltspice.runner import find_ltspice_executable, run_simulation

__all__ = [
    "SimulationLogResult",
    "find_ltspice_executable",
    "parse_log",
    "run_simulation",
]
