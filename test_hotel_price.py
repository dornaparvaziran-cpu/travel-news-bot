import asyncio
import requests
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening Mashhad Hotels list...")
        await page.goto("https://www.eghamat24.com/MashhadHotels.html", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        
        hotels = await page.locator("a[href*='Hotels/']").all()
        
        results = []
        for hotel in hotels[:15]: 
            try:
                name = await hotel.get_attribute("title")
                if not name: name = await hotel.inner_text()
                name = name.strip()
                if not name or len(name) < 3: continue
                
                parent = hotel.locator("xpath=..").locator("xpath=..")
                price_text = await parent.inner_text()
                
                prices = re.findall(r'([\d,]+)\s*تومان', price_text)
                if prices:
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    results.append((name, min_price))
            except: continue
        
        # حذف تکراری‌ها
        unique_results = list(set(results))[:8] # حداکثر ۸ هتل
        print(f"Found {len(unique_results)} hotels.")

        # ساخت صفحه HTML برای عکس
        html_content = """
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.0.3/Vazirmatn-font-face.css');
                body {
                    font-family: 'Vazirmatn', sans-serif;
                    background-color: #f0f4f8;
                    margin: 0;
                    padding: 20px;
                    width: 600px;
                    direction: rtl;
                }
                .header {
                    background-color: #1e3a8a;
                    color: white;
                    text-align: center;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    font-size: 28px;
                    font-weight: bold;
                }
                .list {
                    background: white;
                    padding: 10px 20px;
                    border-radius: 0 0 10px 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                .item {
                    display: flex;
                    justify-content: space-between;
                    padding: 15px 0;
                    border-bottom: 1px solid #e2e8f0;
                    font-size: 22px;
                }
                .item:last-child { border-bottom: none; }
                .name { color: #1e293b; font-weight: bold; }
                .price { color: #16a34a; font-weight: bold; }
                .footer {
                    background-color: #1e3a8a;
                    color: white;
                    text-align: center;
                    padding: 15px;
                    border-radius: 10px;
                    margin-top: 20px;
                    font-size: 20px;
                }
                .footer span { color: #fbbf24; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">قیمت لحظه‌ای هتل‌های مشهد</div>
            <div class="list">
        """
        
        for name, price in unique_results:
            html_content += f'<div class="item"><span class="name">{name}</span><span class="price">{price:,} تومان</span></div>'
            
        html_content += """
            </div>
            <div class="footer">برای رزرو تلفنی با ما در تماس باشید: <span>0915XXXXXXX</span><br><br>✈️ درنا سفر</div>
        </body>
        </html>
        """

        # ذخیره HTML در یک فایل موقت
        with open("temp.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        # باز کردن فایل HTML و گرفتن عکس
        print("Taking screenshot...")
        page2 = await browser.new_page(viewport={"width": 650, "height": 200}) # ارتفاع اولیه، بعدا تنظیم میشه
        await page2.goto("file://" + requests.utils.quote("/".join([asyncio.get_event_loop()._run_once.__globals__['__file__'].rsplit('/',1)[0], "temp.html"])), timeout=30000)
        
        # صبر برای لود فونت
        await page2.wait_for_timeout(3000)
        
        # گرفتن اسکرین‌شات از کل صفحه
        await page2.screenshot(path="hotels_list.jpg", full_page=True)
        
        print("Image saved as hotels_list.jpg!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
