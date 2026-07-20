#!/usr/bin/env python3
"""Prepare a local portrait image for the ASCII SVG generator."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "source-photo.jpg"
DEFAULT_OUTPUT = HERE.parent / "source-prepped.png"
TARGET_RATIO = 100 / 53
PORTRAIT_ZOOM = float(os.environ.get("PORTRAIT_ZOOM", "1.32"))
PORTRAIT_FOCUS_X = float(os.environ.get("PORTRAIT_FOCUS_X", "0.47"))
PORTRAIT_FOCUS_Y = float(os.environ.get("PORTRAIT_FOCUS_Y", "0.52"))


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


def median_background_color(image: Image.Image) -> tuple[int, int, int]:
    width, height = image.size
    samples: list[tuple[int, int, int]] = []
    step_x = max(1, width // 20)
    step_y = max(1, height // 20)
    for x in range(0, width, step_x):
        for y in range(0, height, step_y):
            if x > width * 0.74 or y < height * 0.18 or x < width * 0.08:
                samples.append(image.getpixel((min(x, width - 1), min(y, height - 1))))
    if not samples:
        samples.append(image.getpixel((0, 0)))
    return tuple(sorted(pixel[channel] for pixel in samples)[len(samples) // 2] for channel in range(3))


def lift_background(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    gray = rgb.convert("L")
    bg = median_background_color(rgb)
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, bg)).convert("L")
    differs_from_wall = diff.point(lambda pixel: 255 if pixel > 28 else 0)
    dark_subject = gray.point(lambda pixel: 255 if pixel < 112 else 0)
    mask = ImageChops.lighter(differs_from_wall, dark_subject)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=max(4, int(rgb.size[0] * 0.018))))
    return Image.composite(gray, Image.new("L", rgb.size, 255), mask)


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    image = Image.open(source).convert("RGBA")

    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    image = Image.alpha_composite(white, image)
    image = crop_to_ratio(image, TARGET_RATIO)
    image = lift_background(image)
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.45)
    image = ImageEnhance.Brightness(image).enhance(1.10)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"wrote {output}: {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
