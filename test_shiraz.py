import asyncio
from playwright.async_api import async_playwright
import random
import re

async def main():
    url = "https://safarmarket.com/tours"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("در حال باز کردن صفحه جستجوی تور...")
        
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # کلیک روی دکمه جستجو برای لود تورها
            search_btn = page.locator("button:has-text('جستجوی تور'), a:has-text('جستجوی تور')").first
            if await search_btn.count() > 0:
                await search_btn.click()
                print("دکمه جستجو کلیک شد. منتظر لود نتایج...")
                await page.wait_for_timeout(15000)
            
            # اسکرول کردن صفحه برای لود شدن تورهای بیشتر
            print("در حال اسکرول کردن صفحه برای لود تورهای بیشتر...")
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
            
            cards = await page.locator("div:has-text('جزئیات تور')").all()
            print(f"تعداد کارت‌های پیدا شده: {len(cards)}")
            
            tours = []
            seen_destinations = set()
            
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
                        tours.append({
                            "hotel": hotel,
                            "destination": destination,
                            "price_str": price_str,
                            "price_num": price_num
                        })
                except:
                    pass
            
            # فیلتر کردن برای اینکه از هر مقصد فقط یک تور (ارزان‌ترین) داشته باشیم
            unique_dest_tours = {}
            for t in tours:
                dest = t['destination']
                if dest not in unique_dest_tours:
                    unique_dest_tours[dest] = t
                else:
                    # اگر تور ارزان‌تری برای این مقصد پیدا شد، جایگزین کن
                    if t['price_num'] < unique_dest_tours[dest]['price_num']:
                        unique_dest_tours[dest] = t
                        
            final_tours = list(unique_dest_tours.values())
            
            # انتخاب ۵ تور تصادفی از مقاصد مختلف
            if len(final_tours) > 5:
                final_tours = random.sample(final_tours, 5)
                
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
                
        except Exception as e:
            print(f"خطای کلی: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
