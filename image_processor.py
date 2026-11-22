"""Reusable image compositor for Dorna Parvaz batch processing."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageOps

WIDTH = 750
HEIGHT = 450
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def _cover_crop(image: Image.Image, size: tuple[int, int], focal_point=(0.5, 0.5)) -> Image.Image:
    """Resize to cover the target while keeping the requested focal point in view.

    focal_point uses normalized coordinates (0..1) in the source image.
    """
    width, height = size
    source = ImageOps.exif_transpose(image).convert("RGB")
    sw, sh = source.size
    scale = max(width / sw, height / sh)
    rw, rh = max(width, round(sw * scale)), max(height, round(sh * scale))
    resized = source.resize((rw, rh), Image.Resampling.LANCZOS)

    fx = min(1.0, max(0.0, float(focal_point[0])))
    fy = min(1.0, max(0.0, float(focal_point[1])))
    left = round(fx * rw - width / 2)
    top = round(fy * rh - height / 2)
    left = min(max(0, left), rw - width)
    top = min(max(0, top), rh - height)
    return resized.crop((left, top, left + width, top + height))


def process_image(
    source_path: str | Path,
    overlay_path: str | Path,
    output_path: str | Path,
    *,
    quality: int = 85,
    focal_point=(0.5, 0.5),
) -> Path:
    """Apply the transparent frame and save a 750x450 WebP image."""
    source_path, overlay_path, output_path = map(Path, (source_path, overlay_path, output_path))
    if not 1 <= int(quality) <= 100:
        raise ValueError("quality must be between 1 and 100")

    with Image.open(source_path) as opened:
        photo = _cover_crop(opened, (WIDTH, HEIGHT), focal_point)

    with Image.open(overlay_path) as opened_overlay:
        overlay = ImageOps.exif_transpose(opened_overlay).convert("RGBA")
    if overlay.size != (WIDTH, HEIGHT):
        raise ValueError(
            f"overlay must be exactly {WIDTH}x{HEIGHT}; received {overlay.width}x{overlay.height}"
        )

    canvas = photo.convert("RGBA")
    canvas.alpha_composite(overlay)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, "WEBP", quality=int(quality), method=6)
    return output_path


def is_supported_image(path: str | Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_SUFFIXES
