import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # فقط برای تست، صفحه هتل‌های مشهد رو باز می‌کنیم
        url = "https://www.eghamat24.com/MashhadHotels.html"
        print(f"Opening {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        
        # پیدا کردن همه لینک‌های صفحه
        links = await page.locator("a").all()
        
        # چاپ ۲۰ لینک اولی که حاوی کلمه Hotel هستن
        count = 0
        for link in links:
            try:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                if href and "Hotel" in href:
                    print(f"- Text: {text.strip()[:30]} | Href: {href}")
                    count += 1
                    if count >= 20: break
            except: pass
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
