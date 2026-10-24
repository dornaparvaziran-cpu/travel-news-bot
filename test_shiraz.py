import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # باز کردن صفحه هتل‌های شیراز
        print("Opening Shiraz Hotels...")
        await page.goto("https://www.eghamat24.com/ShirazHotels.html", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        
        # پیدا کردن تمام لینک‌هایی که کلمه Hotel توشون هست
        links = await page.locator("a").all()
        hotel_links = []
        for link in links:
            try:
                href = await link.get_attribute("href")
                if href and "Hotel" in href:
                    text = await link.inner_text()
                    if text.strip():
                        hotel_links.append((text.strip(), href))
            except: pass
            
        print(f"Found {len(hotel_links)} hotel links!")
        for name, href in hotel_links[:5]:
            print(f"- {name}: {href}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
