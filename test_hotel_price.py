import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening Mashhad Hotels list...")
        # باز کردن صفحه لیست هتل‌های مشهد
        await page.goto("https://www.eghamat24.com/MashhadHotels.html", timeout=60000, wait_until="domcontentloaded")
        
        # صبر برای لود شدن کامل لیست
        print("Waiting 10 seconds...")
        await page.wait_for_timeout(10000)
        
        # پیدا کردن تمام کارت‌های هتل (این کلاس رو باید از سایت چک کنیم، فعلا یه حدس رایجه)
        # ما دنبال لینک‌هایی می‌گردیم که به صفحه هتل اشاره می‌کنن
        hotels = await page.locator("a[href*='Hotels/']").all()
        
        results = []
        for hotel in hotels[:15]: # فقط ۱۵ هتل اول رو چک میکنیم
            try:
                # پیدا کردن اسم هتل از روی لینک
                name = await hotel.get_attribute("title")
                if not name: 
                    name = await hotel.inner_text()
                
                name = name.strip()
                if not name or len(name) < 3: continue
                
                # پیدا کردن قیمت نزدیک به این لینک (با رفتن به تگ والد)
                parent = hotel.locator("xpath=..").locator("xpath=..") # رفتن دو مرحله بالاتر
                price_text = await parent.inner_text()
                
                # استخراج قیمت‌های تومانی از متن
                import re
                prices = re.findall(r'([\d,]+)\s*تومان', price_text)
                if prices:
                    # تبدیل به عدد برای پیدا کردن ارزان‌ترین
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    results.append((name, min_price))
            except:
                continue
        
        # حذف تکراری‌ها
        unique_results = list(set(results))
        
        print(f"Found {len(unique_results)} hotels with prices!")
        for name, price in unique_results[:10]:
            print(f"- {name}: {price:,} تومان")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
