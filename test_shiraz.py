import asyncio
from playwright.async_api import async_playwright
import random
import re

async def main():
    url = "https://safarmarket.com/tours/lastminute"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("در حال باز کردن صفحه سفرمارکت...")
        
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # پیدا کردن لینک‌های تب‌های مقصد (با استفاده از کلاس frequentCitiesItem)
            # این همان تگ‌هایی هستند که در عکس شما دیده می‌شدند
            links = await page.locator("a.frequentCitiesItem, div.frequentCitiesItem a, .frequentCitiesItem").all()
            
            destinations = []
            seen_names = set()
            
            for link in links:
                try:
                    # دریافت آدرس لینک
                    href = await link.get_attribute("href")
                    title = await link.get_attribute("data-title") or await link.inner_text()
                    title = title.strip() if title else ""
                    
                    # اگر آدرس یا نام وجود داشت، به لیست اضافه کن
                    if href and title and title not in seen_names and "تور" not in title:
                        seen_names.add(title)
                        destinations.append({"name": title, "href": href})
                except:
                    pass
            
            print(f"تعداد مقاصد پیدا شده: {len(destinations)}")
            for d in destinations:
                print(f" - {d['name']} (آدرس: {d['href']})")
            
            if not destinations:
                print("مقصدی پیدا نشد. لطفا بررسی کنید.")
                await browser.close()
                return
                
            # انتخاب ۵ مقصد تصادفی
            random_destinations = random.sample(destinations, min(5, len(destinations)))
            
            final_tours = []
            
            for dest in random_destinations:
                dest_name = dest["name"]
                dest_href = dest["href"]
                print(f"\nدر حال بررسی تورهای {dest_name}...")
                
                try:
                    # رفتن مستقیم به آدرس آن مقصد
                    full_url = f"https://safarmarket.com{dest_href}" if dest_href.startswith("/") else dest_href
                    await page.goto(full_url, timeout=60000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(8000) # صبر برای لود تورها
                    
                    cards = await page.locator("div:has-text('جزئیات تور')").all()
                    
                    city_tours = []
                    for card in cards:
                        try:
                            text = await card.inner_text()
                            if "تومان" not in text:
                                continue
                                
                            text = text.replace("location_on", "").replace("flight_takeoff", "").replace("flight_land", "").replace("directions_bus", "").replace("جزئیات تور", "")
                            lines = [line.strip() for line in text.split('\n') if line.strip()]
                            
                            price_match = re.search(r'([\d,۰-۹]+)\s*تومان', text)
                            if not price_match:
                                continue
                            
                            price_str = price_match.group(0)
                            price_num_str = price_match.group(1).replace(",", "").replace("۰", "0").replace("۱", "1").replace("۲", "2").replace("۳", "3").replace("۴", "4").replace("۵", "5").replace("۶", "6").replace("۷", "7").replace("۸", "8").replace("۹", "9")
                            price_num = int(price_num_str)
                            
                            hotel = "نامشخص"
                            destination = "نامشخص"
                            
                            for line in lines:
                                word_count = len(line.split())
                                if (len(line) > 5 and word_count < 8 and "تومان" not in line and "شب" not in line and "," not in line and "آبان" not in line and "آذر" not in line and "دی" not in line and "پرفروش" not in line and "تورها" not in line):
                                    hotel = line
                                    break
                                    
                            for line in lines:
                                if "شب" in line:
                                    destination = line
                                    break
                            
                            if hotel != "نامشخص" and destination != "نامشخص":
                                city_tours.append({
                                    "hotel": hotel,
                                    "destination": destination,
                                    "price_str": price_str,
                                    "price_num": price_num
                                })
                        except:
                            pass
                            
                    if city_tours:
                        cheapest = min(city_tours, key=lambda x: x["price_num"])
                        final_tours.append(cheapest)
                        print(f"  ✅ ارزان‌ترین در {dest_name}: {cheapest['hotel']} - {cheapest['price_str']}")
                    else:
                        print(f"  ❌ توری در {dest_name} پیدا نشد.")
                        
                except Exception as e:
                    print(f"  خطا در بررسی {dest_name}: {e}")
                    
        except Exception as e:
            print(f"خطای کلی: {e}")
            await browser.close()
            return
            
        print(f"\n✅ در مجموع {len(final_tours)} تور از مقاصد مختلف استخراج شد.")
        
        if final_tours:
            msg = "🎟️ <b>ارزان‌ترین تورهای لحظه آخری (مقاصد مختلف)</b>\n\n"
            for t in final_tours:
                msg += f"🔹 <b>{t['destination']}</b>\n"
                msg += f"🏨 {t['hotel']}\n"
                msg += f"💰 {t['price_str']}\n\n"
                
            msg += "📞 <b>برای رزرو با ما در تماس باشید:</b>\n"
            msg += "☎️ 05132292292\n"
            msg += "📱 09153092528\n\n"
            msg += "✈️ <b>درنا تراول</b>"
            
            print("\n" + "="*40)
            print("پیش‌نمایش پیام:")
            print("="*40)
            print(msg)
            print("="*40)
        else:
            print("❌ هیچ توری پیدا نشد.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
