import asyncio
from playwright.async_api import async_playwright
import random
import re

async def main():
    url = "https://safarmarket.com/tours/lastminute"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("در حال باز کردن صفحه سفرمارکت...")
        
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(8000)
            
            # پیدا کردن تب‌های بالای صفحه با استفاده از کلاسی که در عکس دیدیم
            tabs = await page.locator("div.frequentCitiesItem, .frequentCitiesItem").all()
            
            # فیلتر کردن تب‌های واقعی (بعضی‌ها ممکن است مبدا باشند)
            valid_tabs = []
            for tab in tabs:
                try:
                    title = await tab.get_attribute("data-title")
                    # اگر اسم شهر معروفی بود، آن را نگه دار
                    if title and title in ["آنتالیا", "استانبول", "کیش", "مشهد", "شیراز", "ایروان", "کوالالامپور", "پاتایا"]:
                        # مختصات مرکز آن تب را پیدا کن
                        box = await tab.bounding_box()
                        if box:
                            valid_tabs.append({"name": title, "box": box})
                except:
                    pass
            
            print(f"تعداد تب‌های معتبر پیدا شده: {len(valid_tabs)}")
            
            if not valid_tabs:
                print("تبی پیدا نشد.")
                await browser.close()
                return
                
            # انتخاب ۵ تب تصادفی
            random_tabs = random.sample(valid_tabs, min(5, len(valid_tabs)))
            final_tours = []
            
            for tab_info in random_tabs:
                tab_name = tab_info["name"]
                box = tab_info["box"]
                
                print(f"\nدر حال کلیک روی تب {tab_name}...")
                
                try:
                    # کلیک با موس روی مختصات دقیق تب
                    await page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    await page.wait_for_timeout(8000) # صبر برای لود تورهای تب جدید
                    
                    cards = await page.locator("div:has-text('جزئیات تور')").all()
                    
                    city_tours = []
                    for card in cards:
                        try:
                            text = await card.inner_text()
                            if "تومان" not in text:
                                continue
                                
                            text = text.replace("location_on", "").replace("flight_takeoff", "").replace("flight_land", "").replace("directions_bus", "").replace("جزئیات تور", "")
                            lines = [line.strip() for line in text.split('\n') if line.strip()]
                            
                            price_match = re.search(r'([\d,۰-۹]+)\s*تومان', text)
                            if not price_match:
                                continue
                            
                            price_str = price_match.group(0)
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
                                city_tours.append({
                                    "hotel": hotel,
                                    "destination": destination,
                                    "price_str": price_str,
                                    "price_num": price_num
                                })
                        except:
                            pass
                            
                    if city_tours:
                        cheapest = min(city_tours, key=lambda x: x["price_num"])
                        final_tours.append(cheapest)
                        print(f"  ✅ ارزان‌ترین در {tab_name}: {cheapest['hotel']} - {cheapest['price_str']}")
                    else:
                        print(f"  ❌ توری در {tab_name} پیدا نشد.")
                        
                except Exception as e:
                    print(f"  خطا در کلیک روی {tab_name}: {e}")
                    
        except Exception as e:
            print(f"خطای کلی: {e}")
            await browser.close()
            return
            
        print(f"\n✅ در مجموع {len(final_tours)} تور از مقاصد مختلف استخراج شد.")
        
        if final_tours:
            msg = "🎟️ <b>ارزان‌ترین تورهای لحظه آخری (مقاصد مختلف)</b>\n\n"
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
