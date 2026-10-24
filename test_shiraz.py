import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # لیست شهرها با لینک مستقیم صفحه هتل‌هاشون
        cities = {
            "مشهد": "https://www.eghamat24.com/MashhadHotels.html",
            "تهران": "https://www.eghamat24.com/TehranHotels.html",
            "کیش": "https://www.eghamat24.com/KishHotels.html",
            "شیراز": "https://www.eghamat24.com/ShirazHotels.html",
            "اصفهان": "https://www.eghamat24.com/EsfahanHotels.html",
            "یزد": "https://www.eghamat24.com/YazdHotels.html",
            "تبریز": "https://www.eghamat24.com/TabrizHotels.html",
            "قم": "https://www.eghamat24.com/QomHotels.html",
            "قشم": "https://www.eghamat24.com/QeshmHotels.html",
        }
        
        for city_name, url in cities.items():
            print(f"\n--- Checking {city_name} ---")
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_timeout(10000)
                
                # پیدا کردن لینک‌هایی که به هتل‌های این شهر اشاره می‌کنن
                links = await page.locator("a[href*='Hotel']").all()
                
                hotel_count = 0
                for link in links:
                    try:
                        href = await link.get_attribute("href")
                        text = await link.inner_text()
                        # اگر لینک شامل اسم شهر و Hotel بود و متنش هم شبیه اسم هتل بود
                        if href and city_name in href and "Hotel" in href:
                            if text.strip() and len(text.strip()) > 5 and "هتل" in text:
                                hotel_count += 1
                    except: pass
                
                print(f"Found {hotel_count} potential hotel links for {city_name}")
                
            except Exception as e:
                print(f"Error for {city_name}: {e}")
            finally:
                await page.close()
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
