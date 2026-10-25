import os
import sys
import requests
import feedparser
import asyncio
import random
import urllib.parse
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright

TG_TOKEN = os.environ.get("BOT_TOKEN")
TG_CHANNEL = os.environ.get("CHANNEL_ID")
EITA_TOKEN = os.environ.get("EITA_TOKEN")
EITA_CHANNEL = os.environ.get("EITA_CHANNEL_ID")
METIS_KEY = os.environ.get("METIS_KEY")

GIST_ID = os.environ.get("GIST_ID")
GIST_TOKEN = os.environ.get("GIST_TOKEN")

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
MAX_NEWS_TO_SEND = 9 

FEEDS = [
    "https://www.tinn.ir/fa/feeds/?p=Y2F0ZWdvcmllcz03Ng,,",
    "https://www.tinn.ir/fa/feeds/?p=cG9zaXRpb25Gcm9udD00",
    "https://biatrip.com/tag/اخبار-خطوط-هوایی/feed",
    "https://biatrip.com/tag/سازمان-هواپیمایی-فدرال/feed",
    "https://www.mehrnews.com/rss",
    "https://www.mehrnews.com/rss?kw=شرکت+فرودگاهها+و+ناوبری+هوایی+ایران",
    "https://www.khabaronline.ir/rss?kw=CIP+فرودگاه",
    "https://www.irna.ir/rss",
    "https://skift.com/feed/",
]

CATEGORIES = {
    "#هواپیمایی": ["هواپیمایی", "هواپیما", "پرواز", "ایرلاین", "فرودگاه", "بلیط", "airline", "flight", "aviation", "airport"],
    "#گردشگری": ["گردشگری", "توریسم", "سفر", "توریست", "هتل", "tourist", "travel", "tourism", "hotel"]
}
ALL_KEYWORDS = [kw for cat in CATEGORIES.values() for kw in cat]

TRAVEL_TIPS = [
    "لباس‌هات رو به جای تا کردن، رول کن تا فضای کمتری توی چمدان بگیرن و چروک هم نشن.",
    "کفش‌های کثیف رو حتماً داخل کیسه پلاستیکی یا کاور مخصوص کفش بذار تا لباس‌های دیگه آلوده نشن.",
    "یک کیف پارچه‌ای تاشو و سبک توی چمدانت بذار تا برای سوغاتی و خریدهای اضافه ازش استفاده کنی.",
    "وسایل ضروری مثل مسواک و شامپو رو در سایز کوچک (سفر) تهیه کن تا هم سبک‌تر باشی هم توی فرودگاه دردسر نداشته باشی.",
    "همیشه یک دست لباس راحت و گرم (مثل سویشرت) توی دستت (کابین) نگه دار، چون دمای هواپیما ممکنه سرد باشه.",
    "برای جلوگیری از گم شدن چمدان، یک برچسب با اسم و شماره تماست روش بچسبون و از عکس گرفتن چمدان قبل از تحویل دادن غافل نشو.",
    "برای پیدا کردن بلیط ارزان‌تر، پروازهای اواسط هفته (سه‌شنبه و چهارشنبه) رو چک کن.",
    "قبل از نهایی کردن خرید بلیط، پنجره مرورگرت رو در حالت ناشناس (Incognito) باز کن تا سایت‌ها قیمت رو به خاطر جستجوی مکرر بالا نبرن.",
    "هنگام رزرو هتل، نظرات (کامنت‌های) واقعی کاربران قبلی رو با دقت بخون، مخصوصاً عکس‌هایی که خودشون آپلود کردن.",
    "اگر برنامه سفرت قطعی نیست، هتلی رو رزرو کن که گزینه «لغو رایگان» (Free Cancellation) داشته باشه.",
    "برای پیدا کردن تورهای ارزان، همیشه بخش «تورهای لحظه آخر» (Last Minute) آژانس‌ها رو چک کن.",
    "گاهی خرید بلیط یک‌طرفه از دو ایرلاین مختلف، ارزان‌تر از خرید بلیط رفت و برگشت از یک ایرلاین درمیاد.",
    "همیشه کمی پول نقد (ارز محلی) همراهت داشته باش، چون بعضی تاکسی‌ها یا مغازه‌های محلی دستگاه کارت نمی‌پذیرن.",
    "برای صرفه‌جویی در هزینه، به جای هتل‌های مرکز شهر، اقامتگاه‌های کمی دورتر از مرکز رو انتخاب کن که به مترو یا ایستگاه اتوبوس نزدیک باشن.",
    "قبل از سفر، از نرخ لحظه‌ای ارز مقصدت مطلع بشی تا در صرافی‌ها گول قیمت‌های بالا رو نخوری.",
    "در بازارهای محلی و سنتی چانه بزن، اما در مراکز خرید بزرگ و برندها چانه زدن معنی نداره.",
    "یک کیف پول کوچک و مخفی (کمری یا آستینی) برای نگهداری پول و کارت‌های اصلیت تهیه کن.",
    "همیشه یک کپی دیجیتال از پاسپورت، ویزا، بلیط و بیمه‌نامه‌ت رو توی ایمیل یا گالری گوشیت ذخیره کن.",
    "عکس صفحه اول پاسپورتت رو در گوشی ذخیره کن تا اگر گم شد، راحت‌تر بتونی به سفارتخانه مراجعه کنی.",
    "کیف یا کوله‌پشتی‌ت رو همیشه جلوی بدنت نگه دار (Crossbody)، مخصوصاً توی شهرهای شلوغ و توریستی.",
    "شماره‌های اضطراری (پلیس، اورژانس) و آدرس سفارت ایران در کشور مقصد رو از قبل توی گوشیت ذخیره کن.",
    "هرگز پاسپورتت رو به عنوان ضمانت به هتل‌ها یا آژانس‌های کرایه ماشین نده؛ فقط ازش کپی بگیرن کافیه.",
    "توی پروازهای طولانی، هر چند ساعت یک بار از جات بلند شو و کمی راه برو تا گردش خونت بهتر بشه.",
    "توی هواپیما به خاطر هوای خشک، آب بیشتری بنوش و از نوشیدنی‌های کافئین‌دار (قهوه، نوشابه) کمتر استفاده کن.",
    "یک بسته دستمال کاغذی جیبی و ضدعفونی‌کننده دست همیشه توی کوله‌ت باشه.",
    "کرم ضد آفتاب رو حتی در روزهای ابری و فصل زمستان هم فراموش نکن.",
    "داروهای مصرفی شخصی (مثل مسکن، داروی معده یا سرماخوردگی) رو توی بسته‌بندی اصلی‌شون و به مقدار کافی همراهت داشته باش.",
    "اگر به مقصدی با ارتفاع بالا (مثل کوهستان) سفر می‌کنی، روز اول رو به استراحت و سازگاری با ارتفاع اختصاص بده.",
    "یک پاوربانک کوچک و سبک همیشه همراهت باشه، چون توی گشت‌های طولانی باتری گوشی تموم میشه.",
    "قبل از سفر، نقشه شهر مقصد رو در اپلیکیشن Google Maps دانلود (آفلاین) کن تا بدون اینترنت هم مسیرت رو پیدا کنی.",
    "یک مبدل برق (آداپتور) مخصوص کشور مقصد بخر تا بتونی گوشی و وسایلت رو شارژ کنی.",
    "اگر به کشوری می‌ری که اینترنت گرونه، قبل از سفر یک eSIM بخر یا بعد از ورود از فرودگاه یک سیم‌کارت محلی بگیر.",
    "تمام عکس‌ها و ویدیوهای سفرت رو به صورت خودکار در فضای ابری (مثل Google Photos) بکاپ بگیر تا فضای گوشیت پر نشه.",
    "قبل از سفر به کشورهای خارجی، با آداب و رسوم و قوانین مهم اونجا (مخصوصاً پوشش و رفتار در مکان‌های مذهبی) آشنا بشو.",
    "یاد گرفتن ۲ یا ۳ کلمه ساده از زبان محلی (مثل سلام، تشکر و ببخشید) باعث میشه برخورد مردم با تو خیلی صمیمی‌تر بشه.",
    "قبل از عکاسی از مردم محلی (مخصوصاً در روستاها یا بازارها)، حتماً از خودشون اجازه بگیر.",
    "به عنوان یک توریست، سعی کن از رستوران‌ها و مغازه‌های محلی خرید کنی تا هم اقتصاد اونجا رو حمایت کنی، هم تجربه بهتری داشته باشی.",
    "سعی کن برنامه سفرت رو کمی انعطاف‌پذیر بذاری؛ گاهی بهترین خاطرات از یک مسیر برنامه‌ریزی نشده به دست میاد!"
]

# ---------- توابع Gist ----------
def load_sent_from_gist():
    if not GIST_ID or not GIST_TOKEN: return set()
    try:
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.ok:
            files = r.json().get("files", {})
            content = files.get("sent_links.txt", {}).get("content", "").strip()
            if not content: return set()
            return set(content.splitlines())
    except Exception as e:
        print(f"Gist load warning: {e}")
    return set()

def save_sent_to_gist(new_link):
    if not GIST_ID or not GIST_TOKEN: return
    sent = load_sent_from_gist()
    sent.add(new_link)
    new_content = "\n".join(sent)
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"files": {"sent_links.txt": {"content": new_content}}}
    try:
        r = requests.patch(url, headers=headers, json=data, timeout=10)
        if not r.ok: print(f"Gist save error: {r.text}")
    except Exception as e: print(f"Gist save warning: {e}")

# ---------- توابع پاک کردن پیام‌های قیمت ----------
def delete_previous_messages(file_name):
    if not GIST_ID or not GIST_TOKEN: return
    try:
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.ok:
            files = r.json().get("files", {})
            content = files.get(file_name, {}).get("content", "").strip()
            if content:
                msg_ids = content.splitlines()
                for msg_id in msg_ids:
                    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/deleteMessage", 
                                  data={"chat_id": TG_CHANNEL, "message_id": msg_id}, timeout=10)
                print(f"Deleted {len(msg_ids)} previous messages from {file_name}.")
    except Exception as e: print(f"Delete messages error: {e}")

def save_message_ids(file_name, msg_ids):
    if not GIST_ID or not GIST_TOKEN: return
    new_content = "\n".join(str(i) for i in msg_ids if i)
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    data = {"files": {file_name: {"content": new_content}}}
    try:
        requests.patch(url, headers=headers, json=data, timeout=10)
    except Exception as e: print(f"Save msg IDs error: {e}")

# ---------- توابع ارسال ----------
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

def send_to_telegram(text, image_url=None):
    if not TG_TOKEN or not TG_CHANNEL: return None
    if image_url:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
        payload = {"chat_id": TG_CHANNEL, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHANNEL, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        r = requests.post(url, data=payload, timeout=20)
        if not r.ok:
            if image_url: return send_to_telegram(text, None)
            return None
        data = r.json()
        if data.get("ok"): return data["result"]["message_id"]
        return None
    except: return None

def send_to_eita(text, image_url=None):
    if not EITA_TOKEN or not EITA_CHANNEL: return False
    text_md = text.replace("<b>", "*").replace("</b>", "*")
    def clean_link(match):
        url = match.group(1)
        try:
            decoded_url = urllib.parse.unquote(url)
            return f"{match.group(2)}:\n{decoded_url}"
        except:
            return f"{match.group(2)}:\n{url}"
    text_md = re.sub(r"<a href='([^']+)'>([^<]+)</a>", clean_link, text_md)
    
    if "قیمت‌های لحظه‌ای پرواز" in text_md:
        text_md = text_md.replace("🔹", "✈️")
        text_md = f"{text_md}\n\n➖➖➖➖➖➖➖➖"
    elif "🌍" in text_md:
        text_md = f"{text_md}\n\n➖➖➖➖➖➖➖➖"
    elif "🌤" in text_md or "💱" in text_md or "💡" in text_md:
        text_md = f"{text_md}\n\n➖➖➖➖➖➖➖➖"
    else:
        text_md = text_md.replace("🔹", "📰")
        text_md = f"{text_md}\n\n➖➖➖➖➖➖➖➖\n📢 کانال اخبار درنا تراول"
    
    base_url = f"https://eitaayar.ir/api/{EITA_TOKEN}"
    url = f"{base_url}/sendMessage"
    payload = {"chat_id": EITA_CHANNEL, "text": text_md, "parse_mode": "Markdown", "disable_web_page_preview": False}
    try:
        r = requests.post(url, data=payload, timeout=20)
        if not r.ok:
            print("Eitaa error:", r.text)
            return False
        return True
    except: return False

def send_to_all(text, image_url=None):
    tg_id = send_to_telegram(text, image_url)
    eita_ok = send_to_eita(text, None) 
    return tg_id, eita_ok

def summarize_with_ai(title):
    if not METIS_KEY: return title
    url = "https://api.metisai.ir/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {METIS_KEY}", "Content-Type": "application/json"}
    prompt = f"این تیتر خبر در حوزه گردشگری یا هواپیمایی است: '{title}'\nیک خلاصه بسیار کوتاه و جذاب (حداکثر ۲ خط) به زبان فارسی برای کانال تلگرام بنویس. لحن آن خبری و حرفه‌ای باشد. فقط متن خلاصه را برگردان."
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        if r.ok: 
            summary = r.json()['choices'][0]['message']['content'].strip()
            english_chars = sum(1 for c in summary if c.isascii() and c.isalpha())
            if english_chars > len(summary) * 0.5: return None
            return summary
        return None
    except: return None

def fetch_news(max_per_feed=2):
    sent = load_sent_from_gist()
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
                text = text.replace("ء", "").strip()
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
        await page.close()
        return None

async def fetch_random_flight_prices():
    delete_previous_messages("last_price_msgs.txt")
    
    selected_routes = random.sample(ALL_ROUTES, NUMBER_OF_ROUTES)
    new_msg_ids = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for route in selected_routes:
            price_text = await get_prices_for_route(browser, route["name"], route["url"])
            if price_text: 
                tg_id, _ = send_to_all(price_text)
                if tg_id: new_msg_ids.append(tg_id)
        await browser.close()
    
    save_message_ids("last_price_msgs.txt", new_msg_ids)

def send_news_only():
    news = fetch_news()
    if news:
        news_to_send = news[:MAX_NEWS_TO_SEND] 
        for title, link, image_url in news_to_send:
            summary = summarize_with_ai(title)
            if not summary: continue
            category = get_category(title)
            text = f"🔹 <b>{summary}</b>\n\n🔗 <a href='{link}'>مشاهده خبر کامل</a>\n\n{category}"
            tg_id, _ = send_to_all(text, image_url)
            if tg_id: save_sent_to_gist(link)

def get_weather_and_currency():
    msg = "🌤 <b>گزارش روزانه سفر</b>\n\n"
    cities = {"تهران": "Tehran", "مشهد": "Mashhad", "کیش": "Kish", "استانبول": "Istanbul", "دبی": "Dubai"}
    msg += "<b>وضعیت هوا:</b>\n"
    for fa, en in cities.items():
        try:
            r = requests.get(f"https://wttr.in/{en}?format=%C+%t&m&lang=fa", timeout=10)
            if r.ok: msg += f"📍 {fa}: {r.text.strip()}\n"
        except: pass
    msg += "\n<b>نرخ لحظه‌ای ارز (تومان):</b>\n"
    try:
        r_rates = requests.get("https://nerkh.jahankhahan.shop/data/live.json", timeout=15)
        if r_rates.ok:
            rates = r_rates.json().get("rates", {})
            usd_toman = rates.get("dollar")
            eur_toman = rates.get("euro")
            aed_toman = rates.get("aed")
            try_toman = rates.get("try")
            if usd_toman: msg += f"💵 دلار: {usd_toman:,} تومان\n"
            if eur_toman: msg += f"💶 یورو: {eur_toman:,} تومان\n"
            if try_toman: msg += f"🇹🇷 لیر ترکیه: {try_toman:,} تومان\n"
            if aed_toman: msg += f"🇦🇪 درهم امارات: {aed_toman:,} تومان\n"
            if usd_toman:
                try:
                    r_global = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
                    if r_global.ok:
                        g_rates = r_global.json()['rates']
                        iqd_rate = g_rates.get('IQD', 1)
                        sar_rate = g_rates.get('SAR', 1)
                        msg += f"🇮🇶 دینار عراق: {int(usd_toman / iqd_rate):,} تومان\n"
                        msg += f"🇸🇦 ریال عربستان: {int(usd_toman / sar_rate):,} تومان\n"
                except: pass
    except: msg += "⚠️ خطا در دریافت نرخ ارز.\n"
    msg += f"\n💡 <b>نکته سفر امروز:</b>\n{random.choice(TRAVEL_TIPS)}"
    return msg

def send_extras():
    text = get_weather_and_currency()
    send_to_all(text)

def send_destination_of_day():
    print("Sending destination of the day...")
    try:
        with open("destinations.json", "r", encoding="utf-8") as f:
            destinations = json.load(f)
            
        dest = random.choice(destinations)
        
        text = f"🌍 <b>مقصد گردشگری امروز: {dest['name']}</b>\n\n"
        text += f"{dest['description']}\n\n"
        text += "📞 <b>برای رزرو تور و مشاوره سفر با ما در تماس باشید:</b>\n"
        text += "☎️ 05132292292\n"
        text += "📱 09153092528\n\n"
        text += "✈️ <b>درنا تراول</b>"
        
        send_to_all(text, dest["image"])
        
    except Exception as e:
        print(f"Error sending destination: {e}")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "news": send_news_only()
    elif mode == "prices": asyncio.run(fetch_random_flight_prices())
    elif mode == "extras": send_extras()
    elif mode == "destination": send_destination_of_day()
    else:
        send_news_only()
        asyncio.run(fetch_random_flight_prices())
        send_extras()
        send_destination_of_day()

if __name__ == "__main__":
    main()
