import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # تست روی اصفهان
        url = "https://www.eghamat24.com/EsfahanHotels.html"
        print(f"Opening {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)
        
        # پیدا کردن لینک‌های هتل
        links = await page.locator("a[href*='Hotel']").all()
        
        hotel_links = []
        for link in links:
            try:
                href = await link.get_attribute("href")
                if href and "/EsfahanHotels/" in href and href.endswith(".html"):
                    hotel_links.append(href)
            except: pass
            
        print(f"Found {len(hotel_links)} hotel links for Esfahan.")
        for href in hotel_links[:5]:
            print(f"- {href}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
