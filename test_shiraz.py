import random
import json

def main():
    print("Testing Local Food of the Day...")
    
    try:
        with open("foods.json", "r", encoding="utf-8") as f:
            all_foods = json.load(f)
            
        food = random.choice(all_foods)
        
        text = f"🍽️ <b>غذای محلی امروز: {food['name']} ({food['city']})</b>\n\n"
        text += f"{food['description']}\n\n"
        text += "📞 <b>برای رزرو تور و مشاوره سفر با ما در تماس باشید:</b>\n"
        text += "☎️ 05132292292\n"
        text += "📱 09153092528\n\n"
        text += "✈️ <b>درنا تراول</b>"
        
        print("\n--- پیش‌نمایش پیام ---")
        print(text)
        print("-----------------------")
        print(f"\nلینک عکس تولید شده: \n{food['image']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
