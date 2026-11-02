import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    url = "https://safarmarket.com/tours/lastminute"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("در حال باز کردن صفحه سفرمارکت...")
        
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # پیدا کردن و کلیک روی دکمه جستجو
            print("در حال کلیک روی دکمه جستجو...")
            # به دنبال دکمه‌ای می‌گردیم که متن آن شامل "جستجوی تور" است
            search_btn = page.locator("button:has-text('جستجوی تور'), a:has-text('جستجوی تور')").first
            if await search_btn.count() > 0:
                await search_btn.click()
                print("دکمه جستجو کلیک شد. منتظر لود نتایج...")
                # صبر می‌کنیم تا نتایج لود شوند
                await page.wait_for_timeout(15000)
            else:
                print("دکمه جستجو پیدا نشد. شاید صفحه مستقیم نتایج را نشان دهد.")
                await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"خطا در تعامل با صفحه: {e}")
            await browser.close()
            return
            
        text = await page.inner_text('body')
        print(f"طول محتوای جدید: {len(text)} کاراکتر")
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # چاپ ۵۰ خط برای بررسی نتایج
        print("\n--- ۵۰ خط اول متن صفحه بعد از جستجو ---")
        for line in lines[:50]:
            print(line)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
