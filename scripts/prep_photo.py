#!/usr/bin/env python3
"""Prepare a local portrait image for the ASCII SVG generator."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "source-photo.jpg"
DEFAULT_OUTPUT = HERE.parent / "source-prepped.png"
TARGET_RATIO = 100 / 53


def crop_to_ratio(image: Image.Image, ratio: float) -> Image.Image:
    width, height = image.size
    current = width / height
    if current > ratio:
        new_width = int(height * ratio)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))
    new_height = int(width / ratio)
    top = max(0, (height - new_height) // 2)
    return image.crop((0, top, width, top + new_height))


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    image = Image.open(source).convert("RGBA")

    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    image = Image.alpha_composite(white, image)
    image = crop_to_ratio(image, TARGET_RATIO).convert("L")
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.3)
    image = ImageEnhance.Brightness(image).enhance(1.08)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"wrote {output}: {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
