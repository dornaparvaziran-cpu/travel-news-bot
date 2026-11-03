import asyncio
from playwright.async_api import async_playwright
import re
import random

async def main():
    url = "https://safarmarket.com/tours/lastminute"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("در حال باز کردن صفحه سفرمارکت...")
        
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # پیدا کردن تب‌های مقصد (شهرها)
            tabs = await page.locator("div, span, a").filter(has_text=re.compile(r"^(آنتالیا|استانبول|کیش|مشهد|شیراز|ایروان|وان|کوالالامپور|پاتایا|کوش آداسی|قشم|تبریز|اصفهان)$")).all()
            
            unique_tabs = []
            seen_texts = set()
            for tab in tabs:
                try:
                    text = await tab.inner_text()
                    text = text.strip()
                    if text and text not in seen_texts and len(text) < 20:
                        seen_texts.add(text)
                        unique_tabs.append({"element": tab, "name": text})
                except:
                    pass
            
            print(f"تعداد تب‌های پیدا شده: {len(unique_tabs)}")
            
            if not unique_tabs:
                print("تبی پیدا نشد. ادامه با نتایج پیش‌فرض...")
                search_btn = page.locator("button:has-text('جستجوی تور'), a:has-text('جستجوی تور')").first
                if await search_btn.count() > 0:
                    await search_btn.click()
                    await page.wait_for_timeout(10000)
            
            # انتخاب ۵ تب تصادفی
            random_tabs = random.sample(unique_tabs, min(5, len(unique_tabs)))
            
            final_tours = []
            
            for tab_info in random_tabs:
                tab_name = tab_info["name"]
                print(f"در حال بررسی تب: {tab_name}")
                
                try:
                    await tab_info["element"].click()
                    await page.wait_for_timeout(8000) # صبر برای لود تورهای تب جدید
                    
                    cards = await page.locator("div:has-text('جزئیات تور')").all()
                    
                    tab_tours = []
                    for card in cards:
                        try:
                            text = await card.inner_text()
                            if "تومان" not in text:
                                continue
                                
                            text = text.replace("location_on", "").replace("flight_takeoff", "").replace("flight_land", "").replace("directions_bus", "").replace("جزئیات تور", "")
                            lines = [line.strip() for line in text.split('\n') if line.strip()]
                            
                            # استخراج قیمت به صورت عدد برای مقایسه
                            price_match = re.search(r'([\d,۰-۹]+)\s*تومان', text)
                            if not price_match:
                                continue
                            
                            price_str = price_match.group(0)
                            # تبدیل اعداد فارسی به انگلیسی برای مقایسه
                            price_num_str = price_match.group(1).replace(",", "").replace("۰", "0").replace("۱", "1").replace("۲", "2").replace("۳", "3").replace("۴", "4").replace("۵", "5").replace("۶", "6").replace("۷", "7").replace("۸", "8").replace("۹", "9")
                            price_num = int(price_num_str)
                            
                            hotel = "نامشخص"
                            destination = "نامشخص"
                            
                            for line in lines:
                                word_count = len(line.split())
                                if (len(line) > 5 and word_count < 8 and "تومان" not in line and "شب" not in line and "," not in line and "آبان" not in line and "آذر" not in line and "دی" not in line and "پرفروش" not in line and "تورها" not in line):
                                    hotel = line
                                    break
                                    
                            for line in lines:
                                if "شب" in line:
                                    destination = line
                                    break
                            
                            if hotel != "نامشخص" and destination != "نامشخص":
                                tab_tours.append({
                                    "hotel": hotel,
                                    "destination": destination,
                                    "price_str": price_str,
                                    "price_num": price_num
                                })
                        except:
                            pass
                            
                    # پیدا کردن ارزان‌ترین تور این تب
                    if tab_tours:
                        cheapest = min(tab_tours, key=lambda x: x["price_num"])
                        final_tours.append(cheapest)
                        print(f"  ✅ ارزان‌ترین در {tab_name}: {cheapest['hotel']} - {cheapest['price_str']}")
                    else:
                        print(f"  ❌ توری در {tab_name} پیدا نشد.")
                        
                except Exception as e:
                    print(f"  خطا در کلیک روی تب {tab_name}: {e}")
                    
        except Exception as e:
            print(f"خطای کلی: {e}")
            await browser.close()
            return
            
        print(f"\n✅ در مجموع {len(final_tours)} تور از ۵ مقصد استخراج شد.")
        
        if final_tours:
            msg = "🎟️ <b>ارزان‌ترین تورهای لحظه آخری (از ۵ مقصد)</b>\n\n"
            for t in final_tours:
                msg += f"🔹 <b>{t['destination']}</b>\n"
                msg += f"🏨 {t['hotel']}\n"
                msg += f"💰 {t['price_str']}\n\n"
                
            msg += "📞 <b>برای رزرو با ما در تماس باشید:</b>\n"
            msg += "☎️ 05132292292\n"
            msg += "📱 09153092528\n\n"
            msg += "✈️ <b>درنا تراول</b>"
            
            print("\n" + "="*40)
            print("پیش‌نمایش پیام:")
            print("="*40)
            print(msg)
            print("="*40)
        else:
            print("❌ هیچ توری پیدا نشد.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
