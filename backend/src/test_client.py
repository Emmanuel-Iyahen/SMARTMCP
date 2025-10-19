# test_client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_client():
    server_params = StdioServerParameters(
        command="python",
        args=["/home/townbox/Desktop/smartMCP/backend/src/modules/mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            
            # Test a tool
            result = await session.call_tool("get_transport_data", {})
            print("Transport data:", result.content)

            # Test other tools
            await session.call_tool("get_financial_data", {"days_back": 7})
            await session.call_tool("get_weather_data", {})
            await session.call_tool("get_combined_daily_data", {})

if __name__ == "__main__":
    asyncio.run(test_client())