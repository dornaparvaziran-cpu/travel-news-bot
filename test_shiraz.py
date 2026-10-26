import requests
import feedparser
import os
import re

def main():
    print("Testing Google Translate (deep-translator)...")
    
    # ۱. بررسی نصب بودن پکیج
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print("❌ deep-translator is not installed. Please add it to requirements.txt")
        return
        
    # ۲. گرفتن یک خبر انگلیسی از Skift
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
    
    # ۳. تست ترجمه
    print("\nTranslating with Google...")
    try:
        translator = GoogleTranslator(source='en', target='fa')
        
        translated_title = translator.translate(title)
        translated_text = translator.translate(full_text) if full_text else ""
        
        print(f"\n✅ Translated Title:\n{translated_title}")
        print(f"\n✅ Translated Text:\n{translated_text[:200]}...")
        
    except Exception as e:
        print(f"❌ Translation Error: {e}")

if __name__ == "__main__":
    main()
