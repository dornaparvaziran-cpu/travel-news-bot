import os
import requests
import feedparser
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
METIS_KEY = os.getenv("METIS_KEY") # کلید متیس

FEEDS = [
    "https://www.irna.ir/rss",
    "https://www.isna.ir/rss",
    "https://khabarfarsi.com/rss",
    "https://www.yjc.ir/fa/rss",
    "https://www.tasnimnews.ir/fa/rss",
    "https://www.tabnak.ir/fa/rss",
    "https://www.javanonline.ir/fa/rss",
    "https://snn.ir/fa/rss",
    "https://www.entekhab.ir/fa/rss",
    "https://www.mehrnews.com/rss/tp/37",
  
    
]

KEYWORDS = [
    "گردشگری", "توریسم", "هواپیمایی", "هواپیما", "پرواز",
    "ایرلاین", "فرودگاه", "بلیط", "سفر",
    "tourism", "airline", "flight", "travel", "aviation",
]

SENT_FILE = "sent_links.txt"

def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_sent(links):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    r = requests.post(url, data=payload, timeout=20)
    if not r.ok:
        print("Telegram error:", r.text)
    return r.ok

# ---------- اتصال به هوش مصنوعی ایرانی متیس ----------
def summarize_with_ai(title):
    if not METIS_KEY:
        return title
    
    url = "https://api.metisai.ir/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {METIS_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"این تیتر خبر در حوزه گردشگری یا هواپیمایی است: '{title}'\nیک خلاصه بسیار کوتاه و جذاب (حداکثر ۲ خط) به زبان فارسی برای کانال تلگرام بنویس. لحن آن خبری و حرفه‌ای باشد. فقط متن خلاصه را برگردان و هیچ توضیح اضافه‌ای نده."
    
    data = {
        "model": "gpt-4o-mini", # متیس از این مدل پشتیبانی می‌کند
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        if r.ok:
            res = r.json()
            summary = res['choices'][0]['message']['content']
            return summary.strip()
        else:
            print("AI error:", r.text)
            return title
    except Exception as e:
        print("AI exception:", e)
        return title

def fetch_news(max_per_feed=3):
    sent = load_sent()
    collected = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= max_per_feed:
                    break
                title = entry.get("title", "")
                link = entry.get("link", "")
                if not title or not link:
                    continue
                if link in sent:
                    continue
                if not any(kw.lower() in title.lower() for kw in KEYWORDS):
                    continue
                collected.append((title, link))
                count += 1
        except Exception as e:
            print(f"Feed error {url}: {e}")
    return collected

def main():
    print(f"Start: {datetime.now()}")
    news = fetch_news()
    if not news:
        print("No new news.")
        return

    send_message("📰 <b>اخبار گردشگری و هواپیمایی</b>\n")

    sent = load_sent()
    for title, link in news:
        summary = summarize_with_ai(title)
        
        text = f"🔹 <b>{summary}</b>\n\n🔗 <a href='{link}'>ادامه خبر</a>"
        
        if send_message(text):
            sent.add(link)
            print(f"Sent: {title[:60]}")
        else:
            print(f"Failed: {title[:60]}")

    save_sent(sent)

if __name__ == "__main__":
    main()
