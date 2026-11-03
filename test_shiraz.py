import requests
import random
import re

def main():
    # کدهای شهرها (از روی عکس شما و حدس برای بقیه)
    city_codes = {
        "آنتالیا": "10910", # حدس
        "استانبول": "10908", # حدس
        "کیش": "15676", # از عکس
        "مشهد": "21931", # از عکس
        "شیراز": "18911", # از عکس
        "اصفهان": "8849", # از عکس
        "تبریز": "19749", # از عکس
        "ایروان": "23298", # حدس
        "وان": "23299", # حدس
        "کوالالامپور": "23300" # حدس
    }
    
    # انتخاب ۵ شهر تصادفی
    cities = list(city_codes.keys())
    selected_cities = random.sample(cities, min(5, len(cities)))
    
    print("شهرهای انتخاب شده برای تست:", selected_cities)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    for city in selected_cities:
        city_id = city_codes[city]
        url = f"https://tourapi.safarmarket.com/api/v1/application/web/tours/top-selling/tours/{city_id}"
        
        print(f"\nدر حال دریافت تورهای {city}...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # ساختار دیتای برگشتی را چک می‌کنیم
                # (معمولاً لیستی از تورها در کلید data یا tours است)
                tours = data.get("data", []) or data.get("tours", [])
                if not tours:
                    print(f"توری برای {city} پیدا نشد.")
                    continue
                
                # پیدا کردن ارزان‌ترین تور
                cheapest_tour = None
                min_price = float('inf')
                
                for tour in tours:
                    # استخراج قیمت (بسته به ساختار JSON شاید متفاوت باشد)
                    price = tour.get("price", 0)
                    if 0 < price < min_price:
                        min_price = price
                        cheapest_tour = tour
                        
                if cheapest_tour:
                    print(f"✅ ارزان‌ترین تور {city}:")
                    print(f"قیمت: {min_price:,} تومان")
                    # چاپ کلیدهای دیتا برای اینکه ببینیم اسم هتل کجاست
                    print(f"کلیدهای موجود در دیتا: {list(cheapest_tour.keys())[:10]}")
                else:
                    print(f"قیمتی پیدا نشد.")
            else:
                print(f"خطا در دریافت دیتا. کد وضعیت: {response.status_code}")
        except Exception as e:
            print(f"خطای شبکه یا JSON: {e}")

if __name__ == "__main__":
    main()
