import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # یک هتل تستی در تبریز
        url = "https://www.eghamat24.com/TabrizHotels/ParsElgoliHotel.html"
        print(f"Opening {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        # روش ۱: خواندن کل متن صفحه
        body_text = await page.locator("body").inner_text()
        prices = re.findall(r'([\d,]+)\s*تومان', body_text)
        print(f"All prices found in text: {prices[:10]}")
        
        # روش ۲: پیدا کردن تگ‌هایی که کلاس price دارن
        price_elements = await page.locator("[class*='price'], [class*='Price']").all()
        print(f"Elements with 'price' class: {len(price_elements)}")
        for el in price_elements[:5]:
            text = await el.inner_text()
            print(f"- {text.strip()[:50]}")
            
        # روش ۳: پیدا کردن دکمه‌های رزرو یا انتخاب اتاق
        buttons = await page.locator("button, a").all()
        for btn in buttons:
            text = await btn.inner_text()
            if "اتاق" in text or "رزرو" in text or "قیمت" in text:
                print(f"Button/Link: {text.strip()[:50]}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
