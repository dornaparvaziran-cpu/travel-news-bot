import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening Eghamat24...")
        # باز کردن صفحه هتل امپراطور
        await page.goto("https://www.eghamat24.com/MashhadHotels/ImperatorHotel.html", timeout=60000, wait_until="domcontentloaded")
        
        # صبر برای لود شدن کامل
        print("Waiting 8 seconds...")
        await page.wait_for_timeout(8000)
        
        # پیدا کردن هر متنی که کلمه "تومان" داره
        all_elements = await page.locator("body *").all()
        prices_found = []
        for el in all_elements:
            try:
                text = await el.inner_text()
                if "تومان" in text and len(text) < 50:
                    if text not in prices_found:
                        prices_found.append(text)
            except: pass
            
        print(f"Found {len(prices_found)} prices!")
        for p_text in prices_found[:10]:
            print("-", p_text)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
