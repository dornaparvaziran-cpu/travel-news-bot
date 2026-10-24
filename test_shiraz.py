import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.eghamat24.com/MashhadHotels.html"
        print("Opening Mashhad Hotels...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(12000)
        
        # پیدا کردن لینک‌های هتل‌ها
        links = await page.locator("a[href*='/MashhadHotels/']").all()
        
        hotel_urls = []
        seen_names = set()
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or not href.endswith(".html"): continue
                
                hotel_id = href.split("/")[-1].replace(".html", "")
                if hotel_id in ["MashhadHotels", "CheapHotels"]: continue
                
                name = re.sub(r'(?<!^)(?=[A-Z])', ' ', hotel_id).replace("_", " ").strip()
                if name in seen_names: continue
                seen_names.add(name)
                
                hotel_urls.append({"name": name, "url": f"https://www.eghamat24.com{href}"})
                if len(hotel_urls) >= 5: break # فقط ۵ هتل اول برای تست
            except: pass
            
        print(f"Testing {len(hotel_urls)} hotels...")
        
        # رفتن به صفحه هر هتل و خواندن قیمت
        for hotel in hotel_urls:
            try:
                print(f"\nChecking {hotel['name']}...")
                await page.goto(hotel["url"], timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000) # صبر برای لود قیمت‌ها
                
                # خواندن متن کل صفحه
                body_text = await page.locator("body").inner_text()
                
                # پیدا کردن قیمت‌ها
                prices = re.findall(r'([\d,]+)\s*تومان', body_text)
                if prices:
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    print(f"-> Min price: {min_price:,} تومان")
                else:
                    print("-> No price found.")
                    
            except Exception as e:
                print(f"-> Error: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
