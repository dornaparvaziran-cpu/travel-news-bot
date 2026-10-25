import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # لینک مستقیم فرودگاه مشهد
        url = "https://fids.airport.ir/102/%D8%A7%D8%B7%D9%84%D8%A7%D8%B9%D8%A7%D8%AA-%D9%BE%D8%B1%D9%88%D8%A7%D8%B2-%D9%81%D8%B1%D9%88%D8%AF%DA%AF%D8%A7%D9%87-%D9%85%D8%B4%D9%87%D8%AF"
        print(f"Opening Mashhad Airport...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000) # صبر برای لود کامل
        
        # گرفتن کل متن صفحه
        body_text = await page.locator("body").inner_text()
        
        print("--- Page text (first 2000 chars) ---")
        print(body_text[:2000])
        
        # پیدا کردن پروازها (معمولاً با شماره پرواز یا کلمه پرواز مشخص میشن)
        print("\n--- Searching for flights ---")
        lines = body_text.split("\n")
        for i, line in enumerate(lines):
            if any(kw in line for kw in ["پرواز", "مقصد", "خروجی", "ورودی", "IR", "W5", "ساعت"]):
                print(f"Line {i}: {line.strip()[:100]}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
