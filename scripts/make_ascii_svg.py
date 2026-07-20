#!/usr/bin/env python3
"""Convert a prepared portrait image into a terminal-style ASCII SVG."""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path

from PIL import Image, ImageEnhance


HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "source-prepped.png"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "eeminionn-ascii.svg"
STATIC = bool(os.environ.get("STATIC"))

COLS = 74
ROWS = 39
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"
WHITE_FLOOR = 0.82
GAMMA = 1.16

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

ROW_DUR = 0.11
STAGGER = 0.11


def sampled_rows() -> list[str]:
    image = Image.open(SRC).convert("L")
    image = ImageEnhance.Contrast(image).enhance(1.05)
    image = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    pixels = image.load()
    rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = (pixels[x, y] / 255.0) ** GAMMA
            if lum >= WHITE_FLOOR:
                chars.append(" ")
                continue
            index = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            chars.append(RAMP[max(0, min(index, len(RAMP) - 1))])
        rows.append("".join(chars))
    return rows


def main() -> None:
    art_top = TITLEBAR_H + PAD * 0.35
    font_size = CELL_H * 0.86
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        '</linearGradient></defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W - 1}" height="{CANVAS_H - 1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for index, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + index * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{CANVAS_W / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">'
        "eeminionn@github: ~$ ./portrait.sh</text>"
    )

    for row_index, line in enumerate(sampled_rows()):
        y = art_top + row_index * CELL_H + CELL_H * 0.74
        row_y = art_top + row_index * CELL_H
        delay = row_index * STAGGER
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">'
            f"{html.escape(line)}</text>"
        )
        if STATIC:
            parts.append(text)
            continue
        parts.append(
            f'<clipPath id="r{row_index}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            "</rect></clipPath>"
        )
        parts.append(f'<g clip-path="url(#r{row_index})">{text}</g>')
        parts.append(
            f'<rect y="{row_y + 1:.1f}" width="{CELL_W}" height="{CELL_H - 2}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay + ROW_DUR:.3f}s"/></rect>'
        )

    status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
    status_y = status_line_y + 19
    parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    parts.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" font-size="13">'
        f'eeminionn@github:~$ whoami <tspan fill="{INK}">Emilio Abarca</tspan></text>'
    )
    parts.append(
        f'<rect x="{PAD + 246}" y="{status_y - 12:.1f}" width="8" height="14" fill="{INK}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
        "</rect>"
    )
    parts.append("</svg>")

    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT}: {CANVAS_W}x{CANVAS_H}")


if __name__ == "__main__":
    main()
