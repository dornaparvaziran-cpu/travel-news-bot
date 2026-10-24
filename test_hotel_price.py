import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.eghamat24.com/search/property?destination_id=100&destination_name=Shiraz&check_in=2026-10-27&length_of_stay=1"
        print("Opening Shiraz Search Page...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(12000)
        
        # پیدا کردن تمام لینک‌های هتل در شیراز
        links = await page.locator("a[href*='/ShirazHotels/']").all()
        
        results = []
        seen_names = set()
        
        for link in links:
            try:
                # 🌟 استخراج اسم هتل از ویژگی title
                name = await link.get_attribute("title")
                if not name:
                    continue
                
                name = name.strip()
                if name in seen_names: continue
                seen_names.add(name)
                
                # پیدا کردن قیمت از والد
                parent = link.locator("xpath=..").locator("xpath=..").locator("xpath=..")
                parent_text = await parent.inner_text()
                
                prices = re.findall(r'([\d,]+)\s*تومان', parent_text)
                if prices:
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    results.append({"name": name, "price": min_price})
            except: pass
            
        print(f"Found {len(results)} hotels with prices!")
        
        msg = "🏨 <b>قیمت لحظه‌ای هتل‌های شیراز</b>\n\n"
        for h in results[:10]:
            msg += f"🔹 {h['name']}: {h['price']:,} تومان\n"
            
        msg += "\n📞 <b>برای رزرو تلفنی با ما در تماس باشید:</b>\n☎️ 0915XXXXXXX\n\n✈️ <b>درنا سفر</b>"
        
        print("--- پیام نهایی ---")
        print(msg)
        print("------------------")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
