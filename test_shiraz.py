import asyncio
from playwright.async_api import async_playwright
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
            
            # کلیک روی دکمه جستجو
            search_btn = page.locator("button:has-text('جستجوی تور'), a:has-text('جستجوی تور')").first
            if await search_btn.count() > 0:
                await search_btn.click()
                print("دکمه جستجو کلیک شد. منتظر لود نتایج...")
                await page.wait_for_timeout(15000)
            
        except Exception as e:
            print(f"خطا: {e}")
            await browser.close()
            return
            
        text = await page.inner_text('body')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        tours = []
        
        # پیدا کردن الگوی تورها در لیست خطوط
        for i, line in enumerate(lines):
            # قیمت‌ها به این شکل هستند: "۶۵,۸۱۰,۰۰۰ تومان" یا "56,500,000 تومان"
            if "تومان" in line and i > 5:
                # قیمت در خط i است. اطلاعات بالا را بررسی می‌کنیم
                price = line
                hotel_name = lines[i - 5] if i >= 5 else "نامشخص"
                destination_nights = lines[i - 4] if i >= 4 else "نامشخص"
                agency = lines[i - 3] if i >= 3 else "نامشخص"
                
                # فیلتر کردن خطوطی که واقعاً شبیه اسم هتل هستند
                if len(hotel_name) > 3 and not hotel_name.startswith("flight"):
                    tours.append({
                        "hotel": hotel_name,
                        "destination": destination_nights,
                        "agency": agency,
                        "price": price
                    })
                    
        # حذف تکراری‌ها (بر اساس نام هتل و قیمت)
        unique_tours = []
        seen = set()
        for t in tours:
            key = f"{t['hotel']}_{t['price']}"
            if key not in seen and t["hotel"] != "نامشخص":
                seen.add(key)
                unique_tours.append(t)
                
        print(f"✅ تعداد {len(unique_tours)} تور استخراج شد.")
        
        if unique_tours:
            # انتخاب ۳ تور تصادفی برای نمایش
            random_tours = random.sample(unique_tours, min(3, len(unique_tours)))
            
            msg = "🎟️ <b>تورهای لحظه آخری پیشنهادی</b>\n\n"
            for t in random_tours:
                msg += f"🔹 <b>{t['hotel']}</b>\n"
                msg += f"📍 {t['destination']}\n"
                msg += f"✈️ {t['agency']}\n"
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
            print("❌ هیچ توری با الگوی مورد نظر پیدا نشد.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
