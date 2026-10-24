import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # آدرس جستجوی هتل‌های شیراز
        url = "https://www.eghamat24.com/search/property?destination_id=100&destination_name=Shiraz&check_in=2026-10-27&length_of_stay=1"
        print(f"Opening Shiraz Search Page...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        
        # صبر برای لود کامل
        print("Waiting 12 seconds...")
        await page.wait_for_timeout(12000)
        
        # گرفتن کل متن صفحه
        body_text = await page.locator("body").inner_text()
        lines = body_text.split("\n")
        
        results = []
        for i, line in enumerate(lines):
            # اگر خط شامل قیمت بود
            if "تومان" in line:
                # ۳ خط بالاتر رو نگاه کن، اگر اسم هتل بود
                for j in range(1, 4):
                    if i - j >= 0:
                        name = lines[i - j].strip()
                        if len(name) > 5 and "هتل" in name and "های" not in name:
                            results.append(name)
                            break

        unique_hotels = list(set(results))
        print(f"Found {len(unique_hotels)} hotels!")
        for name in unique_hotels[:10]:
            print(f"- {name}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
