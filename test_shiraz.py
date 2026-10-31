import asyncio
from playwright.async_api import async_playwright
import re

async def test_hotels():
    # لینک جستجوی هتل‌های مشهد
    url = "https://www.iranhotelonline.com/mashhad-hotels/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("در حال باز کردن صفحه هتل‌های مشهد...")
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            # صبر برای لود شدن کامل قیمت‌ها
            await page.wait_for_timeout(15000) 
        except Exception as e:
            print(f"خطا در باز کردن صفحه: {e}")
            await browser.close()
            return
            
        text = await page.inner_text('body')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        hotels = []
        current_hotel = None
        
        for line in lines:
            # تشخیص اسم هتل
            if line.startswith("هتل ") and len(line) < 50:
                current_hotel = line
            
            # تشخیص قیمت (اعداد با کاما که حداقل ۷ رقم دارند -> بالای ۱ میلیون تومان)
            elif re.match(r'^\d{1,3}(,\d{3})+$', line) and current_hotel:
                price_val = int(line.replace(",", ""))
                if price_val > 1000000: # فیلتر کردن قیمت‌های پایین (مثل تخفیف یا بیعانه)
                    hotels.append({
                        "name": current_hotel,
                        "price": price_val
                    })
                    current_hotel = None # ریست کردن برای پیدا کردن هتل بعدی
                    
        # حذف تکراری‌ها (اگر یک هتل چند بار در صفحه بود، فقط یکی را نگه دار)
        unique_hotels = {}
        for h in hotels:
            if h["name"] not in unique_hotels:
                unique_hotels[h["name"]] = h
            else:
                # اگر هتل تکراری بود، ارزان‌ترین قیمت را نگه دار
                if h["price"] < unique_hotels[h["name"]]["price"]:
                    unique_hotels[h["name"]]["price"] = h["price"]
                    
        final_hotels = list(unique_hotels.values())
        final_hotels.sort(key=lambda x: x["price"])
        
        # ساخت متن پیام نهایی (دقیقاً مثل چیزی که به کانال می‌رود)
        msg = "🏨 <b>قیمت لحظه‌ای هتل‌های مشهد</b>\n\n"
        if final_hotels:
            for h in final_hotels[:5]:
                msg += f"🔹 {h['name']}: {h['price']:,} تومان\n"
        else:
            msg += "⚠️ هیچ هتلی پیدا نشد.\n"
            
        msg += f"\n🌐 <a href='{url}'>مشاهده و رزرو در سایت</a>"
        
        # چاپ در لاگ‌ها
        print("\n" + "="*40)
        print("پیش‌نمایش پیام تلگرام/ایتا:")
        print("="*40)
        print(msg)
        print("="*40)
        
        # ذخیره در یک فایل برای بررسی دقیق‌تر
        with open("hotel_test_output.txt", "w", encoding="utf-8") as f:
            f.write(msg)
            
        print(f"\n✅ تعداد کل هتل‌های استخراج شده: {len(final_hotels)}")
        print("خروجی در فایل hotel_test_output.txt ذخیره شد.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_hotels())
