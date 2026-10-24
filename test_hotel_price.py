import asyncio
from playwright.async_api import async_playwright
import re
import random

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # آدرس جستجوی شیراز
        url = "https://www.eghamat24.com/search/property?destination_id=100&destination_name=Shiraz&check_in=2026-10-27&length_of_stay=1"
        print("Opening Shiraz Search Page...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(12000)
        
        # پیدا کردن لینک‌هایی که دقیقاً به صفحه هتل اشاره می‌کنن
        links = await page.locator("a[href*='/ShirazHotels/']").all()
        
        results = []
        seen_names = set()
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                name = await link.inner_text()
                name = name.strip()
                
                # 🌟 فیلتر کردن لینک‌های منو و دکمه‌ها
                if not name or name in seen_names: continue
                if "های" in name or "ثبت" in name or "مشاهده" in name or "انتخاب" in name: continue
                
                seen_names.add(name)
                
                # پیدا کردن متن والد برای استخراج قیمت و ستاره
                parent = link.locator("xpath=..").locator("xpath=..").locator("xpath=..")
                parent_text = await parent.inner_text()
                
                # استخراج ستاره
                stars = 0
                star_match = re.search(r'([1-5])\s*ستاره', parent_text)
                if star_match: stars = int(star_match.group(1))
                
                # استخراج قیمت
                prices = re.findall(r'([\d,]+)\s*تومان', parent_text)
                if prices:
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    results.append({"name": name, "price": min_price, "stars": stars})
            except: pass
            
        # حذف تکراری‌ها
        unique_hotels = {}
        for h in results:
            if h["name"] not in unique_hotels:
                unique_hotels[h["name"]] = h
        final_list = list(unique_hotels.values())
        
        # گروه‌بندی بر اساس ستاره
        grouped = {5: [], 4: [], 3: []}
        for h in final_list:
            if h["stars"] in grouped:
                grouped[h["stars"]].append(h)
                
        print(f"Found {len(final_list)} hotels with stars!")
        
        # ساخت پیش‌نمایش پیام
        msg = "🏨 <b>قیمت لحظه‌ای هتل‌های شیراز</b>\n\n"
        
        for star_level in [5, 4, 3]:
            if grouped[star_level]:
                selected = random.sample(grouped[star_level], min(3, len(grouped[star_level])))
                msg += f"⭐ <b>هتل‌های {star_level} ستاره:</b>\n"
                for h in selected:
                    msg += f"🔹 {h['name']}: {h['price']:,} تومان\n"
                msg += "\n"
                
        msg += "📞 <b>برای رزرو تلفنی با ما در تماس باشید:</b>\n☎️ 0915XXXXXXX\n\n✈️ <b>درنا سفر</b>"
        
        print("--- پیام نهایی ---")
        print(msg)
        print("------------------")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
