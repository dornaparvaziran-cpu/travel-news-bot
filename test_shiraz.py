import subprocess
import sys
import json
import asyncio

# نصب خودکار ابزارها
print("Installing mcp and flytoday-mcp...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp", "flytoday-mcp", "-q"])

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    print("Starting FlyToday MCP server...")
    
    server_params = StdioServerParameters(
        command="flytoday-mcp",
        args=[],
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ MCP server initialized!")

                # ۱. پیدا کردن کد شهر مشهد
                print("\nStep 1: Finding Mashhad city ID...")
                find_result = await session.call_tool(
                    "ft_find_hotel_place",
                    arguments={"query": "مشهد"}
                )
                print("Find result:", json.dumps(find_result.content, indent=2, ensure_ascii=False)[:1000])

                # ۲. جستجوی هتل‌ها با قیمت (فرض می‌کنیم city_id=10 درسته)
                print("\nStep 2: Searching hotels in Mashhad...")
                search_result = await session.call_tool(
                    "ft_search_hotels",
                    arguments={
                        "city_id": 10,
                        "check_in": "2026-10-27",
                        "check_out": "2026-10-28"
                    }
                )
                
                print("✅ Hotel search successful!")
                print(json.dumps(search_result.content, indent=2, ensure_ascii=False)[:3000])

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
