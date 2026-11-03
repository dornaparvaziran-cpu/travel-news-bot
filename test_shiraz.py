import asyncio
from playwright.async_api import async_playwright
import random
import re

TOUR_IMAGE_URL = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1000&auto=format&fit=crop"

async def main():
    url = "https://safarmarket.com/tours/lastminute"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("در حال باز کردن صفحه سفرمارکت...")
        
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(8000)
            
            tabs = await page.locator("span.CardsTitle").all()
            
            valid_tabs = []
            for tab in tabs:
                try:
                    raw_text = await tab.inner_text()
                    clean_name = raw_text.replace("\xa0", " ").strip()
                    
                    if clean_name and len(clean_name) < 20 and clean_name not in ["تور", "هتل"]:
                        valid_tabs.append({"element": tab, "name": clean_name})
                except:
                    pass
            
            if not valid_tabs:
                print("تبی پیدا نشد.")
                await browser.close()
                return
                
            random_tabs = random.sample(valid_tabs, min(5, len(valid_tabs)))
            final_tours = []
            
            for tab_info in random_tabs:
                tab_name = tab_info["name"]
                print(f"\nدر حال کلیک روی تب {tab_name}...")
                
                try:
                    await tab_info["element"].click()
                    await page.wait_for_timeout(8000)
                    
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
                                # 🎯 فیلتر جدید و هوشمند برای اسم هتل
                                is_valid_hotel_name = False
                                if re.search(r'[A-Za-z]{3,}', line): # اگر حروف انگلیسی دارد (مثل Hotel)
                                    is_valid_hotel_name = True
                                elif "هتل" in line or "سوئیت" in line or "اقامتگاه" in line or "بوتیک" in line: # یا کلمات فارسی هتل
                                    is_valid_hotel_name = True
                                
                                if (is_valid_hotel_name and 
                                    len(line) > 5 and 
                                    word_count < 10 and 
                                    "تومان" not in line and 
                                    "شب" not in line):
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
            print(f"\n🌟 لینک عکس: {TOUR_IMAGE_URL}")
        else:
            print("❌ هیچ توری پیدا نشد.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
