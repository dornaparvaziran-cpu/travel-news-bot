import asyncio
from playwright.async_api import async_playwright
import re
import random

async def main():
    url = "https://safarmarket.com/tours/lastminute"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("در حال باز کردن صفحه سفرمارکت...")
        
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # پیدا کردن لینک‌های تب‌های مقصد (لینک‌هایی که به تورهای یک شهر خاص می‌روند)
            # این لینک‌ها معمولاً شامل کلمه tours و نام شهر هستند
            links = await page.locator("a[href*='/tours/']").all()
            
            unique_destinations = []
            seen_names = set()
            
            for link in links:
                try:
                    text = await link.inner_text()
                    text = text.strip()
                    # فیلتر کردن لینک‌هایی که متن کوتاه و شبیه نام شهر هستند
                    if text and 2 < len(text) < 20 and text not in seen_names and "تور" not in text:
                        href = await link.get_attribute("href")
                        if href:
                            seen_names.add(text)
                            unique_destinations.append({"element": link, "name": text, "href": href})
                except:
                    pass
            
            print(f"تعداد مقاصد پیدا شده: {len(unique_destinations)}")
            
            if not unique_destinations:
                print("مقصدی پیدا نشد.")
                await browser.close()
                return
            
            # انتخاب ۵ مقصد تصادفی
            random_destinations = random.sample(unique_destinations, min(5, len(unique_destinations)))
            
            final_tours = []
            
            for dest_info in random_destinations:
                dest_name = dest_info["name"]
                dest_href = dest_info["href"]
                print(f"در حال بررسی مقصد: {dest_name}")
                
                try:
                    # به جای کلیک، مستقیماً به لینک آن مقصد می‌رویم
                    full_url = f"https://safarmarket.com{dest_href}" if dest_href.startswith("/") else dest_href
                    await page.goto(full_url, timeout=60000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(8000) # صبر برای لود تورها
                    
                    cards = await page.locator("div:has-text('جزئیات تور')").all()
                    
                    dest_tours = []
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
                                dest_tours.append({
                                    "hotel": hotel,
                                    "destination": destination,
                                    "price_str": price_str,
                                    "price_num": price_num
                                })
                        except:
                            pass
                            
                    if dest_tours:
                        cheapest = min(dest_tours, key=lambda x: x["price_num"])
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
            
        print(f"\n✅ در مجموع {len(final_tours)} تور از ۵ مقصد استخراج شد.")
        
        if final_tours:
            msg = "🎟️ <b>ارزان‌ترین تورهای لحظه آخری (از ۵ مقصد)</b>\n\n"
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
