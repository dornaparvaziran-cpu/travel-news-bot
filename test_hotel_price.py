import asyncio
from playwright.async_api import async_playwright
import re
from datetime import datetime, timedelta

async def main():
    # محاسبه تاریخ فردا به صورت داینامیک
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Target Date: {tomorrow}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # لینک جستجوی شیراز با تاریخ فردا
        url = f"https://www.eghamat24.com/search/property?destination_id=100&destination_name=Shiraz&check_in={tomorrow}&length_of_stay=1"
        print(f"Opening: {url}")
        
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(15000) # صبر برای لود کامل جاوااسکریپت
        
        # پیدا کردن همه لینک‌های هتل
        links = await page.locator("a[href*='/ShirazHotels/']").all()
        print(f"Found {len(links)} hotel links.")
        
        results = []
        seen_names = set()
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or not href.endswith(".html"): continue
                
                hotel_id = href.split("/")[-1].replace(".html", "")
                if hotel_id == "ShirazHotels": continue 
                
                # تبدیل CamelCase به اسم خوانا
                name = re.sub(r'(?<!^)(?=[A-Z])', ' ', hotel_id).strip()
                
                if name in seen_names: continue
                seen_names.add(name)
                
                # پیدا کردن قیمت با جستجوی کلمه "تومان" در کل صفحه
                # این روش دقیق‌ترین نیست اما برای تست اولیه خوب است
                parent_text = await link.inner_text()
                
                # اگر قیمت کنار لینک نبود، از کل صفحه قیمت‌ها را می‌گیریم
                if "تومان" not in parent_text:
                     # یک روش ساده: گرفتن متن از والد سطح بالاتر
                     parent = link.locator("xpath=ancestor::div[contains(@class, 'property') or contains(@class, 'item')][1]")
                     parent_text = await parent.inner_text()
                
                prices = re.findall(r'([\d,]+)\s*تومان', parent_text)
                if prices:
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    results.append({"name": name, "price": min_price})
            except Exception as e:
                pass
            
        unique_hotels = {}
        for h in results:
            if h["name"] not in unique_hotels:
                unique_hotels[h["name"]] = h
        final_list = list(unique_hotels.values())
                
        print(f"Successfully extracted {len(final_list)} hotels with prices.")
        
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
