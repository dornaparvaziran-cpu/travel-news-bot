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
        
        # پیدا کردن کارت‌های پرواز
        cards = await page.locator("div[class*='card'], div[class*='item'], div[class*='flight']").all()
        
        print(f"Found {len(cards)} cards.")
        
        for i, card in enumerate(cards):
            try:
                text = await card.inner_text()
                # چک میکنیم که آیا این کارت واقعاً یک پرواز هست (شامل قیمت و ساعت)
                if "تومان" in text and re.search(r'\d{1,2}:\d{2}', text):
                    print(f"\n--- FLIGHT CARD {i} ---")
                    # چاپ دقیق خطوط برای دیدن ساختار
                    lines = text.split('\n')
                    for line in lines:
                        print(line.strip())
            except: pass
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())