import subprocess
import sys
import asyncio
import json

# 🌟 نصب پکیج مستربلیط به صورت موقت برای تست
print("Installing mrbilit-mcp...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "mrbilit-mcp"])

try:
    from mrbilit_mcp import MrBilit
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def main():
    print("Testing MrBilit MCP...")
    
    try:
        # اتصال به سرویس
        client = MrBilit()
        
        print("Searching for hotels in Mashhad...")
        # جستجوی هتل در مشهد (کد شهر ۱ برای مشهد)
        result = await client.search_hotels(city_id=1, check_in="2026-10-26", check_out="2026-10-27")
        
        print("Result received!")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
