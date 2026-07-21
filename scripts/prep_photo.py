#!/usr/bin/env python3
"""Prepare a local portrait image for the ASCII SVG generator."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image, ImageEnhance


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "source-photo.png"
DEFAULT_OUTPUT = HERE.parent / "source-prepped.png"
TARGET_RATIO = float(os.environ.get("PORTRAIT_RATIO", "1.0"))
PORTRAIT_ZOOM = float(os.environ.get("PORTRAIT_ZOOM", "1.0"))
PORTRAIT_FOCUS_X = float(os.environ.get("PORTRAIT_FOCUS_X", "0.50"))
PORTRAIT_FOCUS_Y = float(os.environ.get("PORTRAIT_FOCUS_Y", "0.50"))


def crop_to_ratio(image: Image.Image, ratio: float) -> Image.Image:
    width, height = image.size
    crop_width = min(width, int(height * ratio))
    crop_width = max(1, int(crop_width / max(1.0, PORTRAIT_ZOOM)))
    crop_height = max(1, int(crop_width / ratio))
    center_x = width * PORTRAIT_FOCUS_X
    center_y = height * PORTRAIT_FOCUS_Y
    left = int(max(0, min(width - crop_width, center_x - crop_width / 2)))
    top = int(max(0, min(height - crop_height, center_y - crop_height / 2)))
    return image.crop((left, top, left + crop_width, top + crop_height))


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    image = Image.open(source).convert("RGBA")

    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    image = Image.alpha_composite(white, image)
    image = crop_to_ratio(image, TARGET_RATIO).convert("RGB")
    image = ImageEnhance.Color(image).enhance(1.08)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    image = ImageEnhance.Brightness(image).enhance(1.08)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"wrote {output}: {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
