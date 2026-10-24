import asyncio
from playwright.async_api import async_playwright
import re
import random

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.eghamat24.com/search/property?destination_id=100&destination_name=Shiraz&check_in=2026-10-27&length_of_stay=1"
        print("Opening Shiraz Search Page...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(12000)
        
        # پیدا کردن لینک‌هایی که دقیقاً به هتل‌های شیراز اشاره می‌کنن (نه منو)
        links = await page.locator("a[href*='/ShirazHotels/']").all()
        
        results = []
        seen_names = set()
        
        for link in links:
            try:
                name = await link.inner_text()
                name = name.strip()
                
                # 🌟 فیلتر هوشمند: فقط اسم‌هایی که کلمه "هتل" دارن و کلمات منو توشون نیست
                if not name or name in seen_names: continue
                if "هتل" not in name: continue
                if any(word in name for word in ["های", "مشاهده", "انتخاب", "پیشنهاد", "تخفیف", "ثبت", "همه"]): continue
                
                seen_names.add(name)
                
                # پیدا کردن والد برای استخراج قیمت
                parent = link.locator("xpath=..").locator("xpath=..").locator("xpath=..")
                parent_text = await parent.inner_text()
                
                prices = re.findall(r'([\d,]+)\s*تومان', parent_text)
                if prices:
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    results.append({"name": name, "price": min_price})
            except: pass
            
        # حذف تکراری‌ها
        unique_hotels = {}
        for h in results:
            if h["name"] not in unique_hotels:
                unique_hotels[h["name"]] = h
        final_list = list(unique_hotels.values())
                
        print(f"Found {len(final_list)} hotels!")
        
        msg = "🏨 <b>قیمت لحظه‌ای هتل‌های شیراز</b>\n\n"
        for h in final_list[:10]:
            msg += f"🔹 {h['name']}: {h['price']:,} تومان\n"
            
        msg += "\n📞 <b>برای رزرو تلفنی با ما در تماس باشید:</b>\n☎️ 0915XXXXXXX\n\n✈️ <b>درنا سفر</b>"
        
        print("--- پیام نهایی ---")
        print(msg)
        print("------------------")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
