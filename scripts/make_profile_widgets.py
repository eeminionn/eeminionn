#!/usr/bin/env python3
"""Build custom README widgets for the profile."""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

BG = "#0d1117"
BG2 = "#111722"
PANEL = "#161b22"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
BRIGHT = "#e6edf3"
BLUE = "#58a6ff"
CYAN = "#22d3ee"
GREEN = "#3fb950"
ORANGE = "#ffa657"
PINK = "#e4405f"
PURPLE = "#a371f7"


def esc(value: object) -> str:
    return html.escape(str(value))


def shell_start(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient>"
        f'<filter id="glow"><feGaussianBlur stdDeviation="2.2" result="blur"/>'
        f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        "</defs>",
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        '<line x1="0" y1="30" x2="{0}" y2="30" stroke="{1}"/>'.format(width, FRAME),
    ]


def add_titlebar(parts: list[str], width: int, title: str) -> None:
    for index, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{20 + index * 16}" cy="15" r="5" fill="{color}"/>')
    parts.append(f'<text x="{width / 2}" y="19" fill="{MUTED}" font-size="12" text-anchor="middle">{esc(title)}</text>')


def text(x: float, y: float, value: str, color: str = INK, size: float = 13, weight: str = "400", **attrs: str) -> str:
    attr_text = " ".join(f'{key}="{esc(val)}"' for key, val in attrs.items())
    if attr_text:
        attr_text = " " + attr_text
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}"{attr_text}>{esc(value)}</text>'


def chip(x: float, y: float, label: str, color: str, width: float | None = None) -> str:
    chip_w = width if width is not None else 16 + len(label) * 7.2
    return (
        f'<rect x="{x}" y="{y}" width="{chip_w}" height="24" rx="6" fill="{color}" fill-opacity="0.12" '
        f'stroke="{color}" stroke-opacity="0.55"/>'
        f'<text x="{x + 10}" y="{y + 16}" fill="{BRIGHT}" font-size="11" font-weight="700">{esc(label)}</text>'
    )


def bar(x: float, y: float, label: str, value: int, color: str) -> str:
    width = 190
    filled = width * value / 100
    return (
        f'<text x="{x}" y="{y}" fill="{MUTED}" font-size="11">{esc(label)}</text>'
        f'<rect x="{x}" y="{y + 8}" width="{width}" height="8" rx="4" fill="{PANEL}" stroke="{FRAME}"/>'
        f'<rect x="{x}" y="{y + 8}" width="{filled:.1f}" height="8" rx="4" fill="{color}" opacity="0.22"/>'
        f'<rect x="{x}" y="{y + 8}" width="0" height="8" rx="4" fill="{color}">'
        f'<animate attributeName="width" from="0" to="{filled:.1f}" dur="1.2s" begin="0.25s" fill="freeze"/>'
        "</rect>"
    )


def pipeline_widget() -> None:
    width, height = 860, 196
    steps = [
        ("01", "Problem", "learning goal"),
        ("02", "CAD", "fit + enclosure"),
        ("03", "PCB", "power + signals"),
        ("04", "Firmware", "control loop"),
        ("05", "UX", "test with users"),
        ("06", "Docs", "kit docs"),
    ]
    parts = shell_start(width, height)
    add_titlebar(parts, width, "eeminionn@github: ~$ ./prototype-pipeline.sh")
    parts.append(text(28, 62, "$ build --from idea --to working-system", GREEN, 13, "700"))
    parts.append(text(28, 84, "A practical loop for robotics kits, physical interfaces and STEAM workshops.", INK, 12))

    start_x = 28
    gap = 136
    y = 110
    for index, (number, label, detail) in enumerate(steps):
        x = start_x + index * gap
        color = [BLUE, CYAN, GREEN, ORANGE, PURPLE, PINK][index]
        parts.append(f'<rect x="{x}" y="{y}" width="108" height="54" rx="8" fill="{PANEL}" stroke="{FRAME}"/>')
        parts.append(f'<text x="{x + 12}" y="{y + 20}" fill="{color}" font-size="11" font-weight="700">{number}</text>')
        parts.append(text(x + 12, y + 36, label, BRIGHT, 13, "700"))
        parts.append(text(x + 12, y + 50, detail, MUTED, 10.5))
        if index < len(steps) - 1:
            line_x = x + 110
            parts.append(f'<path d="M{line_x} {y + 27} H{line_x + 22}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
            parts.append(
                f'<circle cx="{line_x}" cy="{y + 27}" r="3" fill="{color}" filter="url(#glow)">'
                f'<animate attributeName="cx" values="{line_x};{line_x + 22};{line_x}" dur="2.2s" begin="{index * 0.18:.2f}s" repeatCount="indefinite"/>'
                "</circle>"
            )

    parts.append("</svg>")
    (ROOT / "build-pipeline.svg").write_text("".join(parts), encoding="utf-8")


def lab_console_widget() -> None:
    width, height = 420, 300
    parts = shell_start(width, height)
    add_titlebar(parts, width, "eeminionn@github: ~$ ./lab-status")
    parts.append(text(22, 60, "$ scan --profile Emilio_Abarca", GREEN, 13, "700"))
    parts.append(text(22, 86, "status", ORANGE, 12, "700"))
    parts.append(text(92, 86, "building at the hardware/software edge", BRIGHT, 12))
    parts.append(text(22, 110, "mode", ORANGE, 12, "700"))
    parts.append(text(92, 110, "prototype -> test -> document", BRIGHT, 12))
    parts.append(text(22, 134, "signal", ORANGE, 12, "700"))
    parts.append(text(92, 134, "robotics, fabrication, interaction", BRIGHT, 12))

    parts.append(bar(22, 166, "hardware + firmware integration", 88, CYAN))
    parts.append(bar(22, 204, "workshop-ready documentation", 78, GREEN))
    parts.append(bar(22, 242, "design-to-prototype fluency", 84, PURPLE))

    for index, color in enumerate([GREEN, CYAN, ORANGE]):
        cx = 358 + index * 16
        parts.append(
            f'<circle cx="{cx}" cy="54" r="4" fill="{color}">'
            f'<animate attributeName="opacity" values="0.35;1;0.35" dur="1.4s" begin="{index * 0.22:.2f}s" repeatCount="indefinite"/>'
            "</circle>"
        )

    parts.append("</svg>")
    (ROOT / "lab-console.svg").write_text("".join(parts), encoding="utf-8")


def stack_matrix_widget() -> None:
    width, height = 420, 300
    groups = [
        ("Firmware", ["C/C++", "Arduino", "ESP32"], BLUE),
        ("Software", ["Python", "JS", "TypeScript"], CYAN),
        ("Electronics", ["KiCad", "Eagle", "sensors"], GREEN),
        ("Fabrication", ["Fusion 360", "Blender", "CNC"], ORANGE),
        ("Creative tech", ["MadMapper", "projection", "UX"], PURPLE),
        ("AI workflow", ["docs", "analysis", "prototyping"], PINK),
    ]
    parts = shell_start(width, height)
    add_titlebar(parts, width, "eeminionn@github: ~$ ./stack-matrix")
    parts.append(text(22, 60, "$ map --toolchain", GREEN, 13, "700"))
    parts.append(text(22, 82, "Concept -> prototype toolchain.", INK, 12))

    y = 106
    for index, (group, items, color) in enumerate(groups):
        parts.append(f'<rect x="22" y="{y - 16}" width="376" height="28" rx="7" fill="{PANEL}" stroke="{FRAME}" opacity="0.95"/>')
        parts.append(f'<circle cx="36" cy="{y - 2}" r="4" fill="{color}"/>')
        parts.append(text(48, y + 2, group, BRIGHT, 12, "700"))
        x = 158
        for item in items:
            parts.append(chip(x, y - 18, item, color))
            x += 18 + len(item) * 7.2 + 12
        y += 32

    parts.append("</svg>")
    (ROOT / "stack-matrix.svg").write_text("".join(parts), encoding="utf-8")


def main() -> None:
    pipeline_widget()
    lab_console_widget()
    stack_matrix_widget()
    print("wrote build-pipeline.svg lab-console.svg stack-matrix.svg")


if __name__ == "__main__":
    main()
