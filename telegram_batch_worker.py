"""Process a photo batch submitted by the Cloudflare Telegram webhook.

The Cloudflare Worker collects Telegram file_ids and dispatches this workflow
only after the admin sends /done. Image processing remains on GitHub Actions.
"""
from __future__ import annotations

import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

import requests
from image_processor import process_image

BOT_TOKEN = os.environ["PHOTO_BOT_TOKEN"]
CHAT_ID = str(os.getenv("BATCH_CHAT_ID", "")).strip()
RAW_FILE_IDS = os.getenv("BATCH_FILE_IDS", "[]")
MAX_BATCH = int(os.getenv("MAX_BATCH", "30"))
MAX_FILE_BYTES = 15 * 1024 * 1024
QUALITY = int(os.getenv("WEBP_QUALITY", "85"))
FRAME = Path("assets/dorna_frame.png")
TG = f"https://api.telegram.org/bot{BOT_TOKEN}"


def telegram(method: str, **data):
    response = requests.post(f"{TG}/{method}", data=data, timeout=60)
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(result.get("description", f"Telegram {method} failed"))
    return result["result"]


def reply(chat_id: str, text: str):
    telegram("sendMessage", chat_id=chat_id, text=text)


def get_photo_bytes(file_id: str) -> bytes:
    info = telegram("getFile", file_id=file_id)
    response = requests.get(
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/{info['file_path']}",
        timeout=60,
    )
    response.raise_for_status()
    data = response.content
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("حجم هر عکس نباید بیشتر از ۱۵ مگابایت باشد.")
    return data


def finish_batch(chat_id: str, file_ids: list[str]):
    if not FRAME.is_file():
        raise FileNotFoundError(f"قاب در مسیر {FRAME} پیدا نشد.")
    with tempfile.TemporaryDirectory(prefix="dorna-batch-") as folder:
        root = Path(folder)
        input_dir = root / "input"
        output_dir = root / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        report = {"processed": [], "failed": []}
        for index, file_id in enumerate(file_ids, 1):
            try:
                raw = get_photo_bytes(file_id)
                source = input_dir / f"photo_{index:03d}.jpg"
                source.write_bytes(raw)
                target = output_dir / f"dorna_{index:03d}.webp"
                process_image(source, FRAME, target, quality=QUALITY)
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
    try:
        file_ids = json.loads(RAW_FILE_IDS)
    except json.JSONDecodeError as exc:
        raise ValueError("BATCH_FILE_IDS is not valid JSON.") from exc

    if not isinstance(file_ids, list) or not file_ids:
        raise ValueError("No photo file IDs were supplied to this workflow.")
    if len(file_ids) > MAX_BATCH:
        raise ValueError(f"Batch contains {len(file_ids)} photos; maximum is {MAX_BATCH}.")
    if not all(isinstance(item, str) and item for item in file_ids):
        raise ValueError("One or more Telegram file IDs are invalid.")

    reply(CHAT_ID, f"{len(file_ids)} عکس دریافت شد. پردازش را شروع می‌کنم…")
    finish_batch(CHAT_ID, file_ids)


if __name__ == "__main__":
    main()
