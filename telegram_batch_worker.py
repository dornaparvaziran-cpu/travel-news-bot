"""Process Telegram image batches and preserve uploaded document filenames."""
from __future__ import annotations

import io
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path

import requests
from PIL import Image, ImageOps
from image_processor import process_image

BOT_TOKEN = os.environ["PHOTO_BOT_TOKEN"]
CHAT_ID = str(os.getenv("BATCH_CHAT_ID", "")).strip()
RAW_FILE_IDS = os.getenv("BATCH_FILE_IDS", "[]")
RAW_BATCH_FILES = os.getenv("BATCH_FILES", "[]")
FRAME_URL = str(os.getenv("FRAME_URL", "")).strip()
MAX_BATCH = int(os.getenv("MAX_BATCH", "30"))
MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_FRAME_BYTES = 20 * 1024 * 1024
QUALITY = int(os.getenv("WEBP_QUALITY", "85"))
FRAME_SIZE = (750, 450)
TG = f"https://api.telegram.org/bot{BOT_TOKEN}"

FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "BMP": ".bmp",
    "TIFF": ".tiff",
}


def telegram(method: str, **data):
    response = requests.post(f"{TG}/{method}", data=data, timeout=60)
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(result.get("description", f"Telegram {method} failed"))
    return result["result"]


def reply(chat_id: str, text: str):
    telegram("sendMessage", chat_id=chat_id, text=text)


def download_frame(destination: Path) -> Path:
    """Download and validate the current transparent PNG frame."""
    if not FRAME_URL:
        raise ValueError("متغیر FRAME_URL در GitHub Actions تعریف نشده است.")

    response = requests.get(
        FRAME_URL,
        headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        timeout=45,
    )
    response.raise_for_status()
    data = response.content

    if not data:
        raise ValueError("فایل قاب از آدرس FRAME_URL خالی دریافت شد.")
    if len(data) > MAX_FRAME_BYTES:
        raise ValueError("حجم فایل قاب بیشتر از ۲۰ مگابایت است.")
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        content_type = response.headers.get("Content-Type", "نامشخص")
        raise ValueError(
            f"آدرس FRAME_URL فایل PNG معتبر برنگرداند (Content-Type: {content_type})."
        )

    try:
        with Image.open(io.BytesIO(data)) as source_frame:
            if source_frame.format != "PNG":
                raise ValueError("فرمت فایل قاب PNG نیست.")
            source_frame.verify()

        with Image.open(io.BytesIO(data)) as source_frame:
            frame = source_frame.convert("RGBA")
            original_size = frame.size
            frame.thumbnail(FRAME_SIZE, Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
            x = (FRAME_SIZE[0] - frame.width) // 2
            y = (FRAME_SIZE[1] - frame.height) // 2
            canvas.alpha_composite(frame, (x, y))
            canvas.save(destination, format="PNG", optimize=True)
    except Exception as exc:
        raise ValueError(f"فایل قاب PNG خراب یا غیرقابل‌خواندن است: {exc}") from exc

    print(
        f"Frame downloaded and fitted without cropping: "
        f"{original_size[0]}x{original_size[1]} -> "
        f"{FRAME_SIZE[0]}x{FRAME_SIZE[1]}"
    )
    return destination


def get_file_bytes(file_id: str) -> bytes:
    info = telegram("getFile", file_id=file_id)
    response = requests.get(
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/{info['file_path']}",
        timeout=60,
    )
    response.raise_for_status()
    data = response.content
    if not data:
        raise ValueError("فایل دریافتی از تلگرام خالی است.")
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("حجم هر عکس نباید بیشتر از ۱۵ مگابایت باشد.")
    return data


def safe_output_stem(filename: str | None, index: int) -> str:
    """Strip paths and unsafe characters; never trust Telegram's filename as a path."""
    raw = str(filename or "").replace("\\", "/").split("/")[-1]
    stem = Path(raw).stem
    cleaned = "".join(ch for ch in stem if ch.isalnum() or ch in ("-", "_", ".", " "))
    cleaned = re.sub(r"\s+", "_", cleaned).strip(" ._-")
    cleaned = cleaned[:100].rstrip(" ._-")
    return cleaned or f"photo_{index:03d}"


def parse_batch_files() -> list[dict[str, str | None]]:
    """Read new filename-aware payload; fall back to the legacy file_ids array."""
    try:
        files = json.loads(RAW_BATCH_FILES or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError("BATCH_FILES is not valid JSON.") from exc

    if files:
        if not isinstance(files, list):
            raise ValueError("BATCH_FILES must be a JSON array.")
        normalized = []
        for item in files:
            if not isinstance(item, dict):
                raise ValueError("An item in BATCH_FILES is invalid.")
            file_id = item.get("file_id")
            filename = item.get("file_name")
            if not isinstance(file_id, str) or not file_id:
                raise ValueError("A Telegram file ID is missing or invalid.")
            if filename is not None and not isinstance(filename, str):
                filename = None
            normalized.append({"file_id": file_id, "file_name": filename})
        return normalized

    try:
        file_ids = json.loads(RAW_FILE_IDS)
    except json.JSONDecodeError as exc:
        raise ValueError("BATCH_FILE_IDS is not valid JSON.") from exc

    if not isinstance(file_ids, list):
        raise ValueError("BATCH_FILE_IDS must be a JSON array.")
    if not all(isinstance(item, str) and item for item in file_ids):
        raise ValueError("One or more Telegram file IDs are invalid.")
    return [{"file_id": item, "file_name": None} for item in file_ids]


def detect_image_extension(raw: bytes) -> str:
    """Validate actual image content and derive a trusted extension from its format."""
    try:
        with Image.open(io.BytesIO(raw)) as image:
            image_format = image.format
            image.verify()
    except Exception as exc:
        raise ValueError(f"فایل ارسالی تصویر معتبر نیست: {exc}") from exc

    extension = FORMAT_EXTENSIONS.get(str(image_format).upper())
    if not extension:
        raise ValueError(f"فرمت تصویر پشتیبانی نمی‌شود: {image_format}")
    return extension


def unique_output_path(output_dir: Path, stem: str, used: set[str]) -> Path:
    candidate = stem
    suffix = 2
    while f"{candidate.casefold()}.webp" in used:
        candidate = f"{stem}_{suffix}"
        suffix += 1
    used.add(f"{candidate.casefold()}.webp")
    return output_dir / f"{candidate}.webp"


def finish_batch(chat_id: str, files: list[dict[str, str | None]]):
    with tempfile.TemporaryDirectory(prefix="dorna-batch-") as folder:
        root = Path(folder)
        input_dir = root / "input"
        output_dir = root / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        frame_path = root / "dorna_frame.png"
        try:
            download_frame(frame_path)
        except Exception as exc:
            message = f"قاب دریافت یا تأیید نشد؛ پردازش عکس‌ها انجام نشد.\nعلت: {str(exc)[:500]}"
            print("FRAME_DOWNLOAD_ERROR:", str(exc))
            reply(chat_id, message)
            return

        report = {"processed": [], "failed": []}
        used_names: set[str] = set()

        for index, item in enumerate(files, 1):
            try:
                raw = get_file_bytes(str(item["file_id"]))
                extension = detect_image_extension(raw)
                stem = safe_output_stem(item.get("file_name"), index)

                source = input_dir / f"source_{index:03d}{extension}"
                source.write_bytes(raw)

                target = unique_output_path(output_dir, stem, used_names)
                process_image(source, frame_path, target, quality=QUALITY)
                report["processed"].append(target.name)
            except Exception as exc:
                report["failed"].append(f"{index}: {str(exc)[:160]}")

        if not report["processed"]:
            details = "\n".join(report["failed"][:15]) or "علت خطا ثبت نشده است."
            print("All photos failed:\n" + details)
            reply(chat_id, "هیچ عکسی پردازش نشد. علت خطا برای هر عکس:\n" + details)
            return

        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(output_dir.glob("*.webp")):
                bundle.write(path, path.name)
            bundle.writestr("report.json", json.dumps(report, ensure_ascii=False, indent=2))
        archive.seek(0)
        response = requests.post(
            f"{TG}/sendDocument",
            data={
                "chat_id": chat_id,
                "caption": (
                    f"پردازش درناپرواز کامل شد: {len(report['processed'])} عکس "
                    f"| WebP کیفیت {QUALITY}"
                ),
            },
            files={"document": ("dorna_photos.zip", archive, "application/zip")},
            timeout=180,
        )
        response.raise_for_status()
        if report["failed"]:
            reply(chat_id, "برخی عکس‌ها پردازش نشدند:\n" + "\n".join(report["failed"][:15]))


def main():
    if not CHAT_ID:
        raise ValueError("BATCH_CHAT_ID is missing; this workflow must be triggered by the photo webhook.")

    files = parse_batch_files()
    if not files:
        raise ValueError("No photo files were supplied to this workflow.")
    if len(files) > MAX_BATCH:
        raise ValueError(f"Batch contains {len(files)} photos; maximum is {MAX_BATCH}.")

    reply(CHAT_ID, f"{len(files)} عکس دریافت شد. پردازش را شروع می‌کنم…")
    finish_batch(CHAT_ID, files)


if __name__ == "__main__":
    main()
