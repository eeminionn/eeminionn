#!/usr/bin/env python3
"""Build the compact selected-work terminal widget for the profile README."""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "selected-work.svg"

W = 520
H = 220
BG = "#0d1117"
BG2 = "#111722"
PANEL = "#161b22"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
BRIGHT = "#e6edf3"
GREEN = "#3fb950"

PROJECTS = [
    ("01", "BattleBots 2026-1", "ESP32-S3 | Wi-Fi control | mecanum kit", "EMBEDDED", "#58a6ff"),
    ("02", "Casino Diorama", "Blender/Fusion | 3D print | CNC PCB | Arduino", "FABRICATION", "#ffa657"),
    ("03", "Mundial Infinito", "p5.js | microphone bands | audio-reactive game", "CREATIVE CODE", "#a371f7"),
]


def esc(value: object) -> str:
    return html.escape(str(value))


def main() -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        '</linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="10" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="30" x2="{W}" y2="30" stroke="{FRAME}"/>',
    ]

    for index, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{20 + index * 16}" cy="15" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{W / 2}" y="19" fill="{MUTED}" font-size="11.5" text-anchor="middle">'
        "eeminionn@github: ~$ ./selected-work.sh</text>"
    )
    parts.append(f'<text x="20" y="55" fill="{GREEN}" font-size="13" font-weight="700">$ open --proof</text>')
    parts.append(f'<text x="150" y="55" fill="{INK}" font-size="11.5">code, build logs and working interactions</text>')

    for index, (number, title, detail, label, color) in enumerate(PROJECTS):
        y = 68 + index * 48
        inner = (
            f'<rect x="20" y="{y}" width="480" height="40" rx="6" fill="{PANEL}" stroke="{FRAME}"/>'
            f'<rect x="20" y="{y}" width="4" height="40" rx="2" fill="{color}"/>'
            f'<text x="34" y="{y + 17}" fill="{color}" font-size="12" font-weight="700">{esc(number)}</text>'
            f'<text x="61" y="{y + 17}" fill="{BRIGHT}" font-size="15" font-weight="700">{esc(title)}</text>'
            f'<text x="{484}" y="{y + 16}" fill="{color}" font-size="9" font-weight="700" text-anchor="end">{esc(label)}</text>'
            f'<text x="61" y="{y + 33}" fill="{MUTED}" font-size="11.5">{esc(detail)}</text>'
        )
        parts.append(f"<g>{inner}</g>")
        parts.append(
            f'<circle cx="488" cy="{y + 31}" r="2.2" fill="{color}" opacity="0.8">'
            f'<animate attributeName="opacity" values="0.25;1;0.25" dur="1.6s" '
            f'begin="{index * 0.18:.2f}s" repeatCount="indefinite"/></circle>'
        )

    parts.append("</svg>")
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT}: {W}x{H}")


if __name__ == "__main__":
    main()
