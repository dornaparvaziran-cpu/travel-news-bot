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
            
            search_btn = page.locator("button:has-text('جستجوی تور'), a:has-text('جستجوی تور')").first
            if await search_btn.count() > 0:
                await search_btn.click()
                print("دکمه جستجو کلیک شد. منتظر لود نتایج...")
                await page.wait_for_timeout(15000)
            
        except Exception as e:
            print(f"خطا: {e}")
            await browser.close()
            return
            
        cards = await page.locator("div:has-text('جزئیات تور')").all()
        print(f"تعداد کارت‌های پیدا شده: {len(cards)}")
        
        tours = []
        for card in cards:
            try:
                text = await card.inner_text()
                if "تومان" not in text:
                    continue
                    
                text = text.replace("location_on", "").replace("flight_takeoff", "").replace("flight_land", "").replace("directions_bus", "").replace("جزئیات تور", "")
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                price_match = re.search(r'([\d,۰-۹]+)\s*تومان', text)
                price = price_match.group(0) if price_match else "نامشخص"
                
                hotel = "نامشخص"
                destination = "نامشخص"
                
                # پیدا کردن اسم هتل (کمتر از ۸ کلمه)
                for line in lines:
                    word_count = len(line.split())
                    if (len(line) > 5 and 
                        word_count < 8 and 
                        "تومان" not in line and 
                        "شب" not in line and 
                        "," not in line and 
                        "آبان" not in line and 
                        "آذر" not in line and 
                        "دی" not in line and 
                        "پرفروش" not in line and 
                        "تورها" not in line):
                        hotel = line
                        break
                        
                # پیدا کردن مقصد (فقط خطی که کلمه "شب" دارد)
                for line in lines:
                    if "شب" in line:
                        destination = line
                        break
                
                if hotel != "نامشخص" and destination != "نامشخص":
                    tours.append({
                        "hotel": hotel,
                        "destination": destination,
                        "price": price
                    })
            except:
                pass
                
        unique_tours = []
        seen = set()
        for t in tours:
            key = f"{t['hotel']}_{t['price']}"
            if key not in seen:
                seen.add(key)
                unique_tours.append(t)
                
        print(f"✅ تعداد {len(unique_tours)} تور استخراج شد.")
        
        if unique_tours:
            random_tours = random.sample(unique_tours, min(3, len(unique_tours)))
            
            msg = "🎟️ <b>تورهای لحظه آخری پیشنهادی</b>\n\n"
            for t in random_tours:
                msg += f"🔹 <b>{t['hotel']}</b>\n"
                msg += f"📍 {t['destination']}\n"
                msg += f"💰 {t['price']}\n\n"
                
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
