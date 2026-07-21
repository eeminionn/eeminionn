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


def repo_card(x: float, y: float, name: str, kind: str, detail: str, color: str) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="188" height="54" rx="8" fill="{PANEL}" stroke="{FRAME}"/>'
        f'<circle cx="{x + 16}" cy="{y + 18}" r="4" fill="{color}"/>'
        f'<text x="{x + 28}" y="{y + 22}" fill="{BRIGHT}" font-size="12.5" font-weight="700">{esc(name)}</text>'
        f'<text x="{x + 14}" y="{y + 39}" fill="{MUTED}" font-size="10.5">{esc(kind)}</text>'
        f'<text x="{x + 14}" y="{y + 51}" fill="{MUTED}" font-size="10">{esc(detail)}</text>'
    )


def repo_map_widget() -> None:
    width, height = 860, 240
    repos = [
        ("BattleBots", "robot kit", "ESP32-S3, web control", BLUE),
        ("Mustakis", "workshop code", "motors, PID, rotation tests", CYAN),
        ("Casino Diorama", "physical interface", "CNC + Arduino feedback", GREEN),
        ("Puente", "projection study", "shadows + urban memory", ORANGE),
        ("EntoScan", "3D scan concept", "photogrammetry notes", PURPLE),
        ("Walter IoT", "wearable prototype", "LTE-M, GNSS, SMS", PINK),
        ("Othermill UDD", "fabrication guide", "CNC workshop notes", BLUE),
    ]
    parts = shell_start(width, height)
    add_titlebar(parts, width, "eeminionn@github: ~$ ./repo-map.sh")
    parts.append(text(28, 62, "$ ls repos --evidence", GREEN, 13, "700"))
    parts.append(text(28, 84, "Concrete work in this profile: code, guides, tests, fabrication notes and concept studies.", INK, 12))

    for index, (name, kind, detail, color) in enumerate(repos):
        row = index // 4
        col = index % 4
        x = 28 + col * 206
        y = 108 + row * 68
        parts.append(repo_card(x, y, name, kind, detail, color))
        if index in {0, 1, 2, 4, 5}:
            pulse_x = x + 174
            parts.append(
                f'<circle cx="{pulse_x}" cy="{y + 18}" r="2.6" fill="{color}" filter="url(#glow)">'
                f'<animate attributeName="opacity" values="0.25;1;0.25" dur="1.6s" begin="{index * 0.13:.2f}s" repeatCount="indefinite"/>'
                "</circle>"
            )

    parts.append("</svg>")
    (ROOT / "build-pipeline.svg").write_text("".join(parts), encoding="utf-8")


def lab_console_widget() -> None:
    width, height = 420, 300
    rows = [
        ("now", "robot kits + workshop material"),
        ("repo style", "code, notes, tests, guides"),
        ("method", "depends on the project"),
        ("bias", "make it work, then explain it"),
    ]
    checks = [
        ("[x]", "firmware sketches"),
        ("[x]", "fabrication / CNC notes"),
        ("[x]", "student-facing docs"),
        ("[~]", "cleaner READMEs"),
    ]
    parts = shell_start(width, height)
    add_titlebar(parts, width, "eeminionn@github: ~$ ./bench-notes")
    parts.append(text(22, 60, "$ cat notes/current.txt", GREEN, 13, "700"))

    y = 88
    for key, value in rows:
        parts.append(text(22, y, key, ORANGE, 12, "700"))
        parts.append(text(106, y, value, BRIGHT, 12))
        y += 24

    parts.append(f'<line x1="22" y1="178" x2="398" y2="178" stroke="{FRAME}"/>')
    parts.append(text(22, 205, "repo artifacts", BLUE, 12, "700"))
    y = 229
    for marker, value in checks:
        color = GREEN if marker == "[x]" else CYAN
        parts.append(text(34, y, marker, color, 11, "700"))
        parts.append(text(72, y, value, INK, 11.5))
        y += 20

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
        ("Code", ["C/C++", "Python", "JS/TS"], BLUE),
        ("Embedded", ["Arduino", "ESP32", "sensors"], CYAN),
        ("Electronics", ["KiCad", "Eagle", "PCBs"], GREEN),
        ("Fabrication", ["Fusion", "Blender", "CNC"], ORANGE),
        ("Media", ["MadMapper", "projection", "UX"], PURPLE),
        ("Docs", ["README", "guides", "analysis"], PINK),
    ]
    parts = shell_start(width, height)
    add_titlebar(parts, width, "eeminionn@github: ~$ ./tools-used")
    parts.append(text(22, 60, "$ grep -R tools ./repos", GREEN, 13, "700"))
    parts.append(text(22, 82, "Tools I actually reach for. Not a fixed stack.", INK, 12))

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
    repo_map_widget()
    lab_console_widget()
    stack_matrix_widget()
    print("wrote build-pipeline.svg lab-console.svg stack-matrix.svg")


if __name__ == "__main__":
    main()
