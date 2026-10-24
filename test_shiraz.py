import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.eghamat24.com/search/property?destination_id=100&destination_name=Shiraz&check_in=2026-10-27&length_of_stay=1"
        print("Opening Shiraz Search Page...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(12000)
        
        # پیدا کردن تمام لینک‌های صفحه
        links = await page.locator("a").all()
        
        hotel_links = []
        for link in links:
            try:
                href = await link.get_attribute("href")
                # اگر لینک شامل کلمه hotel بود
                if href and "hotel" in href.lower():
                    text = await link.inner_text()
                    if text.strip():
                        hotel_links.append((text.strip(), href))
            except: pass
            
        # حذف تکراری‌ها
        unique_links = list(set(hotel_links))
        
        print(f"Found {len(unique_links)} hotel links!")
        for name, href in unique_links[:10]:
            print(f"- {name}: {href}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
