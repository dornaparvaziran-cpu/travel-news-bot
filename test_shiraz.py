import requests
import feedparser
import os
import re
import time
import translators as ts

def main():
    print("Testing Multi-Provider Translator (Translators lib)...")
    
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
    
    # ۲. تست ترجمه با موتورهای مختلف
    # ما به ترتیب Bing و سپس Google را امتحان می‌کنیم
    engines_to_try = ['bing', 'google']
    
    for engine in engines_to_try:
        print(f"\n--- Trying engine: {engine} ---")
        try:
            # ترجمه تیتر
            translated_title = ts.translate_text(title, translator=engine, from_language='en', to_language='fa')
            # ترجمه متن
            translated_text = ts.translate_text(full_text, translator=engine, from_language='en', to_language='fa') if full_text else ""
            
            print(f"✅ Translated Title ({engine}):\n{translated_title}")
            print(f"\n✅ Translated Text ({engine}):\n{translated_text[:200]}...")
            
            # اگر موفق بود، از حلقه خارج شو
            break
            
        except Exception as e:
            print(f"❌ Engine {engine} failed: {e}")
            time.sleep(2) # کمی صبر کن تا دوباره تلاش کنیم

if __name__ == "__main__":
    main()
