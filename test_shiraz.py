import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # آدرس جستجوی هتل‌های شیراز برای یک شب
        url = "https://www.eghamat24.com/search/property?destination_id=100&destination_name=Shiraz&check_in=2026-10-27&length_of_stay=1"
        print(f"Opening Search Page...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        
        # صبر برای لود کامل نتایج
        print("Waiting 12 seconds...")
        await page.wait_for_timeout(12000)
        
        # گرفتن تمام متن صفحه
        body_text = await page.locator("body").inner_text()
        
        # پیدا کردن خطوطی که شامل قیمت (تومان) هستن
        import re
        # الگوی پیدا کردن اسم هتل و قیمت
        # معمولاً اسم هتل قبل از قیمت میاد
        lines = body_text.split("\n")
        results = []
        
        for i, line in enumerate(lines):
            if "تومان" in line:
                # ۳ خط بالاتر رو به عنوان اسم هتل چک میکنیم
                for j in range(1, 4):
                    if i - j >= 0:
                        potential_name = lines[i - j].strip()
                        if len(potential_name) > 5 and "هتل" in potential_name:
                            results.append(potential_name)
                            break
                            
        unique_results = list(set(results))
        print(f"Found {len(unique_results)} hotel names!")
        for name in unique_results[:10]:
            print(f"- {name}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
