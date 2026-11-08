import os
import requests
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GIST_ID = os.environ.get("GIST_ID")
GIST_TOKEN = os.environ.get("GIST_TOKEN")

# 👇 لینک کانال خود را اینجا بگذار
CHANNEL_LINK = "https://t.me/dornaparvazch" 

def get_gist_file(filename):
    """خواندن یک فایل از Gist"""
    if not GIST_ID or not GIST_TOKEN: return ""
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.ok:
            return r.json().get("files", {}).get(filename, {}).get("content", "").strip()
    except Exception as e:
        print(f"Load error: {e}")
    return ""

def save_gist_file(filename, content):
    """ذخیره یک فایل در Gist"""
    if not GIST_ID or not GIST_TOKEN: return
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"files": {filename: {"content": content}}}
    try:
        requests.patch(url, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(f"Save error: {e}")

def process_new_users():
    # ۱. خواندن آخرین آیدی پیام و لیست کاربران از Gist
    last_id_str = get_gist_file("last_update_id.txt")
    last_id = int(last_id_str) if last_id_str.isdigit() else 0
    
    subs_str = get_gist_file("subscribers.txt")
    subscribers = set(subs_str.splitlines()) if subs_str else set()

    # ۲. گرفتن پیام‌های جدید از تلگرام (با استفاده از offset برای جلوگیری از تکرار)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    if last_id > 0:
        url += f"?offset={last_id + 1}"
        
    try:
        r = requests.get(url, timeout=15)
        if not r.ok: return
        
        updates = r.json().get("result", [])
        if not updates: 
            print("No new updates.")
            return
            
        max_id = last_id
        new_subs_added = False
        
        for u in updates:
            max_id = max(max_id, u["update_id"])
            
            if "message" in u and "chat" in u["message"]:
                chat_id = str(u["message"]["chat"]["id"])
                first_name = u["message"]["chat"].get("first_name", "کاربر")
                text = u["message"].get("text", "")
                
                # ۳. اگر پیام استارت بود و کاربر قبلاً عضو لیست نبود
                if text.startswith("/start") and chat_id not in subscribers:
                    print(f"Welcoming new user: {first_name} ({chat_id})")
                    
                    welcome_text = (
                        f"سلام {first_name} عزیز! 👋\n\n"
                        f"به ربات درنا تراول خوش آمدید.\n"
                        f"برای دریافت آخرین اخبار، قیمت‌ها و پیشنهادهای ویژه، به کانال تلگرام ما بپیوندید:\n\n"
                        f"{CHANNEL_LINK}"
                    )
                    
                    payload = {
                        "chat_id": chat_id, 
                        "text": welcome_text, 
                        "disable_web_page_preview": False
                    }
                    res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload, timeout=10)
                    
                    if res.ok:
                        subscribers.add(chat_id)
                        new_subs_added = True
                        print(f"✅ Sent to {first_name}")
                    else:
                        print(f"❌ Failed to send to {chat_id}: {res.text}")
                        
                    # کمی صبر برای جلوگیری از بلاک شدن
                    time.sleep(1)
        
        # ۴. ذخیره آیدی جدیدترین پیام برای اینکه دفعه بعد دوباره خونده نشه
        if max_id > last_id:
            save_gist_file("last_update_id.txt", str(max_id))
            
        # ۵. ذخیره لیست جدید کاربران
        if new_subs_added:
            save_gist_file("subscribers.txt", "\n".join(subscribers))
            print(f"Updated subscribers list. Total: {len(subscribers)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_new_users()
