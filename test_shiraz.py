import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://dornatravel.ir/flight/THR-MHD"
        print(f"Opening {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)
        
        print("\n--- Searching for flight info ---")
        
        # ۱. پیدا کردن اسم شرکت‌ها (معمولاً به صورت متن هستن)
        airlines = []
        for name in ["ایران ایر", "ماهان", "آسمان", "زاگرس", "قشم ایر", "کیش ایر", "سپهران", "پارس", "کاسپین", "تابان"]:
            if name in await page.content():
                airlines.append(name)
        print(f"Airlines found: {airlines}")
        
        # ۲. پیدا کردن ساعت پروازها (الگوی HH:MM)
        body_text = await page.locator("body").inner_text()
        times = re.findall(r'\d{1,2}:\d{2}', body_text)
        print(f"Times found (first 5): {times[:5]}")
        
        # ۳. پیدا کردن ساختار کلی یک کارت پرواز
        print("\n--- Looking for flight cards ---")
        cards = await page.locator("div[class*='card'], div[class*='item'], div[class*='flight']").all()
        print(f"Found {len(cards)} potential cards.")
        
        for card in cards[:3]:
            text = await card.inner_text()
            print(f"--- Card content ---\n{text[:200]}...\n")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())