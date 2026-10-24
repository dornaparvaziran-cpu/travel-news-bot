import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # رفتن به یک هتل تستی در تبریز
        url = "https://www.eghamat24.com/TabrizHotels/ParsElgoliHotel.html"
        print(f"Opening {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        # گرفتن کل متن صفحه
        body_text = await page.locator("body").inner_text()
        
        # پیدا کردن کلمات مربوط به ستاره
        print("--- Searching for stars in page text ---")
        lines = body_text.split("\n")
        for line in lines:
            if "ستاره" in line or "star" in line.lower():
                print(f"Found: {line.strip()[:100]}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
