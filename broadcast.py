import os
import requests
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GIST_ID = os.environ.get("GIST_ID")
GIST_TOKEN = os.environ.get("GIST_TOKEN")
CHANNEL_LINK = "https://t.me/dornaparvazch" # 👈 اینجا لینک کانال رو بذار

GIST_FILE_NAME = "subscribers.txt"

def load_subscribers():
    """خواندن لیست chat_id ها از Gist"""
    if not GIST_ID or not GIST_TOKEN: return set()
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.ok:
            content = r.json().get("files", {}).get(GIST_FILE_NAME, {}).get("content", "").strip()
            if content: return set(content.splitlines())
    except Exception as e:
        print(f"Load error: {e}")
    return set()

def save_subscribers(subs):
    """ذخیره لیست chat_id ها در Gist"""
    if not GIST_ID or not GIST_TOKEN: return
    new_content = "\n".join(str(s) for s in subs)
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"files": {GIST_FILE_NAME: {"content": new_content}}}
    try:
        requests.patch(url, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(f"Save error: {e}")

def get_new_users():
    """گرفتن کاربران جدیدی که ربات را استارت کرده‌اند"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        r = requests.get(url, timeout=15)
        if r.ok:
            updates = r.json().get("result", [])
            new_users = []
            for update in updates:
                if "message" in update and "chat" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    new_users.append(chat_id)
            return new_users
    except Exception as e:
        print(f"Get updates error: {e}")
    return []

def broadcast():
    """ارسال لینک کانال به همه کاربران با تاخیر"""
    subs = load_subscribers()
    
    # ۱. اول کاربران جدید رو پیدا کن و به لیست اضافه کن
    new_users = get_new_users()
    if new_users:
        print(f"Found {len(new_users)} new users. Updating list...")
        for u in new_users:
            subs.add(u)
        save_subscribers(subs)
        
    if not subs:
        print("No subscribers found yet.")
        return

    print(f"Starting broadcast to {len(subs)} users...")
    
    message_text = f"🔗 <b>عضویت در کانال رسمی ما</b>\n\nبرای دریافت آخرین اخبار و پیشنهادهای ویژه، به کانال تلگرام ما بپیوندید:\n{CHANNEL_LINK}"
    
    success_count = 0
    for chat_id in subs:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            res = requests.post(url, data=payload, timeout=10)
            
            if res.status_code == 429:
                retry_after = res.json().get("parameters", {}).get("retry_after", 30)
                print(f"Rate limit. Sleeping {retry_after}s...")
                time.sleep(retry_after)
                requests.post(url, data=payload, timeout=10)
            elif res.ok:
                success_count += 1
            else:
                print(f"Failed for {chat_id}: {res.text}")
        except Exception as e:
            print(f"Error for {chat_id}: {e}")
            
        # ⚠️ مهم‌ترین بخش: تاخیر ۱.۵ ثانیه‌ای بین هر پیام
        time.sleep(1.5) 
        
    print(f"Broadcast finished. Sent to {success_count} users.")

if __name__ == "__main__":
    broadcast()
