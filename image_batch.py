"""CLI batch runner: process a folder of photos and package results as ZIP."""
from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path

from image_processor import is_supported_image, process_image


def process_folder(input_dir: Path, overlay: Path, zip_path: Path, quality: int = 85) -> dict:
    if not input_dir.is_dir():
        raise NotADirectoryError(input_dir)
    if not overlay.is_file():
        raise FileNotFoundError(f"Frame overlay not found: {overlay}")

    images = sorted(p for p in input_dir.iterdir() if p.is_file() and is_supported_image(p))
    if not images:
        raise ValueError(f"No supported images found in {input_dir}")

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"processed": [], "failed": []}
    with tempfile.TemporaryDirectory(prefix="dorna-images-") as tmp:
        output_dir = Path(tmp) / "processed"
        for index, source in enumerate(images, 1):
            target = output_dir / f"{index:03d}_{source.stem}.webp"
            try:
                process_image(source, overlay, target, quality=quality)
                report["processed"].append({"source": source.name, "output": target.name})
            except Exception as exc:  # keep a bad image from aborting the whole batch
                report["failed"].append({"source": source.name, "error": str(exc)})

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(output_dir.glob("*.webp")):
                archive.write(file, arcname=file.name)
            archive.writestr("processing-report.json", json.dumps(report, ensure_ascii=False, indent=2))

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="DornaParvaz batch photo compositor")
    parser.add_argument("input_dir", type=Path, help="Folder containing source photos")
    parser.add_argument("--overlay", type=Path, default=Path("assets/dorna_frame.png"))
    parser.add_argument("--output", type=Path, default=Path("processed_images.zip"))
    parser.add_argument("--quality", type=int, default=85)
    args = parser.parse_args()

    report = process_folder(args.input_dir, args.overlay, args.output, args.quality)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"ZIP saved to: {args.output}")


if __name__ == "__main__":
    main()
