import requests
import feedparser
import os
import re
import time
from deep_translator import GoogleTranslator

def main():
    print("Testing Google Translate (Batch Mode)...")
    
    # ۱. گرفتن یک خبر انگلیسی از Skift
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
    
    full_text = re.sub(r'<[^>]+>', '', full_text).strip()
    
    print(f"\nOriginal Title: {title}")
    print(f"Original Text (first 100 chars): {full_text[:100]}...")
    
    # ۲. تست ترجمه با متد translate_batch
    print("\nTranslating with Google (Batch)...")
    try:
        translator = GoogleTranslator(source='en', target='fa')
        
        # 🌟 همه متن‌ها رو یکجا می‌فرستیم
        texts_to_translate = [title]
        if full_text:
            texts_to_translate.append(full_text)
            
        translated_list = translator.translate_batch(texts_to_translate)
        
        translated_title = translated_list[0]
        translated_text = translated_list[1] if len(translated_list) > 1 else ""
        
        print(f"\n✅ Translated Title:\n{translated_title}")
        print(f"\n✅ Translated Text:\n{translated_text[:200]}...")
        
    except Exception as e:
        print(f"❌ Translation Error: {e}")
        # اگر خطای 429 (Too many requests) داد، ۳ ثانیه صبر می‌کنیم و دوباره تلاش می‌کنیم
        if "429" in str(e) or "Too Many" in str(e):
            print("⏳ Waiting 3 seconds and retrying...")
            time.sleep(3)
            try:
                translated_list = translator.translate_batch(texts_to_translate)
                translated_title = translated_list[0]
                translated_text = translated_list[1] if len(translated_list) > 1 else ""
                print(f"\n✅ (Retry) Translated Title:\n{translated_title}")
            except Exception as e2:
                print(f"❌ Retry failed: {e2}")

if __name__ == "__main__":
    main()
