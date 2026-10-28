import os
import sys
import requests
import feedparser
import asyncio
import random
import urllib.parse
import re
import json
import time
import translators as ts
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

TG_TOKEN = os.environ.get("BOT_TOKEN")
TG_CHANNEL = os.environ.get("CHANNEL_ID")
EITA_TOKEN = os.environ.get("EITA_TOKEN")
EITA_CHANNEL = os.environ.get("EITA_CHANNEL_ID")

GIST_ID = os.environ.get("GIST_ID")
GIST_TOKEN = os.environ.get("GIST_TOKEN")

MAX_NEWS_TO_SEND = 9
NUMBER_OF_ROUTES = 3

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
    {"name": "مشهد به تبریز", "url": "https://dornatravel.ir/flight/MHD-TBZ"},
    {"name": "تهران به زاهدان", "url": "https://dornatravel.ir/flight/THR-ZAH"},
    {"name": "تهران به اهواز", "url": "https://dornatravel.ir/flight/THR-AWZ"},
    {"name": "شیراز به مشهد", "url": "https://dornatravel.ir/flight/SYZ-MHD"},
    {"name": "اصفهان به مشهد", "url": "https://dornatravel.ir/flight/IFN-MHD"},
    {"name": "تهران به استانبول", "url": "https://dornatravel.ir/flight/IKA-IST"},
    {"name": "مشهد به استانبول", "url": "https://dornatravel.ir/flight/MHD-IST"},
    {"name": "تهران به نجف", "url": "https://dornatravel.ir/flight/IKA-NJF"},
    {"name": "مشهد به نجف", "url": "https://dornatravel.ir/flight/MHD-NJF"},
    {"name": "تهران به مسقط", "url": "https://dornatravel.ir/flight/IKA-MCT"},
]

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
    "https://www.theguardian.com/uk/travel/rss",
    "http://rss.cnn.com/rss/cnn_travel.rss",
    "https://www.atlasobscura.com/feeds/latest",
    "https://www.aerotime.aero/feed",
]

CATEGORIES = {
    "#هواپیمایی": ["هواپیمایی", "هواپیما", "پرواز", "ایرلاین", "فرودگاه", "بلیط", "airline", "flight", "aviation", "airport"],
    "#گردشگری": ["گردشگری", "توریسم", "سفر", "توریست", "هتل", "tourist", "travel", "tourism", "hotel"],
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
    "سعی کن برنامه سفرت رو کمی انعطاف‌پذیر بذاری؛ گاهی بهترین خاطرات از یک مسیر برنامه‌ریزی نشده به دست میاد!",
]

# ---------- Gist ----------
def load_sent_from_gist(file_name):
    if not GIST_ID or not GIST_TOKEN:
        return set()
    try:
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.ok:
            files = r.json().get("files", {})
            content = files.get(file_name, {}).get("content", "").strip()
            if not content:
                return set()
            return set(content.splitlines())
    except Exception as e:
        print(f"Gist load warning: {e}")
    return set()


def save_sent_to_gist(file_name, links):
    if not GIST_ID or not GIST_TOKEN:
        return
    new_content = "\n".join(links)
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"files": {file_name: {"content": new_content}}}
    try:
        r = requests.patch(url, headers=headers, json=data, timeout=10)
        if not r.ok:
            print(f"Gist save error: {r.text}")
    except Exception as e:
        print(f"Gist save warning: {e}")


def delete_previous_messages(file_name):
    if not GIST_ID or not GIST_TOKEN:
        return
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
                    requests.post(
                        f"https://api.telegram.org/bot{TG_TOKEN}/deleteMessage",
                        data={"chat_id": TG_CHANNEL, "message_id": msg_id},
                        timeout=10,
                    )
                print(f"Deleted {len(msg_ids)} previous messages from {file_name}.")
    except Exception as e:
        print(f"Delete messages error: {e}")


def save_message_ids(file_name, msg_ids):
    if not GIST_ID or not GIST_TOKEN:
        return
    new_content = "\n".join(str(i) for i in msg_ids if i)
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    data = {"files": {file_name: {"content": new_content}}}
    try:
        requests.patch(url, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(f"Save msg IDs error: {e}")


# ---------- Send ----------
def get_category(title):
    title_lower = title.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw.lower() in title_lower for kw in keywords):
            return cat
    return "#اخبار"


def get_image_url(entry):
    if "media_content" in entry and len(entry.media_content) > 0:
        return entry.media_content[0]["url"]
    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0]["url"]
    if "enclosures" in entry:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href")
    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image/"):
                return link.get("href")
    return None


def send_to_telegram(text, image_url=None):
    if not TG_TOKEN or not TG_CHANNEL:
        return None
    if image_url:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
        payload = {"chat_id": TG_CHANNEL, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {"chat_id": TG_CHANNEL, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        r = requests.post(url, data=payload, timeout=20)
        if not r.ok:
            if image_url:
                return send_to_telegram(text, None)
            return None
        data = r.json()
        if data.get("ok"):
            return data["result"]["message_id"]
        return None
    except:
        return None


def send_to_eita(text, image_url=None):
    if not EITA_TOKEN or not EITA_CHANNEL:
        return False
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
    elif "🌍" in text_md or "🍽️" in text_md:
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
    except:
        return False


def send_to_all(text, image_url=None):
    tg_id = send_to_telegram(text, image_url)
    eita_ok = send_to_eita(text, None)
    return tg_id, eita_ok


# ---------- News ----------
def fetch_news(max_per_feed=2):
    sent = load_sent_from_gist("sent_links.txt")
    collected = []

    now = datetime.now()
    limit_date = now - timedelta(hours=24)

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

                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])

                if pub_date and pub_date < limit_date:
                    print(f"Skipping old news: {title[:30]}... (Date: {pub_date})")
                    continue

                full_text = ""
                if "content" in entry and len(entry.content) > 0:
                    full_text = entry.content[0].value
                elif "summary" in entry:
                    full_text = entry.summary
                elif "description" in entry:
                    full_text = entry.description

                full_text = re.sub(r"<[^>]+>", "", full_text)
                full_text = full_text.strip()

                if len(full_text) > 500:
                    full_text = full_text[:500] + "..."

                collected.append((title, link, get_image_url(entry), full_text))
                count += 1
        except Exception as e:
            print(f"Feed error: {e}")
    return collected


def send_news_only():
    news = fetch_news()
    if news:
        news_to_send = news[:MAX_NEWS_TO_SEND]
        sent = load_sent_from_gist("sent_links.txt")

        for title, link, image_url, full_text in news_to_send:
            is_english = False
            if full_text:
                english_chars = sum(1 for c in full_text if c.isascii() and c.isalpha())
                if english_chars > len(full_text) * 0.5:
                    is_english = True

            if is_english:
                print(f"Translating English news: {title[:30]}...")
                try:
                    translated_title = ts.translate_text(title, translator="bing", from_language="en", to_language="fa")
                    translated_text = (
                        ts.translate_text(full_text, translator="bing", from_language="en", to_language="fa")
                        if full_text
                        else ""
                    )
                    if translated_title:
                        title = translated_title
                    if translated_text:
                        full_text = translated_text
                    print("✅ Translation successful!")
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ Translation error: {e}")
                    try:
                        translated_title = ts.translate_text(title, translator="google", from_language="en", to_language="fa")
                        translated_text = (
                            ts.translate_text(full_text, translator="google", from_language="en", to_language="fa")
                            if full_text
                            else ""
                        )
                        if translated_title:
                            title = translated_title
                        if translated_text:
                            full_text = translated_text
                        print("✅ Google Translation successful!")
                    except:
                        print("❌ Both Bing and Google failed. Skipping.")
                        continue

            category = get_category(title)

            text = f"🔹 <b>{title}</b>\n\n"
            if full_text:
                text += f"{full_text}\n\n"
            text += f"🔗 <a href='{link}'>مشاهده خبر کامل در سایت</a>\n\n"
            text += f"{category}"

            tg_id, _ = send_to_all(text, image_url)
            if tg_id:
                sent.add(link)
                save_sent_to_gist("sent_links.txt", sent)


# ---------- Prices (Playwright) ----------
async def get_prices_for_route(browser, route_name, route_url):
    page = await browser.new_page()
    try:
        await page.goto(route_url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        cards = await page.locator(
            "div[class*='card'], div[class*='item'], div[class*='flight']"
        ).all()

        flights = []
        for card in cards:
            try:
                text = await card.inner_text()
                if "تومان" not in text or not re.search(r"\d{1,2}:\d{2}", text):
                    continue

                lines = [line.strip() for line in text.split("\n") if line.strip()]

                # پیدا کردن اسم ایرلاین (دقیق‌تر)
                airline = "نامشخص"
                known_airlines = [
                    "ایران ایر", "ماهان", "آسمان", "زاگرس", "قشم ایر", "کیش ایر",
                    "سپهران", "پارس", "کاسپین", "تابان", "آتا", "کارون",
                    "فلای کیش", "نسیم ایر", "معراج", "چابهار", "هما", "مهر",
                    "فلای پرشیا", "پویا ایر", "یاس ایر", "ساها",
                    "اردکان ایر", "فارس ایر", "آساجت", "جی اسکای", "جی‌اسکای"
                ]
                
                for line in lines:
                    if any(name in line for name in known_airlines):
                        airline = line
                        break
                
                # اگر با لیست معروف پیدا نشد، از ۳ خط اول کارت استفاده کن
                if airline == "نامشخص":
                    for line in lines[:3]:
                        # خط باید کوتاه باشه، شامل کلمات منو نباشه و شامل عدد نباشه
                        if (len(line) > 2 and len(line) < 30 and
                            not any(c.isdigit() for c in line) and  # ✅ خط نباید عدد داشته باشه
                            not any(word in line for word in [
                                "پشتیبانی", "ساعته", "بلیط", "اکونومی", "سیستمی", 
                                "بیزنس", "Economy", "Business", "ظرفیت", "نفر", 
                                "تومان", "ریال", "نرخ", "مشاهده", "خرید", 
                                "مرتب", "سازی", "تهران", "مشهد", "کیش", 
                                "شیراز", "اصفهان", "تبریز", "استانبول", 
                                "نجف", "دبی", "مسقط", "اهواز", "آبادان", 
                                "زاهدان", "رشت", "بندر", "چابهار", "درنا",
                                "اکونومی", "Boeing", "Airbus", "737", "320"
                            ])):
                            airline = line
                            break

                times = re.findall(r"\d{1,2}:\d{2}", text)
                departure_time = times[0] if len(times) > 0 else "?"

                price = "?"
                for i, line in enumerate(lines):
                    if line == "تومان" and i > 0:
                        price = lines[i - 1]
                        break
                    elif "تومان" in line:
                        price_match = re.search(r"([\d,]+)", line)
                        if price_match:
                            price = price_match.group(1)
                            break

                if price != "?" and price != "0":
                    flights.append(
                        {"airline": airline, "departure": departure_time, "price": price}
                    )
            except:
                pass

        await page.close()

        if not flights:
            return None

        unique_flights = []
        seen = set()
        for f in flights:
            key = f"{f['airline']}_{f['departure']}_{f['price']}"
            if key not in seen:
                seen.add(key)
                unique_flights.append(f)

        result_text = f"✈️ <b>قیمت‌های لحظه‌ای پرواز {route_name}</b>\n\n"
        for f in unique_flights[:3]:
            result_text += f"🔹 <b>{f['airline']}</b> | ساعت {f['departure']}\n"
            result_text += f"    💰 {f['price']} تومان\n\n"
        result_text += f"🌐 <a href='{route_url}'>مشاهده و خرید در سایت</a>"
        return result_text

    except Exception as e:
        print(f"Playwright error for {route_name}: {e}")
        await page.close()
        return None


async def fetch_random_flight_prices():
    delete_previous_messages("last_price_msgs.txt")
    selected_routes = random.sample(ALL_ROUTES, min(NUMBER_OF_ROUTES, len(ALL_ROUTES)))
    new_msg_ids = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for route in selected_routes:
            price_text = await get_prices_for_route(browser, route["name"], route["url"])
            if price_text:
                tg_id, _ = send_to_all(price_text)
                if tg_id:
                    new_msg_ids.append(tg_id)
        await browser.close()

    save_message_ids("last_price_msgs.txt", new_msg_ids)


# ---------- Extras ----------
def get_weather_and_currency():
    msg = "🌤 <b>گزارش روزانه سفر</b>\n\n"
    cities = {"تهران": "Tehran", "مشهد": "Mashhad", "کیش": "Kish", "استانبول": "Istanbul", "دبی": "Dubai"}
    msg += "<b>وضعیت هوا:</b>\n"
    for fa, en in cities.items():
        try:
            r = requests.get(f"https://wttr.in/{en}?format=%C+%t&m&lang=fa", timeout=10)
            if r.ok:
                msg += f"📍 {fa}: {r.text.strip()}\n"
        except:
            pass

    msg += "\n<b>نرخ لحظه‌ای ارز (تومان):</b>\n"
    try:
        r_rates = requests.get("https://nerkh.jahankhahan.shop/data/live.json", timeout=15)
        if r_rates.ok:
            rates = r_rates.json().get("rates", {})
            usd_toman = rates.get("dollar")
            eur_toman = rates.get("euro")
            aed_toman = rates.get("aed")
            try_toman = rates.get("try")
            if usd_toman:
                msg += f"💵 دلار: {usd_toman:,} تومان\n"
            if eur_toman:
                msg += f"💶 یورو: {eur_toman:,} تومان\n"
            if try_toman:
                msg += f"🇹🇷 لیر ترکیه: {try_toman:,} تومان\n"
            if aed_toman:
                msg += f"🇦🇪 درهم امارات: {aed_toman:,} تومان\n"
            if usd_toman:
                try:
                    r_global = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
                    if r_global.ok:
                        g_rates = r_global.json()["rates"]
                        iqd_rate = g_rates.get("IQD", 1)
                        sar_rate = g_rates.get("SAR", 1)
                        msg += f"🇮🇶 دینار عراق: {int(usd_toman / iqd_rate):,} تومان\n"
                        msg += f"🇸🇦 ریال عربستان: {int(usd_toman / sar_rate):,} تومان\n"
                except:
                    pass
    except:
        msg += "⚠️ خطا در دریافت نرخ ارز.\n"

    msg += f"\n💡 <b>نکته سفر امروز:</b>\n{random.choice(TRAVEL_TIPS)}"
    return msg


def send_extras():
    text = get_weather_and_currency()
    send_to_all(text)


# ---------- Destination ----------
def send_destination_of_day():
    print("Sending destination of the day...")
    sent_destinations = load_sent_from_gist("sent_destinations.txt")

    try:
        with open("destinations.json", "r", encoding="utf-8") as f:
            all_destinations = json.load(f)

        available_destinations = [d for d in all_destinations if d["name"] not in sent_destinations]

        if not available_destinations:
            print("All destinations sent! Resetting list...")
            available_destinations = all_destinations
            sent_destinations = set()

        dest = random.choice(available_destinations)
        wiki_link = f"https://fa.wikipedia.org/wiki/{urllib.parse.quote(dest['name'].replace(' ', '_'))}"

        text = f"🌍 <b>مقصد گردشگری امروز: {dest['name']}</b>\n\n"
        text += f"{dest['description']}\n\n"
        text += f"🔗 <a href='{wiki_link}'>مشاهده عکس‌ها و اطلاعات بیشتر در ویکی‌پدیا</a>\n\n"
        text += "📞 <b>برای رزرو تور و مشاوره سفر با ما در تماس باشید:</b>\n"
        text += "☎️ 05132292292\n"
        text += "📱 09153092528\n\n"
        text += "✈️ <b>درنا تراول</b>"

        tg_id, _ = send_to_all(text)
        if tg_id:
            sent_destinations.add(dest["name"])
            save_sent_to_gist("sent_destinations.txt", sent_destinations)
            print(f"Saved destination to Gist: {dest['name']}")
    except Exception as e:
        print(f"Error sending destination: {e}")


# ---------- Food ----------
def send_local_food():
    print("Sending local food of the day...")
    sent_foods = load_sent_from_gist("sent_foods.txt")

    try:
        with open("foods.json", "r", encoding="utf-8") as f:
            all_foods = json.load(f)

        available_foods = [f for f in all_foods if f["name"] not in sent_foods]

        if not available_foods:
            print("✅ All foods have been sent! Resetting list for a new cycle...")
            available_foods = all_foods
            sent_foods = set()

        food = random.choice(available_foods)

        text = f"🍽️ <b>غذای محلی امروز: {food['name']} ({food['city']})</b>\n\n"
        text += f"{food['description']}\n\n"
        text += "📞 <b>برای رزرو تور و مشاوره سفر با ما در تماس باشید:</b>\n"
        text += "☎️ 05132292292\n"
        text += "📱 09153092528\n\n"
        text += "✈️ <b>درنا تراول</b>"

        tg_id, _ = send_to_all(text, food["image"])
        if tg_id:
            sent_foods.add(food["name"])
            save_sent_to_gist("sent_foods.txt", sent_foods)
            print(f"✅ Saved food to Gist. Total sent: {len(sent_foods)}")
        else:
            print(f"❌ Failed to send food: {food['name']}")
    except Exception as e:
        print(f"Error sending food: {e}")


# ---------- Main ----------
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "news":
        send_news_only()
    elif mode == "prices":
        asyncio.run(fetch_random_flight_prices())
    elif mode == "extras":
        send_extras()
    elif mode == "destination":
        send_destination_of_day()
    elif mode == "food":
        send_local_food()
    else:
        send_news_only()
        asyncio.run(fetch_random_flight_prices())
        send_extras()
        send_destination_of_day()
        send_local_food()


if __name__ == "__main__":
    main()
