import os
import sys
import requests
import feedparser
import asyncio
import random
import re
from datetime import datetime
from playwright.async_api import async_playwright

TG_TOKEN = os.environ.get("BOT_TOKEN")
TG_CHANNEL = os.environ.get("CHANNEL_ID")
EITA_TOKEN = os.environ.get("EITA_TOKEN")
EITA_CHANNEL = os.environ.get("EITA_CHANNEL_ID")
METIS_KEY = os.environ.get("METIS_KEY")

ALL_ROUTES = [ 
    {"name": "تهران به مشهد", "url": "https://dornatravel.ir/flight/THR-MHD"},
    {"name": "مشهد به تهران", "url": "https://dornatravel.ir/flight/MHD-THR"},
    {"name": "تهران به کیش", "url": "https://dornatravel.ir/flight/THR-KIH"},
    {"name": "کیش به تهران", "url": "https://dornatravel.ir/flight/KIH-THR"},
    {"name": "مشهد به کیش", "url": "https://dornatravel.ir/flight/MHD-KIH"},
    {"name": "تهران به شیراز", "url": "https://dornatravel.ir/flight/THR-SYZ"},
    {"name": "تهران به اصفهان", "url": "https://dornatravel.ir/flight/THR-IFN"},
    {"name": "تهران به تبریز", "url": "https://dornatravel.ir/flight/THR-TBZ"},
    {"name": "مشهد به اهواز", "url": "https://dornatravel.ir/flight/MHD-AWZ"},
    {"name": "تهران به آبادان", "url": "https://dornatravel.ir/flight/THR-ABD"},
    {"name": "مشهد به آبادان", "url": "https://dornatravel.ir/flight/MHD-ABD"},
    {"name": "مشهد به تبریز", "url": "https://dornatravel.ir/flight/MHD-TBZ"},
    {"name": "مشهد به بندر", "url": "https://dornatravel.ir/flight/MHD-BND"},
    {"name": "مشهد به چابهار", "url": "https://dornatravel.ir/flight/MHD-ZBR"},
    {"name": "مشهد به رشت", "url": "https://dornatravel.ir/flight/MHD-RAS"},
    {"name": "تهران به زاهدان", "url": "https://dornatravel.ir/flight/THR-ZAH"},
    {"name": "مشهد به زاهدان", "url": "https://dornatravel.ir/flight/MHD-ZAH"},
    {"name": "تهران به بندر", "url": "https://dornatravel.ir/flight/THR-BND"},
    {"name": "تهران به چابهار", "url": "https://dornatravel.ir/flight/THR-ZBR"},
    {"name": "اهواز به رشت", "url": "https://dornatravel.ir/flight/AWZ-RAS"},
    {"name": "تهران به اهواز", "url": "https://dornatravel.ir/flight/THR-AWZ"},
    {"name": "شیراز به مشهد", "url": "https://dornatravel.ir/flight/SYZ-MHD"},
    {"name": "اصفهان به مشهد", "url": "https://dornatravel.ir/flight/IFN-MHD"},
    {"name": "تهران به استانبول", "url": "https://dornatravel.ir/flight/IKA-IST"},
    {"name": "تهران به دبی", "url": "https://dornatravel.ir/flight/IKA-DXB"},
    {"name": "مشهد به استانبول", "url": "https://dornatravel.ir/flight/MHD-IST"},
    {"name": "شیراز به دبی", "url": "https://dornatravel.ir/flight/SYZ-DXB"},
    {"name": "مشهد به نجف", "url": "https://dornatravel.ir/flight/MHD-NJF"},
    {"name": "تهران به نجف", "url": "https://dornatravel.ir/flight/IKA-NJF"},
    {"name": "نجف به مشهد", "url": "https://dornatravel.ir/flight/NJF-MHD"},
    {"name": "نجف به تهران", "url": "https://dornatravel.ir/flight/NJF-IKA"},
    {"name": "تهران به مسقط", "url": "https://dornatravel.ir/flight/IKA-MCT"},
]

NUMBER_OF_ROUTES = 5
MAX_NEWS_TO_SEND = 7 

FEEDS = [
    "https://www.irna.ir/rss",
    "https://www.isna.ir/rss",
    "https://khabarfarsi.com/rss",
    "https://www.yjc.ir/fa/rss",
    "https://www.tasnimnews.ir/fa/rss",
    "https://spnfa.ir/export/rss2/archive/index.xml",
    "https://www.radiofarda.com/api/zpoqil-vomx-tpe_kip",
]

CATEGORIES = {
    "#هواپیمایی": ["هواپیمایی", "هواپیما", "پرواز", "ایرلاین", "فرودگاه", "بلیط", "airline", "flight", "aviation", "airport"],
    "#گردشگری": ["گردشگری", "توریسم", "سفر", "توریست", "هتل", "tourist", "travel", "tourism", "hotel"]
}
ALL_KEYWORDS = [kw for cat in CATEGORIES.values() for kw in cat]
SENT_FILE = "sent_links.txt"

def load_sent():
    if not os.path.exists(SENT_FILE): return set()
    with open(SENT_FILE, "r", encoding="utf-8") as f: return set(line.strip() for line in f)

def save_sent(links):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        for link in links: f.write(link + "\n")

def get_category(title):
    title_lower = title.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw.lower() in title_lower for kw in keywords): return cat
    return "#اخبار"

def get_image_url(entry):
    if 'media_content' in entry and len(entry.media_content) > 0: return entry.media_content[0]['url']
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0: return entry.media_thumbnail[0]['url']
    if 'enclosures' in entry:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'): return enc.get('href')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'): return link.get('href')
    return None

# ---------- ۱. ارسال به تلگرام (HTML) ----------
def send_to_telegram(text, image_url=None):
    if not TG_TOKEN or not TG_CHANNEL: return False
    if image_url:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
        payload = {"chat_id": TG_CHANNEL, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHANNEL, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        r = requests.post(url, data=payload, timeout=20)
        if not r.ok:
            print("Telegram error:", r.text)
            if image_url: return send_to_telegram(text, None)
            return False
        return True
    except Exception as e:
        print("Telegram exception:", e)
        return False

# ---------- ۲. ارسال به ایتا (بدون تغییر فرمت) ----------
import urllib.parse

# ---------- ۲. ارسال به ایتا (با لینک‌های تمیز) ----------
def send_to_eita(text, image_url=None):
    if not EITA_TOKEN or not EITA_CHANNEL: 
        print("Eitaa Error: Token or Channel missing")
        return False
    
    # ۱. تبدیل تگ‌های بولد
    text_md = text.replace("<b>", "").replace("</b>", "")
    
    # ۲. پیدا کردن لینک‌ها و دیکد کردنشون
    def clean_link(match):
        url = match.group(1)
        try:
            # تبدیل %D8%B3... به حروف فارسی عادی
            decoded_url = urllib.parse.unquote(url)
            return f"{match.group(2)}: {decoded_url}"
        except:
            return f"{match.group(2)}: {url}"

    text_md = re.sub(r"<a href='([^']+)'>([^<]+)</a>", clean_link, text_md)
    
    base_url = f"https://eitaayar.ir/api/{EITA_TOKEN}"
    url = f"{base_url}/sendMessage"
    
    payload = {
        "chat_id": EITA_CHANNEL, 
        "text": text_md, 
        "disable_web_page_preview": False
    }
    
    try:
        r = requests.post(url, data=payload, timeout=20)
        print(f"Eitaa Response: {r.status_code} - {r.text}")
        if not r.ok:
            print("Eitaa error:", r.text)
            return False
        return True
    except Exception as e:
        print("Eitaa exception:", e)
        return False

# ---------- ۳. ارسال همزمان به هر دو ----------
def send_to_all(text, image_url=None):
    print("-> Sending to Telegram...")
    tg_ok = send_to_telegram(text, image_url)
    print("-> Sending to Eitaa...")
    eita_ok = send_to_eita(text, None) 
    return tg_ok or eita_ok

def summarize_with_ai(title):
    if not METIS_KEY: return title
    url = "https://api.metisai.ir/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {METIS_KEY}", "Content-Type": "application/json"}
    prompt = f"این تیتر خبر در حوزه گردشگری یا هواپیمایی است: '{title}'\nیک خلاصه بسیار کوتاه و جذاب (حداکثر ۲ خط) به زبان فارسی برای کانال تلگرام بنویس. لحن آن خبری و حرفه‌ای باشد. فقط متن خلاصه را برگردان."
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        if r.ok: return r.json()['choices'][0]['message']['content'].strip()
        return title
    except: return title

def fetch_news(max_per_feed=2):
    sent = load_sent()
    collected = []
    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            count = 0
            for entry in feed.entries:
                if count >= max_per_feed: break
                title = entry.get("title", "")
                link = entry.get("link", "")
                if not title or not link or link in sent: continue
                if not any(kw.lower() in title.lower() for kw in ALL_KEYWORDS): continue
                collected.append((title, link, get_image_url(entry)))
                count += 1
        except Exception as e: print(f"Feed error: {e}")
    return collected

async def get_prices_for_route(browser, route_name, route_url):
    page = await browser.new_page()
    try:
        await page.goto(route_url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)
        all_elements = await page.locator("body *").all()
        prices = []
        for el in all_elements:
            try:
                text = await el.inner_text()
                if "تومان" in text and len(text) < 30 and any(char.isdigit() for char in text):
                    if text not in prices: prices.append(text)
            except: pass
        await page.close()
        if not prices: return None
        
        result_text = f"✈️ <b>قیمت‌های لحظه‌ای پرواز {route_name}</b>\n\n"
        for p in prices[:3]: result_text += f"🔹 {p}\n"
        result_text += f"\n🌐 <a href='{route_url}'>مشاهده و خرید در سایت</a>"
        return result_text
    except Exception as e:
        print(f"Playwright error for {route_name}: {e}")
        await page.close()
        return None

async def fetch_random_flight_prices():
    selected_routes = random.sample(ALL_ROUTES, NUMBER_OF_ROUTES)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for route in selected_routes:
            price_text = await get_prices_for_route(browser, route["name"], route["url"])
            if price_text: send_to_all(price_text)
        await browser.close()

def send_news_only():
    news = fetch_news()
    if news:
        news_to_send = news[:MAX_NEWS_TO_SEND] 
        
        sent = load_sent()
        for title, link, image_url in news_to_send:
            summary = summarize_with_ai(title)
            category = get_category(title)
            text = f"🔹 <b>{summary}</b>\n\n🔗 <a href='{link}'>مشاهده خبر کامل</a>\n\n{category}"
            if send_to_all(text, image_url): sent.add(link)
        save_sent(sent)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"Start in mode: {mode} at {datetime.now()}")
    if mode == "news": send_news_only()
    elif mode == "prices": asyncio.run(fetch_random_flight_prices())
    else:
        send_news_only()
        asyncio.run(fetch_random_flight_prices())

if __name__ == "__main__":
    main()
