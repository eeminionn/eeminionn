#!/usr/bin/env python3
"""Generate a reference-style animated GitHub contribution heatmap SVG."""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "data" / "contributions.json"

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
GRAY = "#7d8590"
TEXT = "#e6edf3"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CELL = 13
GAP = 3
RAD = 2.5
LEFT = 34
TOP = 24
REVEAL = 3.0
CYCLE = 5.2


def sunday_index(date_text: str) -> int:
    date = dt.date.fromisoformat(date_text)
    return (date.weekday() + 1) % 7


def normalized_days(days: list[dict[str, int | str]]) -> list[dict[str, int | str] | None]:
    if not days:
        return []
    leading = sunday_index(str(days[0]["date"]))
    padded: list[dict[str, int | str] | None] = [None] * leading
    padded.extend(days)
    while len(padded) % 7:
        padded.append(None)
    return padded


def month_labels(days: list[dict[str, int | str] | None]) -> list[str]:
    labels = []
    last_month = None
    for week in range(len(days) // 7):
        first_day = next((day for day in days[week * 7 : week * 7 + 7] if day), None)
        if not first_day:
            continue
        date = dt.date.fromisoformat(str(first_day["date"]))
        if date.month != last_month:
            last_month = date.month
            x = LEFT + week * (CELL + GAP)
            labels.append(f'<text class="lbl" x="{x}" y="{TOP - 8}">{MONTHS[date.month - 1]}</text>')
    return labels


def render(username: str, data: dict[str, object]) -> str:
    days = normalized_days(data["days"])  # type: ignore[index]
    weeks = len(days) // 7
    width = LEFT + weeks * (CELL + GAP) + 6
    height = TOP + 7 * (CELL + GAP) + 22
    max_order = max(1.0, (weeks - 1) + 6 * 0.55)

    labels = month_labels(days)
    for name, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        labels.append(f'<text class="lbl" x="2" y="{TOP + row * (CELL + GAP) + CELL - 2}">{name}</text>')

    rects = []
    for index, day in enumerate(days):
        if day is None:
            continue
        week = index // 7
        row = index % 7
        x = LEFT + week * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        count = int(day["count"])
        level = max(0, min(int(day.get("level", 0)), 4))
        delay = round((week + row * 0.55) / max_order * REVEAL, 3)
        css_class = "c g" if level >= 1 else "c e"
        plural = "s" if count != 1 else ""
        rects.append(
            f'<rect class="{css_class}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="{RAD}" fill="{COLORS[level]}" style="animation-delay:{delay}s">'
            f'<title>{day["date"]}: {count} contribution{plural}</title></rect>'
        )

    total = int(data.get("total_contributions", 0))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<style>
  text.lbl {{ fill:{GRAY}; font-size:13px; font-weight:600; }}
  text.total {{ fill:{TEXT}; font-size:15px; font-weight:700; }}
  .c {{ transform-box:fill-box; transform-origin:center; opacity:1; }}
  .g {{ animation:pop {CYCLE}s cubic-bezier(.2,.8,.2,1) infinite both, flash {CYCLE}s ease-out infinite both; }}
  @keyframes pop {{
    0%{{opacity:.16;transform:scale(.72)}}
    8%{{opacity:1;transform:scale(1.12)}}
    14%,34%{{opacity:1;transform:scale(1)}}
    50%,100%{{opacity:.16;transform:scale(.82)}}
  }}
  @keyframes flash {{
    0%{{filter:brightness(.85)}}
    8%{{filter:brightness(2.35)}}
    16%,34%{{filter:brightness(1)}}
    50%,100%{{filter:brightness(.85)}}
  }}
  @media (prefers-reduced-motion: reduce) {{ .g {{ opacity:1 !important; transform:none !important; filter:none !important; animation:none !important; }} }}
</style>
<rect width="{width}" height="{height}" fill="none"/>
{''.join(labels)}
{''.join(rects)}
<text class="total" x="{LEFT}" y="{height - 6}">{total:,} contributions in the last year</text>
<!-- generated for {username} -->
</svg>'''


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else "eeminionn"
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "contrib-heatmap.svg"
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    svg = render(username, data)
    output.write_text(svg, encoding="utf-8")
    print(f"wrote {output}: {len(svg)} bytes")


if __name__ == "__main__":
    main()
