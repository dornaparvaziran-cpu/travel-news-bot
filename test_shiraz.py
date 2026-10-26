import requests
import feedparser
import os

METIS_KEY = os.environ.get("METIS_KEY")

def main():
    print("Testing Metis Translation...")
    
    if not METIS_KEY:
        print("❌ METIS_KEY is missing!")
        return
        
    # گرفتن یک خبر انگلیسی از Skift
    print("Fetching an English news item...")
    feed = feedparser.parse("https://skift.com/feed/")
    if not feed.entries:
        print("❌ No news found.")
        return
        
    entry = feed.entries[0]
    title = entry.get("title", "")
    
    full_text = ""
    if 'content' in entry and len(entry.content) > 0:
        full_text = entry.content[0].value
    elif 'summary' in entry:
        full_text = entry.summary
    
    # پاک کردن تگ‌های HTML
    import re
    full_text = re.sub(r'<[^>]+>', '', full_text).strip()
    
    print(f"Original Title: {title}")
    print(f"Original Text (first 100 chars): {full_text[:100]}...")
    
    # تست ترجمه با متیس
    print("\nSending to Metis for translation...")
    prompt = f"Translate the following English text to Persian (Farsi). Return ONLY the translated text, without any extra explanation or English words:\n\n{full_text}"
    headers = {"Authorization": f"Bearer {METIS_KEY}", "Content-Type": "application/json"}
    data = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    
    try:
        r = requests.post("https://api.metisai.ir/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
        print(f"Status Code: {r.status_code}")
        
        if r.ok:
            response_data = r.json()
            translated = response_data['choices'][0]['message']['content'].strip()
            print(f"\n✅ Translated Text:\n{translated}")
        else:
            print(f"❌ Error Response: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
