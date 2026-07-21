#!/usr/bin/env python3
"""Build the compact neofetch-style identity card for the profile README."""

from __future__ import annotations

import html
from pathlib import Path


OUT = Path(__file__).resolve().parent.parent / "info-card.svg"

W = 560
H = 360
PAD = 24
TITLEBAR_H = 34
KEY_X = PAD
VAL_X = 154
ROW_H = 38

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
KEY = "#ffa657"
GREEN = "#3fb950"
ACCENT = "#22d3ee"

ROWS = [
    ("Name", "Emilio Abarca"),
    ("Role", "Interaction Design @ UDD"),
    ("Build", "Embedded + physical interfaces"),
    ("Code", "C/C++, Python, JavaScript"),
    ("Hardware", "ESP32, Arduino, motors, sensors"),
    ("Making", "CNC, PCB, 3D printing"),
    ("Community", "EIRI UDD / Fundacion Mustakis"),
]


def esc(value: object) -> str:
    return html.escape(str(value))


def main() -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>'
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        '</linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="10" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for index, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + index * 18}" cy="{TITLEBAR_H / 2}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 4.5}" fill="{MUTED}" font-size="13" text-anchor="middle">'
        "eeminionn@github: ~$ neofetch</text>"
    )

    parts.append(
        f'<text x="{PAD}" y="68" font-size="19" font-weight="700">'
        f'<tspan fill="{GREEN}">eeminionn</tspan><tspan fill="{MUTED}">@</tspan>'
        f'<tspan fill="{ACCENT}">github</tspan></text>'
    )
    parts.append(f'<line x1="190" y1="62" x2="{W - PAD}" y2="62" stroke="{FRAME}"/>')
    parts.append(
        f'<rect x="{W - PAD - 9}" y="51" width="9" height="16" fill="{INK}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.48;0.49;1" dur="1s" repeatCount="indefinite"/>'
        "</rect>"
    )

    y = 108
    for key, value in ROWS:
        inner = (
            f'<text x="{KEY_X}" y="{y}" fill="{KEY}" font-size="15" font-weight="700">{esc(key)}</text>'
            f'<text x="{VAL_X}" y="{y}" fill="{INK}" font-size="17">{esc(value)}</text>'
        )
        parts.append(f"<g>{inner}</g>")
        y += ROW_H

    parts.append("</svg>")
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT}: {W}x{H}")


if __name__ == "__main__":
    main()
