import asyncio
from playwright.async_api import async_playwright
import re
import random

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.eghamat24.com/MashhadHotels.html"
        print("Opening Mashhad Hotels...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(12000)
        
        # پیدا کردن همه لینک‌های هتل
        links = await page.locator("a[href*='/MashhadHotels/']").all()
        
        results = []
        seen_names = set()
        
        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or not href.endswith(".html"): continue
                
                hotel_id = href.split("/")[-1].replace(".html", "")
                if hotel_id in ["MashhadHotels", "CheapHotels"]: continue
                
                name = re.sub(r'(?<!^)(?=[A-Z])', ' ', hotel_id).replace("_", " ").strip()
                if name in seen_names: continue
                seen_names.add(name)
                
                # 🌟 پیدا کردن دقیق قیمت با استفاده از تگ‌های همسایه
                # به جای xpath های طولانی، از یک روش ساده‌تر استفاده میکنیم:
                # کل کارت رو از روی لینک پیدا میکنیم
                card = link.locator("xpath=ancestor::div[contains(@class, 'card') or contains(@class, 'item')][1]")
                
                # اگر کارت پیدا نشد، از والد معمولی استفاده میکنیم
                if await card.count() == 0:
                    card = link.locator("xpath=..").locator("xpath=..").locator("xpath=..")
                    
                card_text = await card.inner_text()
                prices = re.findall(r'([\d,]+)\s*تومان', card_text)
                
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
        
        msg = "🏨 <b>قیمت لحظه‌ای هتل‌های مشهد</b>\n\n"
        for h in final_list[:10]:
            msg += f"🔹 {h['name']}: {h['price']:,} تومان\n"
            
        msg += "\n📞 <b>برای رزرو تلفنی با ما در تماس باشید:</b>\n☎️ 0915XXXXXXX\n\n✈️ <b>درنا سفر</b>"
        
        print("--- پیام نهایی ---")
        print(msg)
        print("------------------")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
