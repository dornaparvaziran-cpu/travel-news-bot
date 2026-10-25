import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # رفتن به هتل پرسپولیس شیراز
        url = "https://www.eghamat24.com/ShirazHotels/PerspolisHotel.html"
        print(f"Opening {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        html_content = await page.content()
        
        print("\n--- Searching for property ID patterns ---")
        
        # جستجوی الگوهای مختلف برای پیدا کردن ID عددی
        patterns = [
            r'property_id["\']?\s*[:=]\s*["\']?(\d+)',
            r'propertyId["\']?\s*[:=]\s*["\']?(\d+)',
            r'property-id=["\']?(\d+)',
            r'/properties/(\d+)',
            r'data-property-id=["\']?(\d+)',
            r'id=["\'](\d+)',
            r'item_id["\']?\s*[:=]\s*["\']?(\d+)'
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, html_content)
            if matches:
                print(f"Pattern {i+1} found: {matches[:5]}")
                
        # پیدا کردن اعداد ۳ تا ۵ رقمی نزدیک به کلمه hotel
        print("\n--- Searching around 'hotel' word ---")
        hotel_context = re.findall(r'hotel.{0,50}?(\d{3,5})', html_content, re.IGNORECASE)
        if hotel_context:
            print(f"Numbers near hotel: {hotel_context[:10]}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
