import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    # لینک صفحه تورهای لحظه آخری سفرمارکت
    url = "https://safarmarket.com/tours/lastminute"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Opening page...")
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(15000)
        except Exception as e:
            print(f"Error: {e}")
            await browser.close()
            return
            
        text = await page.inner_text('body')
        print(f"Page loaded. Length: {len(text)}")
        
        # جستجوی کلمات کلیدی مرتبط با تور
        if "تور" in text and ("تومان" in text or "قیمت" in text):
            print("✅ Page seems accessible and contains tour data.")
            # چاپ چند خط اول برای بررسی
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            print("Sample lines:")
            for line in lines[:20]:
                print(line)
        else:
            print("❌ Page content does not look like a tour list. It might be blocked.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
