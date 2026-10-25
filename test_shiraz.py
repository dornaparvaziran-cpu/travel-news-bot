import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # تست روی صفحه اصلی FIDS
        url = "https://fids.airport.ir"
        print(f"Opening {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000) # صبر برای لود کامل
        
        # گرفتن کل متن صفحه برای دیدن ساختار
        body_text = await page.locator("body").inner_text()
        
        print("--- First 2000 characters of page text ---")
        print(body_text[:2000])
        
        # پیدا کردن لینک‌های فرودگاه‌ها
        links = await page.locator("a").all()
        airport_links = []
        for link in links:
            try:
                text = await link.inner_text()
                href = await link.get_attribute("href")
                if text.strip() and ("فرودگاه" in text or "مهرآباد" in text or "مشهد" in text):
                    airport_links.append((text.strip(), href))
            except: pass
            
        print(f"\nFound {len(airport_links)} airport links:")
        for name, href in airport_links[:10]:
            print(f"- {name}: {href}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
