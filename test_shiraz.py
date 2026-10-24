import asyncio
from playwright.async_api import async_playwright
import re
import urllib.parse

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # لیست شهرها
        cities = ["مشهد", "تهران", "کیش", "قشم", "شیراز", "اصفهان", "یزد", "تبریز", "قم"]
        
        for city in cities:
            print(f"\n--- Searching for {city} ---")
            try:
                # جستجو در سایت برای پیدا کردن لینک شهر
                await page.goto(f"https://www.eghamat24.com/search?q={city}", timeout=30000)
                await page.wait_for_timeout(3000)
                
                # پیدا کردن لینک‌های مربوط به هتل‌های این شهر
                links = await page.locator("a").all()
                found_id = None
                
                for link in links:
                    href = await link.get_attribute("href")
                    if href and "destination_name" in href and city in urllib.parse.unquote(href):
                        # استخراج آیدی از لینک
                        id_match = re.search(r'destination_id=(\d+)', href)
                        if id_match:
                            found_id = id_match.group(1)
                            break
                            
                if found_id:
                    print(f"Found ID for {city}: {found_id}")
                else:
                    print(f"ID not found for {city}")
                    
            except Exception as e:
                print(f"Error for {city}: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
