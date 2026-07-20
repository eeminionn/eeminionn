#!/usr/bin/env python3
"""Build the neofetch-style info card SVG for the profile README."""

from __future__ import annotations

import html
import os
from pathlib import Path


OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = bool(os.environ.get("STATIC"))

W = 480
H = 376
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 108
LINE_H = 20.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"
SECTION = "#58a6ff"
GREEN = "#3fb950"
ACCENT = "#22d3ee"

ROWS = [
    ("host",),
    ("kv", "Name", "Emilio Abarca"),
    ("kv", "Role", "Interaction Design student @ UDD"),
    ("kv", "Focus", "Robotics, fabrication, AI"),
    ("kv", "Team", "Founder, EIRI UDD"),
    ("kv", "Mentor", "Fundacion Mustakis"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Firmware", "C/C++, Arduino, ESP32"),
    ("kv", "Software", "Python, JavaScript, TypeScript"),
    ("kv", "Making", "Fusion 360, Blender, CNC"),
    ("kv", "Creative", "MadMapper, projection mapping"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", "BattleBots robot kits + workshops"),
    ("bul", "Physical interfaces + STEAM tools"),
]


def esc(value: object) -> str:
    return html.escape(str(value))


def rise(inner: str, index: int) -> str:
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + index * 0.06
    return (
        f'<g opacity="0" transform="translate(0,5)">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
    )


def main() -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>'
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        '</linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for index, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + index * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">'
        "eeminionn@github: ~$ neofetch</text>"
    )

    y = TITLEBAR_H + 30
    for index, row in enumerate(ROWS):
        kind = row[0]
        if kind == "gap":
            y += LINE_H * 0.5
            continue
        if kind == "host":
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                f'<tspan fill="{GREEN}">eeminionn</tspan><tspan fill="{MUTED}">@</tspan>'
                f'<tspan fill="{ACCENT}">github</tspan></text>'
                f'<line x1="{KEY_X + 132}" y1="{y - 4:.1f}" x2="{W - PAD}" y2="{y - 4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.8"/>'
            )
        elif kind == "sec":
            title = esc(row[1])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                f'&#8212; {title}</text>'
                f'<line x1="{KEY_X + 12 + len(title) * 8}" y1="{y - 4:.1f}" x2="{W - PAD}" y2="{y - 4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.8"/>'
            )
        elif kind == "kv":
            key, value = esc(row[1]), esc(row[2])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{value}</text>'
            )
        elif kind == "bul":
            text = esc(row[1])
            inner = (
                f'<circle cx="{KEY_X + 3}" cy="{y - 4:.1f}" r="2.5" fill="{GREEN}"/>'
                f'<text x="{KEY_X + 14}" y="{y:.1f}" fill="{INK}" font-size="12.5">{text}</text>'
            )
        else:
            continue
        parts.append(rise(inner, index))
        y += LINE_H

    parts.append("</svg>")
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT}: {W}x{H}")


if __name__ == "__main__":
    main()
