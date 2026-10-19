import os
import requests
import feedparser
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
METIS_KEY = os.getenv("METIS_KEY")

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

# دسته‌بندی کلمات کلیدی
CATEGORIES = {
    "#هواپیمایی": ["هواپیمایی", "هواپیما", "پرواز", "ایرلاین", "فرودگاه", "بلیط", "airline", "flight", "aviation", "airport"],
    "#گردشگری": ["گردشگری", "توریسم", "سفر", "توریست", "هتل", "tourist", "travel", "tourism", "hotel"]
}
# کلمات کلیدی کلی برای فیلتر کردن
ALL_KEYWORDS = [kw for cat in CATEGORIES.values() for kw in cat]

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

# تشخیص دسته‌بندی
def get_category(title):
    title_lower = title.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw.lower() in title_lower for kw in keywords):
            return cat
    return "#اخبار"

# استخراج عکس از RSS
def get_image_url(entry):
    # ۱. بررسی تگ media_content (رایج در فیدهای خبری)
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    # ۲. بررسی تگ media_thumbnail
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0]['url']
    # ۳. بررسی تگ enclosures
    if 'enclosures' in entry:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href')
    # ۴. بررسی تگ links
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')
    return None

# ارسال عکس (اگر عکس بود) یا متن
def send_telegram_post(text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL_ID,
            "photo": image_url,
            "caption": text,
            "parse_mode": "HTML"
        }
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    
    try:
        r = requests.post(url, data=payload, timeout=20)
        if not r.ok:
            print("Telegram error:", r.text)
            # اگر ارسال عکس خطا داد، به عنوان جایگزین متن بفرست
            if image_url:
                print("Retrying as text...")
                return send_telegram_post(text, None)
            return False
        return True
    except Exception as e:
        print("Telegram exception:", e)
        return False

def summarize_with_ai(title):
    if not METIS_KEY:
        return title
    
    url = "https://api.metisai.ir/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {METIS_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"این تیتر خبر در حوزه گردشگری یا هواپیمایی است: '{title}'\nیک خلاصه بسیار کوتاه و جذاب (حداکثر ۲ خط) به زبان فارسی برای کانال تلگرام بنویس. لحن آن خبری و حرفه‌ای باشد. فقط متن خلاصه را برگردان."
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        if r.ok:
            return r.json()['choices'][0]['message']['content'].strip()
        return title
    except:
        return title

def fetch_news(max_per_feed=3):
    sent = load_sent()
    collected = []
    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            count = 0
            for entry in feed.entries:
                if count >= max_per_feed:
                    break
                title = entry.get("title", "")
                link = entry.get("link", "")
                if not title or not link or link in sent:
                    continue
                if not any(kw.lower() in title.lower() for kw in ALL_KEYWORDS):
                    continue
                
                image_url = get_image_url(entry)
                collected.append((title, link, image_url))
                count += 1
        except Exception as e:
            print(f"Feed error {feed_url}: {e}")
    return collected

def main():
    print(f"Start: {datetime.now()}")
    news = fetch_news()
    if not news:
        print("No new news.")
        return

    sent = load_sent()
    
    # ارسال یک پیام هدر (اختیاری - اگر نخواستی این را پاک کن)
   # send_telegram_post("📰 <b>اخبار گردشگری</b>\n")

    for title, link, image_url in news:
        summary = summarize_with_ai(title)
        category = get_category(title)
        
        # ساختار متن: خلاصه + لینک + هشتگ
        text = f"🔹 <b>{summary}</b>\n\n🔗 <a href='{link}'>مشاهده خبر کامل</a>\n\n{category}"
        
        if send_telegram_post(text, image_url):
            sent.add(link)
            print(f"Sent ({category}): {title[:50]}")
        else:
            print(f"Failed: {title[:50]}")

    save_sent(sent)

if __name__ == "__main__":
    main()
