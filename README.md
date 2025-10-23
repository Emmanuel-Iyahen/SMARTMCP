# SmartMCP - Universal Multi-Sector Data Analysis Platform with MCP Support


![AI Powered Analysis](https://gaspar-www-test.sfo3.cdn.digitaloceanspaces.com/a3ead86fc17c131fa0cb0ba2c3b60ca8.png?updated_at=2023-01-26T11:38:04.797Z)

# 🧩 Overview

SmartMCP is a domain-agnostic multi-sector data analysis platform that serves as both a comprehensive dashboard for data analysis and a Model Context Protocol (MCP) server providing real-time data and AI-powered insights to other MCP clients.

## 🚀 Features

📊 Multi-Sector Data Integration

   - Transport: Real-time TFL (Transport for London) data with service status and delays

   - Finance: UK stock market data from Snowflake with trend analysis

   - Weather: Current London weather conditions and forecasts

   - AI Analysis: GPT-powered insights across all data sectors

   - Visualization: Interactive charts and dashboards

---

**Live Demo:** [Customer App](https://ev-charging-frontend-seven.vercel.app)  


# ARCHITECTURE
![architecture Demo](mcpDesign.png)

### 🔌 MCP Server Capabilities

  - Standard MCP 1.0.0 Compliance

   - Tool Execution: 5+ data tools for external MCP clients

   - Resource Access: Structured data resources

   - Authentication: Secure bearer token authentication

   - Discovery: Standard .well-known/mcp.json endpoint

### 


# Installation (Lecal environment)

## Prerequisites

   - Python 3.10+

   - Snowflake account (for financial data)

   - TFL API credentials (optional)

## 1. Clone the repository
    git https://github.com/Emmanuel-Iyahen/EV-CHARGING-SYSTEM.git
    cd cpms-backend

## 1. Create virtual environment
    virtualenv venv
    source venv/bin/activate

## 1. install dependencies  
    pip install -r requirements.txt

## 1. Run application
    uvicorn main:app --reload




## 🔌 MCP Server Configuration
### For MCP Client Developers

SmartMCP exposes a standard MCP 1.0.0 compliant server that other MCP clients can connect to.

## Discovery Endpoint

    GET /.well-known/mcp.json

No authentication required - returns server capabilities.

## Client Configuration Examples
### 1. Claude Desktop Configuration
    {
    "mcpServers": {
        "smartmcp": {
        "command": "npx",
        "args": [
            "@modelcontextprotocol/server-smartmcp",
            "--url",
            "https://your-smartmcp-server.com",
            "--token",
            "your-mcp-api-key"
        ]
        }
    }
    }

### 2. Direct HTTP Configuration

    {
    "mcpServers": {
        "smartmcp": {
        "command": "http",
        "args": {
            "url": "https://your-smartmcp-server.com/.well-known/mcp.json",
            "headers": {
            "Authorization": "Bearer your-mcp-api-key"
            }
        }
        }
    }
    }

### 3. Python Client Usage
    import httpx

    class SmartMCPClient:
        def __init__(self, base_url: str, api_key: str):
            self.base_url = base_url
            self.headers = {"Authorization": f"Bearer {api_key}"}
        
        async def get_transport_data(self):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/mcp/tools/get_transport_data",
                    json={},
                    headers=self.headers
                )
                return response.json()
        
        async def list_tools(self):
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/mcp/tools",
                    headers=self.headers
                )
                return response.json()
    #Usage
    client = SmartMCPClient("https://your-smartmcp-server.com", "your-api-key")
    transport_data = await client.get_transport_data()



### 🛠️ Available MCP Tools

SmartMCP provides the following tools for MCP clients:

## 1. get_transport_data

 - Description: Get real-time TFL transport data including delays and service status

 - Parameters: None

 - Returns: Formatted transport status with emoji indicators

### 2. get_financial_data

 - Description: Get UK stock market data for major companies from Snowflake

 - Parameters:

    - days_back (number): Number of days of historical data (default: 7)

 - Returns: Stock prices, volumes, and company information

### 3. get_weather_data

 - Description: Get current London weather data

 - Parameters: None

 - Returns: Temperature, humidity, precipitation, and weather conditions

### 4. get_financial_trends

 - Description: Get financial trend analysis and market insights

 - Parameters:

   - period_days (number): Analysis period in days (default: 30)

 - Returns: Market trends, performance metrics, and sector analysis

### 5. get_combined_daily_data

 - Description: Get all daily data (transport, finance, weather) in one call

 - Parameters: None

 - Returns: Comprehensive daily report across all data sectors


## 🌐 API Endpoints

Dashboard & Analysis

 - GET / - Platform information

 - GET /health - Health check

 - GET /api/dashboard/ - Comprehensive dashboard data

 - GET /api/financial-trends - Financial trend analysis

 - POST /api/prompts/analyze - AI-powered analysis

## MCP Server Endpoints

 - GET /.well-known/mcp.json - MCP discovery

 - GET /mcp/tools - List available tools (authenticated)

 - POST /mcp/tools/{tool_name} - Execute tool (authenticated)

 - GET /mcp/resources - List resources (authenticated)

 - GET /mcp/resources/{resource_uri} - Read resource (authenticated)


🔒 Security

 - API Authentication: Bearer token authentication for MCP endpoints

 - CORS: Configurable CORS settings

 - Rate Limiting: Implemented on MCP endpoints

 - Environment Variables: Sensitive data stored in environment

### 📊 Data Sources
| Source       | Type       | Data Provided               | Authentication           |
|---------------|------------|-----------------------------|---------------------------|
| TFL API       | REST API   | Transport status, delays    | Optional App ID/Key       |
| Alphavantage     | REST API   | Financial market data       | Username/Password         |
| Open-Meteo    | REST API   | Weather data                | None required             |


## 🤝 Contributing

### We welcome contributions! Please see our Contributing Guide for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE ](https://example.com) file for details.
## 🆘 Support

 - 📚 Documentation

 - 🐛 Issue Tracker

 - 💬 Discussions

 - 📧 Email: your-email@example.com

## 🙏 Acknowledgments

 - Model Context Protocol for the MCP standard

 - TFL Unified API for transport data
 - Alphavantage for finance data
 - Open-Meteo for weather data

 - Snowflake for data warehousing

 - FastAPI for backend service
 - React for web frame work

### SmartMCP - Bridging data analysis and AI through standardized protocols. 🚀

Built with ❤️ for the MCP ecosystem