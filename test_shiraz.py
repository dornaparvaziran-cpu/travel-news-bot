import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    url = "https://www.iranhotelonline.com/mashhad-hotels/%D9%87%D8%AA%D9%84-%DA%AF%D9%84%D8%AF%D9%86-%D9%BE%D8%A7%D9%84%D8%A7%D8%B3/?date=1405%2F08%2F09&endDate=1405%2F08%2F10&refer=searchresult"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("در حال باز کردن صفحه ایران‌هتل...")
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            # صبر بیشتر برای لود شدن قیمت‌ها
            await page.wait_for_timeout(20000) 
        except Exception as e:
            print(f"خطا در باز کردن صفحه: {e}")
            await browser.close()
            return
            
        content = await page.content()
        print(f"صفحه لود شد. طول محتوا: {len(content)} کاراکتر")
        
        # جستجوی کلمه "تومان"
        prices = re.findall(r'([\d,]+)\s*تومان', content)
        
        if prices:
            print(f"✅ تعداد {len(prices)} قیمت پیدا شد. ۵ مورد اول: {prices[:5]}")
        else:
            print("❌ هیچ قیمتی با فرمت 'عدد تومان' پیدا نشد.")
            # چاپ بخشی از متن که شامل اعداد بزرگ است
            text = await page.inner_text('body')
            
            # پیدا کردن خطوطی که شامل اعداد ۶ رقمی یا بیشتر هستند
            lines = text.split('\n')
            price_like_lines = [line for line in lines if re.search(r'\d{3},\d{3}', line)]
            
            print("\n--- خطوطی که شبیه قیمت هستند ---")
            for line in price_like_lines[:10]:
                print(line.strip())
                
            print("\n--- ۱۰ خط آخر متن صفحه ---")
            for line in lines[-10:]:
                print(line.strip())
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
