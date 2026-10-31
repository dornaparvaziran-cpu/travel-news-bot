import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    # لینک تستی هتل گلدن پالاس (همان لینکی که فرستادید)
    url = "https://www.iranhotelonline.com/mashhad-hotels/%D9%87%D8%AA%D9%84-%DA%AF%D9%84%D8%AF%D9%86-%D9%BE%D8%A7%D9%84%D8%A7%D8%B3/?date=1405%2F08%2F09&endDate=1405%2F08%2F10&refer=searchresult"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("در حال باز کردن صفحه ایران‌هتل...")
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            # صبر می‌کنیم تا جاوااسکریپت‌های سایت لود شوند
            await page.wait_for_timeout(15000) 
        except Exception as e:
            print(f"خطا در باز کردن صفحه: {e}")
            await browser.close()
            return
            
        content = await page.content()
        print(f"صفحه لود شد. طول محتوا: {len(content)} کاراکتر")
        
        # جستجوی کلمه "تومان" در متن
        prices = re.findall(r'([\d,]+)\s*تومان', content)
        
        if prices:
            print(f"✅ تعداد {len(prices)} قیمت پیدا شد. ۵ مورد اول: {prices[:5]}")
        else:
            print("❌ هیچ قیمتی پیدا نشد. احتمالا سایت بلاک کرده یا ساختار عوض شده.")
            # چاپ بخشی از متن برای دیباگ
            text = await page.inner_text('body')
            print("متن صفحه (۵۰۰ کاراکتر اول):\n", text[:500])
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
