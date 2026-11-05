"""Deterministic SPICE Netlist (.net) to LTspice Schematic (.asc) Converter.

Converts topological SPICE netlists into standardized ladder/rung LTspice
schematics using explicit net flags, avoiding 2D routing errors.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ComponentLine:
    """Represents a component instance in a SPICE netlist."""

    inst_name: str
    component_type: str  # R, C, L, D, V, I, B, S, X, etc.
    nodes: list[str]
    value: str
    raw_line: str


@dataclass
class NetlistContent:
    """Parsed content of a SPICE netlist."""

    title: str = ""
    directives: list[str] = field(default_factory=list)
    components: list[ComponentLine] = field(default_factory=list)
    subcircuits: list[str] = field(default_factory=list)
    port_pins: set[str] = field(default_factory=set)
    is_subckt_file: bool = False
    subckt_name: str = ""


DEFAULT_SYM_DIRS = [
    Path.cwd() / "Projets",
    Path.cwd() / "_Shared_Lib" / "sym",
    Path.cwd() / "_Shared_Lib" / "common_blocks",
    Path(r"C:\Users\guill\AppData\Local\LTspice\lib\sym"),
    Path(r"C:\Users\guill\AppData\Local\Programs\ADI\LTspice\lib\sym"),
]


def find_symbol_file(symbol_name: str, search_dirs: list[Path] | None = None) -> Path | None:
    """Search for an .asy symbol file in standard and project directories."""
    dirs = list(search_dirs or []) + DEFAULT_SYM_DIRS
    clean_name = symbol_name.replace("/", "\\").strip()
    if not clean_name.lower().endswith(".asy"):
        clean_name += ".asy"

    for d in dirs:
        if not d.exists():
            continue
        direct = d / clean_name
        if direct.is_file():
            return direct
        for match in d.rglob(Path(clean_name).name):
            if match.is_file():
                return match

    return None


def resolve_symbol_reference(
    symbol_name: str, netlist_dir: Path, search_dirs: list[Path] | None = None
) -> tuple[str, Path | None]:
    """Resolve the exact symbol name or relative path to put in the SYMBOL line."""
    asy_path = find_symbol_file(symbol_name, search_dirs)
    if not asy_path:
        return symbol_name, None

    for std in [
        Path(r"C:\Users\guill\AppData\Local\LTspice\lib\sym"),
        Path(r"C:\Users\guill\AppData\Local\Programs\ADI\LTspice\lib\sym"),
        Path.cwd() / "_Shared_Lib" / "sym",
        Path.cwd() / "_Shared_Lib" / "common_blocks",
    ]:
        try:
            asy_path.relative_to(std)
            rel = os.path.relpath(asy_path.with_suffix(""), std)
            return rel.replace("/", "\\"), asy_path
        except ValueError:
            pass

    try:
        rel_local = os.path.relpath(asy_path.with_suffix(""), netlist_dir)
        return rel_local.replace("/", "\\"), asy_path
    except ValueError:
        return asy_path.stem, asy_path


def get_symbol_pin_offsets(symbol_name: str, search_dirs: list[Path] | None = None) -> list[tuple[int, int]]:
    """Parse an .asy symbol file and return relative (x, y) pin coordinates in SpiceOrder."""
    asy_path = find_symbol_file(symbol_name, search_dirs)
    if not asy_path:
        lower = symbol_name.lower()
        if lower in ("res", "ind"):
            return [(16, 16), (16, 96)]
        if lower in ("cap", "diode"):
            return [(16, 0), (16, 64)]
        if lower in ("voltage", "bv"):
            return [(0, 16), (0, 96)]
        if lower == "current":
            return [(0, 0), (0, 80)]
        return [(0, 16), (0, 80)]

    pins: dict[int, tuple[int, int]] = {}
    current_x: int | None = None
    current_y: int | None = None

    for line in asy_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        if parts[0] == "PIN" and len(parts) >= 3:
            try:
                current_x = int(parts[1])
                current_y = int(parts[2])
            except ValueError:
                pass
        elif parts[0] == "PINATTR" and len(parts) >= 3 and parts[1] == "SpiceOrder":
            try:
                order = int(parts[2])
                if current_x is not None and current_y is not None:
                    pins[order] = (current_x, current_y)
            except ValueError:
                pass
            current_x, current_y = None, None

    if not pins:
        return [(0, 16), (0, 80)]

    sorted_orders = sorted(pins.keys())
    return [pins[o] for o in sorted_orders]


def get_wire_delta(rel_x: int, rel_y: int) -> tuple[int, int]:
    """Calculate the direction vector for a wire extending outwards from a pin."""
    if rel_x < -8:
        return (-32, 0)
    elif rel_x > 24:
        return (32, 0)
    elif rel_y <= 24:
        return (0, -32)
    else:
        return (0, 32)


def parse_netlist_file(netlist_path: Path) -> NetlistContent:
    """Parse a .net file into structured directives and component instances."""
    content = NetlistContent()
    raw_lines = netlist_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if not raw_lines:
        return content

    content.title = raw_lines[0].lstrip("*; ").strip()

    top_comp_count = 0
    subckt_comp_count = 0
    in_sub = False
    for l in raw_lines:
        s = l.strip()
        if not s or s.startswith("*") or s.startswith(";"):
            continue
        if s.lower().startswith(".subckt"):
            in_sub = True
            continue
        if s.lower().startswith(".ends"):
            in_sub = False
            continue
        if not s.startswith("."):
            if in_sub:
                subckt_comp_count += 1
            else:
                top_comp_count += 1

    is_pure_subckt = top_comp_count == 0 and subckt_comp_count > 0
    content.is_subckt_file = is_pure_subckt

    in_subckt = False
    current_subckt_lines: list[str] = []

    for idx, raw in enumerate(raw_lines):
        line = raw.strip()
        if not line or (idx == 0 and line.startswith("*")):
            continue

        if line.lower().startswith(".subckt"):
            in_subckt = True
            tokens = line.split()
            if is_pure_subckt and len(tokens) >= 2:
                content.subckt_name = tokens[1]
                content.port_pins = set(tokens[2:])
            current_subckt_lines = [line]
            continue
        elif line.lower().startswith(".ends"):
            in_subckt = False
            current_subckt_lines.append(line)
            if not is_pure_subckt:
                content.subcircuits.append("\n".join(current_subckt_lines))
            continue

        if in_subckt and not is_pure_subckt:
            current_subckt_lines.append(line)
            continue

        if line.startswith("*") or line.startswith(";"):
            continue

        if line.startswith("."):
            lower = line.lower()
            if not (lower.startswith(".end") or lower.startswith(".backanno")):
                content.directives.append(line)
            continue

        tokens = line.split()
        if len(tokens) < 3:
            continue

        inst = tokens[0]
        prefix = inst[0].upper()

        if prefix in ("R", "C", "L", "D", "V", "I", "B"):
            nodes = tokens[1:3]
            val = " ".join(tokens[3:]) if len(tokens) > 3 else ""
            content.components.append(
                ComponentLine(inst_name=inst, component_type=prefix, nodes=nodes, value=val, raw_line=line)
            )
        elif prefix == "S":
            nodes = tokens[1:5]
            val = " ".join(tokens[5:]) if len(tokens) > 5 else ""
            content.components.append(
                ComponentLine(inst_name=inst, component_type="S", nodes=nodes, value=val, raw_line=line)
            )
        elif prefix == "X":
            subckt_name = tokens[-1]
            nodes = tokens[1:-1]
            content.components.append(
                ComponentLine(
                    inst_name=inst,
                    component_type="X",
                    nodes=nodes,
                    value=subckt_name,
                    raw_line=line,
                )
            )
        else:
            nodes = tokens[1:3]
            val = " ".join(tokens[3:]) if len(tokens) > 3 else ""
            content.components.append(
                ComponentLine(inst_name=inst, component_type=prefix, nodes=nodes, value=val, raw_line=line)
            )

    return content


def netlist_to_asc(netlist_path: Path, output_asc_path: Path | None = None) -> Path:
    """Convert a SPICE .net file into a clean, standardized .asc ladder schematic."""
    parsed = parse_netlist_file(netlist_path)
    out_path = output_asc_path or netlist_path.with_suffix(".asc")

    lines: list[str] = [
        "Version 4",
        "SHEET 1 3200 2400",
    ]

    project_search_dirs = [
        netlist_path.parent,
        netlist_path.parent / "blocks",
        netlist_path.parent.parent / "sim" / "blocks",
        netlist_path.parent.parent / "blocks",
    ]

    # 1. Place Directives & Comments at top left
    text_x = 32
    text_y = 32
    if parsed.title:
        lines.append(f"TEXT {text_x} {text_y} Left 2 ;{parsed.title}")
        text_y += 32

    for d in parsed.directives:
        lines.append(f"TEXT {text_x} {text_y} Left 2 !{d}")
        text_y += 32

    # Check for subcircuits: do NOT emit if matching .asc or .asy exists as a hierarchical block
    for sub in parsed.subcircuits:
        sub_name = ""
        first_line = sub.splitlines()[0].strip()
        tokens = first_line.split()
        if len(tokens) >= 2:
            sub_name = tokens[1]

        has_block_file = False
        if sub_name:
            for d in project_search_dirs:
                if (d / f"{sub_name}.asc").is_file() or (d / f"{sub_name}.asy").is_file():
                    has_block_file = True
                    break

        if not has_block_file:
            for sub_line in sub.splitlines():
                lines.append(f"TEXT {text_x} {text_y} Left 2 !{sub_line}")
                text_y += 24
            text_y += 16

    # 2. Grid Placement Parameters
    start_x = 320
    start_y = 96
    x_spacing = 224
    y_spacing = 256
    max_y = 1800

    current_x = start_x
    current_y = start_y

    symbol_map = {
        "R": "res",
        "C": "cap",
        "L": "ind",
        "D": "diode",
        "V": "voltage",
        "I": "current",
        "B": "bv",
        "S": "sw",
    }

    # 3. Draw components and standardized rung connections
    for comp in parsed.components:
        raw_sym = comp.value if comp.component_type == "X" else symbol_map.get(comp.component_type, "res")
        sym_ref, asy_file = resolve_symbol_reference(raw_sym, netlist_path.parent, project_search_dirs)
        pin_offsets = get_symbol_pin_offsets(raw_sym, project_search_dirs)

        lines.append(f"SYMBOL {sym_ref} {current_x} {current_y} R0")
        lines.append("WINDOW 0 24 24 Left 2")
        lines.append("WINDOW 3 24 56 Left 2")
        lines.append(f"SYMATTR InstName {comp.inst_name}")
        if comp.value and comp.component_type != "X":
            lines.append(f"SYMATTR Value {comp.value}")

        for idx, node in enumerate(comp.nodes):
            if idx < len(pin_offsets):
                rel_x, rel_y = pin_offsets[idx]
            else:
                rel_x, rel_y = (0, 16 + idx * 32)

            pin_abs_x = current_x + rel_x
            pin_abs_y = current_y + rel_y

            dx, dy = get_wire_delta(rel_x, rel_y)
            flag_x = pin_abs_x + dx
            flag_y = pin_abs_y + dy

            lines.append(f"WIRE {pin_abs_x} {pin_abs_y} {flag_x} {flag_y}")

            flag_label = "0" if node in ("0", "GND", "gnd") else node
            lines.append(f"FLAG {flag_x} {flag_y} {flag_label}")
            if parsed.is_subckt_file and node.upper() in [p.upper() for p in parsed.port_pins]:
                lines.append(f"IOPIN {flag_x} {flag_y} BiDir")

        current_y += y_spacing
        if current_y > max_y:
            current_y = start_y
            current_x += x_spacing

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    """CLI entry point for converting .net to .asc."""
    if len(sys.argv) < 2:
        print("Usage: uv run ltspice-convert <circuit.net> [output.asc]")
        sys.exit(1)

    target_net = Path(sys.argv[1])
    target_asc = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not target_net.exists():
        print(f"[!] Error: File not found: {target_net}", file=sys.stderr)
        sys.exit(1)

    try:
        asc_file = netlist_to_asc(target_net, target_asc)
        print(f"[+] Successfully converted '{target_net.name}' -> '{asc_file.name}'")
    except Exception as exc:
        print(f"[!] Conversion error: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
