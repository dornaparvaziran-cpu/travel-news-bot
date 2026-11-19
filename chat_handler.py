import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TEXT = os.environ.get("MESSAGE_TEXT", "")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

if __name__ == "__main__":
    print(f"Received message: {TEXT}")
    
    if TEXT == "/start":
        reply = "سلام رفیق! ربات خصوصی با موفقیت وصل شد. حالا می‌تونیم بریم سراغ رزرو بلیط."
    else:
        reply = f"پیام تو: {TEXT}\n(ربات هنوز رزرو بلد نیست، فقط تست اتصال بود)"
        
    send_message(CHAT_ID, reply)
