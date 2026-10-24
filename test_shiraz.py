import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening Shiraz Hotels...")
        await page.goto("https://www.eghamat24.com/ShirazHotels.html", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        
        # پیدا کردن کارت‌های هتل بر اساس کلاس‌های رایج
        cards = await page.locator("div[class*='hotel'], div[class*='Hotel'], article[class*='hotel'], article[class*='Hotel']").all()
        
        print(f"Found {len(cards)} hotel cards!")
        
        found_hotels = []
        for card in cards[:20]:
            try:
                text = await card.inner_text()
                if "تومان" in text and len(text) < 1000:
                    lines = text.split("\n")
                    name = lines[0].strip()
                    found_hotels.append(name)
            except: pass
            
        for name in found_hotels[:10]:
            print(f"- {name}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
