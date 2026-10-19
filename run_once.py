import os
import requests
import feedparser
import asyncio
import random  # برای انتخاب تصادفی مسیرها
from datetime import datetime
from playwright.async_api import async_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
METIS_KEY = os.getenv("METIS_KEY")

# ---------- لیست بزرگ مسیرهای پرفروش ----------
# کدهای فرودگاه: THR=تهران، MHD=مشهد، KIH=کیش، SYZ=شیراز، IFN=اصفهان، TBZ=تبریز، AWZ=اهواز
# IST=استانبول، DXB=دبی، IKA=تهران(امام)، THR=تهران(مهرآباد)
ALL_ROUTES = [
    # --- داخلی ---
    {"name": "تهران به مشهد", "url": "https://dornatravel.ir/flight/THR-MHD"},
    {"name": "مشهد به تهران", "url": "https://dornatravel.ir/flight/MHD-THR"},
    {"name": "تهران به کیش", "url": "https://dornatravel.ir/flight/THR-KIH"},
    {"name": "کیش به تهران", "url": "https://dornatravel.ir/flight/KIH-THR"},
    {"name": "مشهد به کیش", "url": "https://dornatravel.ir/flight/MHD-KIH"},
    {"name": "تهران به شیراز", "url": "https://dornatravel.ir/flight/THR-SYZ"},
    {"name": "تهران به اصفهان", "url": "https://dornatravel.ir/flight/THR-IFN"},
    {"name": "تهران به تبریز", "url": "https://dornatravel.ir/flight/THR-TBZ"},
    {"name": "تهران به اهواز", "url": "https://dornatravel.ir/flight/THR-AWZ"},
    {"name": "شیراز به مشهد", "url": "https://dornatravel.ir/flight/SYZ-MHD"},
    {"name": "اصفهان به مشهد", "url": "https://dornatravel.ir/flight/IFN-MHD"},
    
    # --- خارجی (اگر سایتت این کدها را پشتیبانی می‌کند) ---
    {"name": "تهران به استانبول", "url": "https://dornatravel.ir/flight/IKA-IST"},
    {"name": "تهران به دبی", "url": "https://dornatravel.ir/flight/IKA-DXB"},
    {"name": "مشهد به استانبول", "url": "https://dornatravel.ir/flight/MHD-IST"},
    {"name": "شیراز به دبی", "url": "https://dornatravel.ir/flight/SYZ-DXB"},
    {"name": "تهران به نجف", "url": "https://dornatravel.ir/flight/IKA-NJF"},
    {"name": "تهران به مسقط", "url": "https://dornatravel.ir/flight/IKA-MCT"},
]

# ---------- تنظیمات تعداد مسیر رندوم ----------
# هر بار که ربات اجرا می‌شود، چند مسیر به صورت تصادفی انتخاب شود؟
NUMBER_OF_ROUTES = 3 

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

CATEGORIES = {
    "#هواپیمایی": ["هواپیمایی", "هواپیما", "پرواز", "ایرلاین", "فرودگاه", "بلیط", "airline", "flight", "aviation", "airport"],
    "#گردشگری": ["گردشگری", "توریسم", "سفر", "توریست", "هتل", "tourist", "travel", "tourism", "hotel"]
}
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

def get_category(title):
    title_lower = title.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw.lower() in title_lower for kw in keywords):
            return cat
    return "#اخبار"

def get_image_url(entry):
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0]['url']
    if 'enclosures' in entry:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                return link.get('href')
    return None

def send_telegram_post(text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {"chat_id": CHANNEL_ID, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        r = requests.post(url, data=payload, timeout=20)
        if not r.ok:
            if image_url:
                return send_telegram_post(text, None)
            return False
        return True
    except:
        return False

def summarize_with_ai(title):
    if not METIS_KEY:
        return title
    url = "https://api.metisai.ir/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {METIS_KEY}", "Content-Type": "application/json"}
    prompt = f"این تیتر خبر در حوزه گردشگری یا هواپیمایی است: '{title}'\nیک خلاصه بسیار کوتاه و جذاب (حداکثر ۲ خط) به زبان فارسی برای کانال تلگرام بنویس. لحن آن خبری و حرفه‌ای باشد. فقط متن خلاصه را برگردان."
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
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
            print(f"Feed error: {e}")
    return collected

# ---------- استخراج قیمت از سایت ----------
async def get_prices_for_route(browser, route_name, route_url):
    page = await browser.new_page()
    try:
        print(f"Opening {route_url}...")
        await page.goto(route_url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)
        
        all_elements = await page.locator("body *").all()
        prices = []
        for el in all_elements:
            try:
                text = await el.inner_text()
                if "تومان" in text and len(text) < 30 and any(char.isdigit() for char in text):
                    if text not in prices:
                        prices.append(text)
            except:
                pass
        
        await page.close()
        
        if not prices:
            return None
            
        result_text = f"✈️ <b>قیمت‌های لحظه‌ای پرواز {route_name}</b>\n\n"
        for i, p in enumerate(prices[:3]):
            result_text += f"🔹 {p}\n"
        
        result_text += f"\n🌐 <a href='{route_url}'>مشاهده و خرید در سایت</a>"
        return result_text
        
    except Exception as e:
        print(f"Playwright error for {route_name}: {e}")
        await page.close()
        return None

async def fetch_random_flight_prices():
    # 🎲 انتخاب تعداد مشخصی مسیر به صورت کاملاً تصادفی از لیست بزرگ
    selected_routes = random.sample(ALL_ROUTES, NUMBER_OF_ROUTES)
    print(f"Selected random routes: {[r['name'] for r in selected_routes]}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for route in selected_routes:
            price_text = await get_prices_for_route(browser, route["name"], route["url"])
            if price_text:
                send_telegram_post(price_text)
                print(f"Sent prices for: {route['name']}")
            else:
                print(f"Could not fetch prices for: {route['name']}")
        
        await browser.close()

def main():
    print(f"Start: {datetime.now()}")
    
    # ۱. ارسال اخبار
    news = fetch_news()
    if news:
    #    send_telegram_post("📰 <b>اخبار گردشگری و هواپیمایی</b>\n")
        sent = load_sent()
        for title, link, image_url in news:
            summary = summarize_with_ai(title)
            category = get_category(title)
            text = f"🔹 <b>{summary}</b>\n\n🔗 <a href='{link}'>مشاهده خبر کامل</a>\n\n{category}"
            if send_telegram_post(text, image_url):
                sent.add(link)
                print(f"Sent: {title[:50]}")
        save_sent(sent)
        
    # ۲. ارسال قیمت‌های چند مسیر رندوم
    print("Fetching flight prices for random routes...")
    asyncio.run(fetch_random_flight_prices())

if __name__ == "__main__":
    main()
