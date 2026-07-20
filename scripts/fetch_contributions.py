#!/usr/bin/env python3
"""Fetch public GitHub contribution data for the profile heatmap."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = os.environ.get("GH_PROFILE_USER", "eeminionn")
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"


def contribution_level(count: int) -> int:
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    return 4


def parse_count(text: str) -> int:
    if re.search(r"no contributions", text, re.I):
        return 0
    match = re.search(r"([\d,]+)\s+contribution", text, re.I)
    if not match:
        match = re.match(r"([\d,]+)", text)
    return int(match.group(1).replace(",", "")) if match else 0


def fetch_days() -> list[dict[str, int | str]]:
    response = requests.get(
        URL,
        headers={"User-Agent": "eeminionn-profile-readme-bot/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("no contribution calendar cells found", file=sys.stderr)
        sys.exit(1)

    days: list[dict[str, int | str]] = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        tooltip = soup.find("tool-tip", attrs={"for": td.get("id")}) if td.get("id") else None
        count = parse_count(tooltip.get_text(" ", strip=True) if tooltip else "")
        raw_level = td.get("data-level")
        try:
            level = int(raw_level) if raw_level is not None else contribution_level(count)
        except ValueError:
            level = contribution_level(count)
        days.append({"date": date, "count": count, "level": max(0, min(level, 4))})

    days.sort(key=lambda day: str(day["date"]))
    return days


def streaks(days: list[dict[str, int | str]]) -> tuple[int, int]:
    current = 0
    idx = len(days) - 1
    if idx >= 0 and int(days[idx]["count"]) == 0:
        idx -= 1
    while idx >= 0 and int(days[idx]["count"]) > 0:
        current += 1
        idx -= 1

    longest = run = 0
    for day in days:
        if int(day["count"]) > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return current, longest


def build_payload(days: list[dict[str, int | str]]) -> dict[str, object]:
    total = sum(int(day["count"]) for day in days)
    active_days = sum(1 for day in days if int(day["count"]) > 0)
    best_day = max(days, key=lambda day: int(day["count"]))
    current, longest = streaks(days)

    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active_days,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "days": days,
    }


def main() -> None:
    days = fetch_days()
    payload = build_payload(days)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {OUT_PATH}: {payload['total_contributions']} contributions, "
        f"{payload['active_days']} active days"
    )


if __name__ == "__main__":
    main()
