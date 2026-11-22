"""Telegram batch intake worker, polled by GitHub Actions every five minutes.

Commands: /batch, upload photos, /done. Only ADMIN_CHAT_ID is allowed.
The batch state and Telegram update offset are stored in a private GitHub Gist.
"""
from __future__ import annotations

import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

import requests
from PIL import Image
from image_processor import process_image

BOT_TOKEN = os.environ["PHOTO_BOT_TOKEN"]
GIST_ID = os.environ["GIST_ID"]
GIST_TOKEN = os.environ["GIST_TOKEN"]
ADMIN_CHAT_ID = str(os.environ["ADMIN_CHAT_ID"])
MAX_BATCH = int(os.getenv("MAX_BATCH", "30"))
MAX_FILE_BYTES = 15 * 1024 * 1024
QUALITY = int(os.getenv("WEBP_QUALITY", "85"))
STATE_NAME = "dorna_photo_batch_state.json"
FRAME = Path("assets/dorna_frame.png")
TG = f"https://api.telegram.org/bot{BOT_TOKEN}"
GIST = f"https://api.github.com/gists/{GIST_ID}"
HEADERS = {"Authorization": f"Bearer {GIST_TOKEN}", "Accept": "application/vnd.github+json"}

def telegram(method: str, **data):
    response = requests.post(f"{TG}/{method}", data=data, timeout=45)
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(result.get("description", f"Telegram {method} failed"))
    return result["result"]

def reply(chat_id: str, text: str):
    telegram("sendMessage", chat_id=chat_id, text=text)

def load_state() -> dict:
    response = requests.get(GIST, headers=HEADERS, timeout=20)
    response.raise_for_status()
    content = response.json().get("files", {}).get(STATE_NAME, {}).get("content", "")
    try:
        state = json.loads(content) if content else {}
    except json.JSONDecodeError:
        state = {}
    state.setdefault("offset", 0)
    state.setdefault("active", False)
    state.setdefault("photos", [])
    return state

def save_state(state: dict):
    response = requests.patch(
        GIST, headers=HEADERS,
        json={"files": {STATE_NAME: {"content": json.dumps(state, ensure_ascii=False)}}},
        timeout=20,
    )
    response.raise_for_status()

def get_photo_bytes(file_id: str) -> bytes:
    info = telegram("getFile", file_id=file_id)
    response = requests.get(
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/{info['file_path']}",
        timeout=45,
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
            reply(chat_id, "هیچ عکسی پردازش نشد. تصاویر را دوباره ارسال کنید.")
            return
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(output_dir.glob("*.webp")):
                bundle.write(path, path.name)
            bundle.writestr("report.json", json.dumps(report, ensure_ascii=False, indent=2))
        archive.seek(0)
        response = requests.post(
            f"{TG}/sendDocument",
            data={"chat_id": chat_id, "caption": f"پردازش درناپرواز کامل شد: {len(report['processed'])} عکس | WebP کیفیت {QUALITY}"},
            files={"document": ("dorna_photos.zip", archive, "application/zip")},
            timeout=120,
        )
        response.raise_for_status()
        if report["failed"]:
            reply(chat_id, "برخی عکس‌ها پردازش نشدند:\n" + "\n".join(report["failed"][:15]))

def handle(message: dict, state: dict):
    chat_id = str(message.get("chat", {}).get("id", ""))
    if chat_id != ADMIN_CHAT_ID:
        return
    text = (message.get("text") or "").strip()
    if text.startswith("/start"):
        reply(chat_id, "ربات پردازش تصویر درناپرواز آماده است.\nشروع: /batch\nپایان و دریافت ZIP: /done")
    elif text == "/batch":
        state["active"] = True
        state["photos"] = []
        reply(chat_id, f"دریافت شروع شد. حداکثر {MAX_BATCH} عکس بفرستید؛ سپس /done را ارسال کنید.")
    elif text == "/done":
        photos = list(state["photos"])
        state["photos"] = []
        state["active"] = False
        if not photos:
            reply(chat_id, "عکسی دریافت نشده است. ابتدا /batch را بفرستید.")
        else:
            reply(chat_id, f"{len(photos)} عکس دریافت شد. در حال پردازش…")
            finish_batch(chat_id, photos)
    elif message.get("photo"):
        if not state["active"]:
            reply(chat_id, "برای شروع ابتدا /batch را ارسال کنید.")
        elif len(state["photos"]) >= MAX_BATCH:
            reply(chat_id, f"سقف این نوبت {MAX_BATCH} عکس است؛ /done را ارسال کنید.")
        else:
            state["photos"].append(message["photo"][-1]["file_id"])
            reply(chat_id, f"عکس {len(state['photos'])} دریافت شد.")
    elif text:
        reply(chat_id, "فرمان‌ها: /batch برای شروع و /done برای پایان.")

def main():
    state = load_state()
    updates = telegram(
        "getUpdates",
        offset=state["offset"] + 1,
        timeout=5,
        allowed_updates=json.dumps(["message"]),
    )
    for update in updates:
        state["offset"] = max(state["offset"], update["update_id"])
        message = update.get("message")
        if message:
            try:
                handle(message, state)
            except Exception as exc:
                chat_id = str(message.get("chat", {}).get("id", ""))
                if chat_id == ADMIN_CHAT_ID:
                    reply(chat_id, f"خطا: {str(exc)[:250]}")
    save_state(state)

if __name__ == "__main__":
    main()
