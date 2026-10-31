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

from content import FOODS, TRAVEL_TIPS, YOUTUBE_QUERIES, ALL_ROUTES, FEEDS

TG_TOKEN = os.environ.get("BOT_TOKEN")
TG_CHANNEL = os.environ.get("CHANNEL_ID")
EITA_TOKEN = os.environ.get("EITA_TOKEN")
EITA_CHANNEL = os.environ.get("EITA_CHANNEL_ID")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

GIST_ID = os.environ.get("GIST_ID")
GIST_TOKEN = os.environ.get("GIST_TOKEN")

MAX_NEWS_TO_SEND = 9
NUMBER_OF_ROUTES = 3

CATEGORIES = {
    "#هواپیمایی": ["هواپیمایی", "هواپیما", "پرواز", "ایرلاین", "فرودگاه", "بلیط", "airline", "flight", "aviation", "airport"],
    "#گردشگری": ["گردشگری", "توریسم", "سفر", "توریست", "هتل", "tourist", "travel", "tourism", "hotel"],
}
ALL_KEYWORDS = [kw for cat in CATEGORIES.values() for kw in cat]

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
    elif "🌍" in text_md or "🍽️" in text_md or "🏨" in text_md:
        text_md = f"{text_md}\n\n➖➖➖➖➖➖➖➖"
    elif "🎬" in text_md:
        # پیام یوتیوب: بدون خط جداکننده
        pass
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

                airline = "نامشخص"
                known_airlines = [
                    "ایران ایر", "ماهان", "آسمان", "زاگرس", "قشم ایر", "کیش ایر",
                    "سپهران", "پارس", "کاسپین", "تابان", "آتا", "کارون",
                    "فلای کیش", "نسیم ایر", "معراج", "چابهار", "هما", "مهر",
                    "فلای پرشیا", "پویا ایر", "یاس ایر", "ساها",
                    "اردکان ایر", "فارس ایر", "آساجت", "جی اسکای", "جی‌اسکای",
                    "کیش ایر", "فلای پرشیا", "ایران‌ایر", "ماهان‌ایر"
                ]

                for line in lines:
                    if any(name in line for name in known_airlines):
                        airline = line
                        break

                if airline == "نامشخص":
                    for line in lines[:3]:
                        if (2 < len(line) < 25 and
                            not any(c.isdigit() for c in line) and
                            "درنا" not in line and
                            not any(word in line for word in [
                                "پشتیبانی", "ساعته", "بلیط", "اکونومی", "سیستمی",
                                "بیزنس", "Economy", "Business", "ظرفیت", "نفر",
                                "تومان", "ریال", "نرخ", "مشاهده", "خرید",
                                "مرتب", "سازی", "تهران", "مشهد", "کیش",
                                "شیراز", "اصفهان", "تبریز", "استانبول",
                                "نجف", "دبی", "مسقط", "اهواز", "آبادان",
                                "زاهدان", "رشت", "بندر", "چابهار",
                                "Boeing", "Airbus", "EMB", "737", "320", "145"
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

                if airline != "نامشخص" and price != "?" and price != "0" and departure_time != "?":
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

        final_flights = []
        seen_airline_time = set()
        for f in unique_flights:
            key = f"{f['airline']}_{f['departure']}"
            if key not in seen_airline_time:
                seen_airline_time.add(key)
                final_flights.append(f)

        result_text = f"✈️ <b>قیمت‌های لحظه‌ای پرواز {route_name}</b>\n\n"
        for f in final_flights[:3]:
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

    except FileNotFoundError:
        print("destinations.json not found! Skipping destination job.")
    except Exception as e:
        print(f"Destination error: {e}")


# ---------- Food ----------
def send_food_of_day():
    print("Sending food of the day...")
    sent_foods = load_sent_from_gist("sent_foods.txt")

    available_foods = [f for f in FOODS if f["name"] not in sent_foods]
    if not available_foods:
        print("All foods sent! Resetting list...")
        available_foods = FOODS
        sent_foods = set()

    food = random.choice(available_foods)

    text = f"🍽️ <b>غذای پیشنهادی امروز: {food['name']}</b>\n\n"
    text += f"{food['description']}\n\n"
    text += "✈️ <b>درنا تراول</b> — همراه سفرهای شما"

    tg_id, _ = send_to_all(text)
    if tg_id:
        sent_foods.add(food["name"])
        save_sent_to_gist("sent_foods.txt", sent_foods)


# ---------- YouTube ----------
def send_youtube_video():
    print("Fetching YouTube video...")
    if not YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not set! Skipping.")
        return

    sent_videos = load_sent_from_gist("sent_youtube.txt")
    query = random.choice(YOUTUBE_QUERIES)

    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 25,
            "order": "relevance",
            "videoEmbeddable": "true",
            "key": YOUTUBE_API_KEY,
        }
        r = requests.get(url, params=params, timeout=15)
        if not r.ok:
            print(f"YouTube API error: {r.text}")
            return

        items = r.json().get("items", [])
        candidates = []
        
        # فیلتر کلمات ممنوعه و مجاز
        blacklist = ["politics", "war", "news", "media", "propaganda", "military", "israel", "palestine", "usa", "america"]
        whitelist = ["travel", "iran", "tour", "tourism", "guide", "vlog", "visit", "nature", "city"]

        for item in items:
            vid = item.get("id", {}).get("videoId")
            if not vid or vid in sent_videos:
                continue
                
            title_raw = item["snippet"]["title"].lower()
            desc_raw = item["snippet"].get("description", "").lower()
            
            if any(bad_word in title_raw or bad_word in desc_raw for bad_word in blacklist):
                print(f"Skipping blacklisted video: {title_raw[:30]}...")
                continue
                
            if not any(good_word in title_raw or good_word in desc_raw for good_word in whitelist):
                print(f"Skipping unrelated video: {title_raw[:30]}...")
                continue

            candidates.append(item)

        if not candidates:
            print("No suitable videos found. Resetting list...")
            sent_videos = set()
            candidates = [it for it in items if it.get("id", {}).get("videoId")]
            if not candidates:
                print("YouTube returned no results.")
                return

        video = random.choice(candidates)
        vid = video["id"]["videoId"]
        raw_title = video["snippet"]["title"]

        # حذف هشتگ‌ها
        title = re.sub(r"#\S+", "", raw_title).strip()
        if not title:
            title = raw_title

        # ترجمه عنوان
        english_chars = sum(1 for c in title if c.isascii() and c.isalpha())
        if english_chars > len(title) * 0.5:
            print("Translating YouTube title to Persian...")
            try:
                title = ts.translate_text(title, translator="bing", from_language="en", to_language="fa")
            except Exception as e:
                print(f"Translation error: {e}")
                try:
                    title = ts.translate_text(title, translator="google", from_language="en", to_language="fa")
                except:
                    pass

        video_url = f"https://www.youtube.com/watch?v={vid}"

        text = f"🎬 <b>{title}</b>\n\n"
        text += f"🔗 تماشا در یوتیوب:\n{video_url}\n\n"
        text += "✈️ <b>درنا تراول</b>"

        tg_id, _ = send_to_all(text)
        if tg_id:
            sent_videos.add(vid)
            save_sent_to_gist("sent_youtube.txt", sent_videos)

    except Exception as e:
        print(f"YouTube error: {e}")


# ---------- Hotels ----------
async def get_hotels_data(browser):
    url = "https://www.iranhotelonline.com/mashhad-hotels/"
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(15000) 
        
        text = await page.inner_text('body')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        hotels = []
        current_hotel = None
        
        for line in lines:
            if line.startswith("هتل ") and len(line) < 50:
                current_hotel = line
            elif re.match(r'^\d{1,3}(,\d{3})+$', line) and current_hotel:
                price_val = int(line.replace(",", ""))
                if price_val > 1000000:
                    hotels.append({"name": current_hotel, "price": price_val})
                    current_hotel = None
                    
        unique_hotels = {}
        for h in hotels:
            if h["name"] not in unique_hotels:
                unique_hotels[h["name"]] = h
            else:
                if h["price"] < unique_hotels[h["name"]]["price"]:
                    unique_hotels[h["name"]]["price"] = h["price"]
                    
        final_hotels = list(unique_hotels.values())
        
        if not final_hotels:
            return None
            
        # انتخاب ۵ هتل به صورت تصادفی
        random_hotels = random.sample(final_hotels, min(5, len(final_hotels)))
        
        result_text = "🏨 <b>پیشنهاد ویژه اقامت در مشهد</b>\n\n"
        for h in random_hotels:
            result_text += f"🔹 {h['name']}: {h['price']:,} تومان\n"
            
        result_text += "\n📞 <b>برای رزرو تلفنی با ما در تماس باشید:</b>\n"
        result_text += "☎️ 05132292292\n"
        result_text += "📱 09153092528\n\n"
        result_text += "✈️ <b>درنا تراول</b>"
        
        return result_text

    except Exception as e:
        print(f"Hotel Playwright error: {e}")
        return None
    finally:
        await page.close()


async def send_hotel_prices():
    print("Fetching hotel prices...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        hotel_text = await get_hotels_data(browser)
        if hotel_text:
            send_to_all(hotel_text)
            print("Hotel prices sent successfully.")
        else:
            print("No hotels found or error occurred.")
        await browser.close()


# ---------- Main ----------
if __name__ == "__main__":
    job = sys.argv[1] if len(sys.argv) > 1 else "news"
    print(f"Running job: {job}")
    if job == "news":
        send_news_only()
    elif job == "prices":
        asyncio.run(fetch_random_flight_prices())
    elif job == "extras":
        send_extras()
    elif job == "destination":
        send_destination_of_day()
    elif job == "food":
        send_food_of_day()
    elif job == "youtube":
        send_youtube_video()
    elif job == "hotels":
        asyncio.run(send_hotel_prices())
    else:
        print(f"Unknown job: {job}")
