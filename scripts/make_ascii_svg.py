#!/usr/bin/env python3
"""Convert a prepared portrait image into a terminal-style ASCII SVG."""

from __future__ import annotations

import html
import os
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "source-prepped.png"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "eeminionn-ascii.svg"
STATIC = bool(os.environ.get("STATIC"))

COLS = 88
ROWS = 47
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"

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
INK = "#e6edf3"
CURSOR = "#c9d1d9"

ROW_DUR = 0.11
STAGGER = 0.09


def ascii_rows(image: Image.Image) -> list[list[tuple[int, str, float]]]:
    small = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(small)
    gray = ImageOps.autocontrast(gray)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    color_pixels = small.load()
    gray_pixels = gray.load()
    edge_pixels = edges.load()

    edge_width = max(3, COLS // 12)
    row_backgrounds = []
    for y in range(ROWS):
        left = [color_pixels[x, y] for x in range(edge_width)]
        right = [color_pixels[COLS - 1 - x, y] for x in range(edge_width)]
        left_rgb = tuple(sum(pixel[channel] for pixel in left) / len(left) for channel in range(3))
        right_rgb = tuple(sum(pixel[channel] for pixel in right) / len(right) for channel in range(3))
        row_backgrounds.append((left_rgb, right_rgb))

    rows: list[list[tuple[int, str, float]]] = []
    for y in range(ROWS):
        row: list[tuple[int, str, float]] = []
        for x in range(COLS):
            red, green, blue = color_pixels[x, y]
            lum = gray_pixels[x, y] / 255.0
            edge = min(1.0, edge_pixels[x, y] / 255.0 * 1.85)
            left_bg, right_bg = row_backgrounds[y]
            mix = x / max(1, COLS - 1)
            background = tuple(left_bg[channel] * (1.0 - mix) + right_bg[channel] * mix for channel in range(3))
            distance = (abs(red - background[0]) + abs(green - background[1]) + abs(blue - background[2])) / (
                255.0 * 3.0
            )
            shadow = max(0.0, 0.64 - lum) * 1.55
            subject = min(1.0, distance * 2.4)
            signal = max(edge * 0.70, shadow * subject * 1.1)
            if subject < 0.20:
                signal *= 0.25
            if x < 2 or x >= COLS - 2 or y < 2 or y >= ROWS - 2:
                signal *= 0.20
            if signal < 0.16:
                continue

            ramp_index = round(min(1.0, signal * 1.25) * (len(RAMP) - 1))
            char = RAMP[max(1, min(ramp_index, len(RAMP) - 1))]
            opacity = min(0.92, 0.28 + signal * 0.82)
            row.append((x, char, opacity))
        rows.append(row)
    return rows


def row_text(row: list[tuple[int, str, float]], y: float) -> str:
    pieces = []
    for x, char, opacity in row:
        pieces.append(
            f'<text x="{PAD + x * CELL_W}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{CELL_H * 0.86:.1f}" opacity="{opacity:.3f}">'
            f"{html.escape(char)}</text>"
        )
    return "".join(pieces)


def main() -> None:
    image = Image.open(SRC).convert("RGB")
    art_top = TITLEBAR_H + PAD * 0.35

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
        "</linearGradient></defs>",
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

    parts.append(f'<rect x="{PAD}" y="{art_top:.1f}" width="{ART_W}" height="{ART_H}" fill="{BG}" opacity="0.35"/>')

    for row_index, row in enumerate(ascii_rows(image)):
        if not row:
            continue
        y = art_top + row_index * CELL_H + CELL_H * 0.74
        row_y = art_top + row_index * CELL_H
        delay = row_index * STAGGER
        text = row_text(row, y)
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
