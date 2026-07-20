#!/usr/bin/env python3
"""Prepare a local portrait image for the ASCII SVG generator."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "source-photo.jpg"
DEFAULT_OUTPUT = HERE.parent / "source-prepped.png"
TARGET_RATIO = 74 / 39
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


def subject_mask(size: tuple[int, int]) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # Tuned for close portrait selfies: keep head/hair/neck and remove wall noise.
    shapes = [
        (0.45, 0.28, 0.32, 0.42, 255),
        (0.43, 0.48, 0.22, 0.28, 210),
    ]
    for cx, cy, rx, ry, value in shapes:
        draw.ellipse(
            (
                int((cx - rx) * width),
                int((cy - ry) * height),
                int((cx + rx) * width),
                int((cy + ry) * height),
            ),
            fill=value,
        )

    torso = [(0.31, 0.58), (0.58, 0.58), (0.72, 1.05), (0.18, 1.05)]
    draw.polygon([(int(x * width), int(y * height)) for x, y in torso], fill=220)
    return mask.filter(ImageFilter.GaussianBlur(radius=max(5, int(width * 0.018))))


def prepare_ascii_luminance(image: Image.Image) -> Image.Image:
    gray = image.convert("L")
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.45)
    gray = ImageEnhance.Brightness(gray).enhance(1.10)

    edges = ImageOps.autocontrast(gray.filter(ImageFilter.FIND_EDGES))
    edge_darkener = edges.point(lambda pixel: max(0, 255 - int(pixel * 0.28)))
    gray = ImageChops.multiply(gray, edge_darkener)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.0, percent=120, threshold=2))

    return Image.composite(gray, Image.new("L", gray.size, 255), subject_mask(gray.size))


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    image = Image.open(source).convert("RGBA")

    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    image = Image.alpha_composite(white, image)
    image = crop_to_ratio(image, TARGET_RATIO)
    image = prepare_ascii_luminance(image)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"wrote {output}: {image.size[0]}x{image.size[1]}")


if __name__ == "__main__":
    main()
