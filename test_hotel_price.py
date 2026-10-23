import asyncio
import requests
import re
import os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

def download_font():
    # دانلود فونت وزیرمتن
    font_url = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Bold.ttf"
    if not os.path.exists("Vazirmatn-Bold.ttf"):
        print("Downloading font...")
        r = requests.get(font_url)
        with open("Vazirmatn-Bold.ttf", "wb") as f:
            f.write(r.content)

def create_hotel_image(hotels):
    print("Creating image...")
    # تنظیمات ابعاد عکس
    width, height = 800, 800
    img = Image.new('RGB', (width, height), color='#f0f4f8') # رنگ پس‌زمینه آبی روشن
    draw = ImageDraw.Draw(img)
    
    # بارگذاری فونت
    try:
        font_title = ImageFont.truetype("Vazirmatn-Bold.ttf", 50)
        font_text = ImageFont.truetype("Vazirmatn-Bold.ttf", 35)
        font_footer = ImageFont.truetype("Vazirmatn-Bold.ttf", 25)
    except:
        print("Font load failed. Using default.")
        font_title = font_text = font_footer = ImageFont.load_default()

    # تابع کمکی برای نوشتن متن فارسی
    def draw_fa_text(draw, text, position, font, fill):
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        draw.text(position, bidi_text, font=font, fill=fill)

    # ۱. هدر عکس
    draw.rectangle([0, 0, width, 100], fill='#1e3a8a') # نوار آبی تیره
    draw_fa_text(draw, "قیمت لحظه‌ای هتل‌های مشهد", (width//2 - 200, 25), font_title, 'white')
    
    # ۲. لیست هتل‌ها
    y_offset = 150
    for i, (name, price) in enumerate(hotels):
        # خط جداکننده
        draw.line([(50, y_offset - 10), (width - 50, y_offset - 10)], fill='#cbd5e1', width=2)
        
        # اسم هتل (سمت راست)
        draw_fa_text(draw, name, (width - 400, y_offset), font_text, '#1e293b')
        
        # قیمت (سمت چپ)
        price_str = f"{price:,} تومان"
        draw_fa_text(draw, price_str, (50, y_offset), font_text, '#16a34a') # رنگ سبز
        
        y_offset += 80

    # ۳. فوتر (درنا سفر و رزرو تلفنی)
    draw.rectangle([0, height - 120, width, height], fill='#1e3a8a')
    draw_fa_text(draw, "برای رزرو با ما تماس بگیرید: 0915XXXXXXX", (width//2 - 220, height - 90), font_text, 'white')
    draw_fa_text(draw, "درنا سفر", (width//2 - 50, height - 40), font_footer, '#fbbf24')

    img.save("hotels_list.jpg")
    print("Image saved as hotels_list.jpg!")


async def main():
    download_font()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening Mashhad Hotels list...")
        await page.goto("https://www.eghamat24.com/MashhadHotels.html", timeout=60000, wait_until="domcontentloaded")
        
        print("Waiting 10 seconds...")
        await page.wait_for_timeout(10000)
        
        hotels = await page.locator("a[href*='Hotels/']").all()
        
        results = []
        for hotel in hotels[:10]: 
            try:
                name = await hotel.get_attribute("title")
                if not name: name = await hotel.inner_text()
                name = name.strip()
                if not name or len(name) < 3: continue
                
                parent = hotel.locator("xpath=..").locator("xpath=..")
                price_text = await parent.inner_text()
                
                prices = re.findall(r'([\d,]+)\s*تومان', price_text)
                if prices:
                    numeric_prices = [int(p.replace(',', '')) for p in prices]
                    min_price = min(numeric_prices)
                    results.append((name, min_price))
            except: continue
        
        unique_results = list(set(results))
        print(f"Found {len(unique_results)} hotels with prices!")
        
        # ساخت عکس با ۶ هتل اول
        if unique_results:
            create_hotel_image(unique_results[:6])
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
