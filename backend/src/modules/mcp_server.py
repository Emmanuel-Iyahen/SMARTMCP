# mcp_server.py
import asyncio
import json
import os
import aiohttp
import httpx
import pandas as pd
import snowflake.connector
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedDataLoader:
    """Simplified data loader without adapters dependency"""
    
    def __init__(self):
        self.snowflake_conn = self._init_snowflake()
    
    def _init_snowflake(self):
        """Initialize Snowflake connection"""
        try:
            conn = snowflake.connector.connect(
                user='SENIORMAN',
                password='Seniorman007123$',
                account='jibmsvk-VV57583',
                warehouse='MCP_WH',
                database='MCP_PLATFORM',
                schema='FINANCE'
            )
            logger.info("✅ Connected to Snowflake")
            return conn
        except Exception as e:
            logger.error(f"❌ Snowflake connection failed: {e}")
            return None

    async def load_transport_data(self) -> pd.DataFrame:
        """Load TFL transport data"""
        try:
            app_id = os.getenv('TFL_APP_ID', '')
            app_key = os.getenv('TFL_APP_KEY', '')
            
            params = {'detail': 'true'}
            if app_id and app_key:
                params.update({'app_id': app_id, 'app_key': app_key})
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://api.tfl.gov.uk/Line/Mode/tube,overground,dlr/Status',
                    params=params,
                    timeout=30
                )
                data = response.json()
                
                processed_records = []
                for line in data:
                    line_info = self._extract_line_info(line)
                    if line_info:
                        processed_records.append(line_info)
                
                return pd.DataFrame(processed_records)
                
        except Exception as e:
            logger.error(f"Error loading transport data: {e}")
            return self._get_sample_transport_data()

    def _extract_line_info(self, line_data) -> dict:
        """Extract line information from TFL API response"""
        try:
            line_id = line_data.get('id', 'unknown')
            line_name = line_data.get('name', 'Unknown Line')
            
            # Extract status information
            statuses = line_data.get('lineStatuses', [])
            status_info = self._extract_status_info(statuses)
            
            return {
                'line_id': line_id,
                'line_name': line_name,
                'mode': line_data.get('modeName', 'Unknown'),
                'timestamp': datetime.utcnow(),
                'status': status_info['status'],
                'status_severity': status_info['severity'],
                'reason': status_info['reason'],
                'delay_minutes': status_info['delay_minutes'],
                'is_active': status_info['is_active']
            }
        except Exception as e:
            logger.warning(f"Error extracting line info: {e}")
            return None

    def _extract_status_info(self, line_statuses: list) -> dict:
        """Extract status information"""
        if not line_statuses:
            return {
                'status': 'Good Service',
                'severity': 10,
                'reason': '',
                'delay_minutes': 0,
                'is_active': True
            }
        
        try:
            status = line_statuses[0]
            status_text = status.get('statusSeverityDescription', 'Good Service')
            severity = status.get('statusSeverity', 10)
            reason = status.get('reason', '')
            
            # Estimate delay
            delay_minutes = self._estimate_delay_from_severity(severity, status_text)
            is_active = severity < 20
            
            return {
                'status': status_text,
                'severity': severity,
                'reason': reason,
                'delay_minutes': delay_minutes,
                'is_active': is_active
            }
        except Exception as e:
            logger.warning(f"Error extracting status info: {e}")
            return {
                'status': 'Good Service',
                'severity': 10,
                'reason': '',
                'delay_minutes': 0,
                'is_active': True
            }

    def _estimate_delay_from_severity(self, severity: int, status_text: str) -> int:
        """Estimate delay minutes"""
        status_lower = status_text.lower()
        
        if severity <= 3:
            return 0
        elif severity <= 6:
            return 5
        elif severity <= 9:
            return 15
        else:
            return 30
        
        if 'good service' in status_lower:
            return 0
        elif 'minor' in status_lower:
            return 5
        elif 'severe' in status_lower:
            return 20
        elif 'closed' in status_lower:
            return 60
        else:
            return 10

    def _get_sample_transport_data(self) -> pd.DataFrame:
        """Sample transport data"""
        lines = ['Victoria', 'Central', 'Jubilee', 'Northern', 'Piccadilly']
        statuses = ['Good Service', 'Minor Delays', 'Severe Delays', 'Part Suspended']
        
        records = []
        for i, line in enumerate(lines):
            records.append({
                'timestamp': datetime.utcnow(),
                'line_id': f'line_{i}',
                'line_name': line,
                'mode': 'tube',
                'status': statuses[i % len(statuses)],
                'status_severity': 10 - (i % 4) * 3,
                'reason': 'Signal failure' if i % 3 == 0 else 'No issues',
                'delay_minutes': (i % 4) * 5,
                'is_active': True
            })
        
        return pd.DataFrame(records)

    async def load_financial_data_from_snowflake(self) -> pd.DataFrame:
        """Load financial data from Snowflake"""
        try:
            if self.snowflake_conn:
                query = """
                SELECT 
                    SYMBOL,
                    COMPANY_NAME,
                    OPEN,
                    HIGH,
                    LOW,
                    CLOSE,
                    VOLUME,
                    TIMESTAMP
                FROM MCP_PLATFORM.FINANCE.FINANCIAL_MARKET_DATA_PROCESSED 
                WHERE TIMESTAMP >= DATEADD(day, -7, CURRENT_DATE())
                ORDER BY TIMESTAMP DESC, SYMBOL
                """
                
                cursor = self.snowflake_conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                cursor.close()
                    
                logger.info(f"📊 Loaded {len(df)} financial records from Snowflake")
                return df
            else:
                logger.warning("Snowflake connection not available")
                return self._get_sample_financial_data()
                
        except Exception as e:
            logger.error(f"Error loading financial data: {e}")
            return self._get_sample_financial_data()

    def _get_sample_financial_data(self) -> pd.DataFrame:
        """Sample financial data"""
        symbols = ['HSBA.L', 'BP.L', 'GSK.L', 'ULVR.L', 'AZN.L', 'RIO.L', 'LLOY.L', 'BARC.L']
        companies = ['HSBC Holdings', 'BP', 'GSK', 'Unilever', 'AstraZeneca', 'Rio Tinto', 'Lloyds Banking', 'Barclays']
        
        data = []
        base_date = datetime.now() - timedelta(days=5)
        
        for i, (symbol, company) in enumerate(zip(symbols, companies)):
            for day in range(5):
                timestamp = base_date + timedelta(days=day)
                base_price = 1000 + (i * 100)
                close_price = base_price + (i * 10) + (day * 5)
                
                data.append({
                    'SYMBOL': symbol,
                    'COMPANY_NAME': company,
                    'OPEN': base_price,
                    'HIGH': close_price + 10,
                    'LOW': close_price - 5,
                    'CLOSE': close_price,
                    'VOLUME': 1000000 + (i * 100000),
                    'TIMESTAMP': timestamp
                })
        
        return pd.DataFrame(data)

    async def load_weather_data(self) -> pd.DataFrame:
        """Load London weather data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://api.open-meteo.com/v1/forecast',
                    params={
                        'latitude': 51.5074,
                        'longitude': -0.1278,
                        'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code',
                        'timezone': 'Europe/London'
                    },
                    timeout=30
                )
                data = response.json()
                
                current = data.get('current', {})
                return pd.DataFrame([{
                    'timestamp': datetime.utcnow(),
                    'temperature': current.get('temperature_2m', 0),
                    'humidity': current.get('relative_humidity_2m', 0),
                    'precipitation': current.get('precipitation', 0),
                    'weather_code': current.get('weather_code', 0),
                    'location': 'London'
                }])
                
        except Exception as e:
            logger.error(f"Error loading weather data: {e}")
            return self._get_sample_weather_data()

    def _get_sample_weather_data(self) -> pd.DataFrame:
        """Sample weather data"""
        return pd.DataFrame([{
            'timestamp': datetime.utcnow(),
            'temperature': 15.5,
            'humidity': 65,
            'precipitation': 0.0,
            'weather_code': 3,
            'location': 'London'
        }])

    async def load_financial_trend_data(self) -> pd.DataFrame:
        """Load financial trend data (simplified)"""
        return await self.load_financial_data_from_snowflake()

    def _process_financial_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Process financial trends (simplified)"""
        try:
            if data.empty:
                return self._get_sample_trend_analysis()
            
            # Simple trend calculation
            latest_data = data.sort_values('TIMESTAMP').groupby('SYMBOL').last().reset_index()
            
            market_trends = []
            for _, row in latest_data.iterrows():
                market_trends.append({
                    'symbol': row['SYMBOL'],
                    'company': row['COMPANY_NAME'],
                    'price': float(row['CLOSE']),
                    'change': 0.0  # Simplified for demo
                })
            
            return {
                'market_trends': market_trends,
                'performance_metrics': [
                    {'name': 'Market Status', 'value': 'Stable'},
                    {'name': 'Active Stocks', 'value': f'{len(latest_data)}'},
                    {'name': 'Data Freshness', 'value': 'Live'}
                ],
                'trend_indicators': [
                    {'name': 'Market Trend', 'status': 'Neutral'},
                    {'name': 'Volatility', 'status': 'Low'},
                    {'name': 'Liquidity', 'status': 'Good'}
                ],
                'stock_performance': [
                    {
                        'symbol': row['SYMBOL'],
                        'company': row['COMPANY_NAME'],
                        'change': 0.0,
                        'volatility': 0.0
                    } for _, row in latest_data.iterrows()
                ]
            }
        except Exception as e:
            logger.error(f"Error processing trends: {e}")
            return self._get_sample_trend_analysis()

    def _get_sample_trend_analysis(self) -> Dict[str, Any]:
        """Sample trend analysis"""
        return {
            'market_trends': [
                {'symbol': 'HSBA.L', 'company': 'HSBC', 'price': 650.0, 'change': 1.5},
                {'symbol': 'BP.L', 'company': 'BP', 'price': 480.0, 'change': -0.5}
            ],
            'performance_metrics': [
                {'name': 'Market Status', 'value': 'Sample Data'},
                {'name': 'Active Stocks', 'value': '8'},
                {'name': 'Data Source', 'value': 'Sample'}
            ],
            'trend_indicators': [
                {'name': 'Market Trend', 'status': 'Sample'},
                {'name': 'Volatility', 'status': 'Sample'},
                {'name': 'Data', 'status': 'Sample'}
            ],
            'stock_performance': [
                {'symbol': 'HSBA.L', 'company': 'HSBC', 'change': 1.5, 'volatility': 2.1},
                {'symbol': 'BP.L', 'company': 'BP', 'change': -0.5, 'volatility': 1.8}
            ]
        }

# Create server instance
server = Server("tfl-finance-weather")

# Create data loader instance
data_loader = SimplifiedDataLoader()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_transport_data",
            description="Get real-time TFL transport data including delays and service status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_financial_data", 
            description="Get UK stock market data for major companies from Snowflake",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_back": {
                        "type": "number",
                        "description": "Number of days of historical data to retrieve",
                        "default": 7
                    }
                }
            }
        ),
        types.Tool(
            name="get_weather_data",
            description="Get current London weather data",
            inputSchema={
                "type": "object", 
                "properties": {}
            }
        ),
        types.Tool(
            name="get_financial_trends",
            description="Get financial trend analysis and market insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "period_days": {
                        "type": "number",
                        "description": "Analysis period in days",
                        "default": 30
                    }
                }
            }
        ),
        types.Tool(
            name="get_combined_daily_data",
            description="Get all daily data (transport, finance, weather) in one call",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

# @server.list_tools()
# async def handle_list_tools() -> list[types.Tool]:
#     """List available tools"""
#     return [
#         types.Tool(
#             name="get_transport_data",
#             description="Get real-time TFL transport data including delays and service status"
#         ),
#         types.Tool(
#             name="get_financial_data", 
#             description="Get UK stock market data for major companies from Snowflake"
#         ),
#         types.Tool(
#             name="get_weather_data",
#             description="Get current London weather data"
#         ),
#         types.Tool(
#             name="get_financial_trends",
#             description="Get financial trend analysis and market insights"
#         ),
#         types.Tool(
#             name="get_combined_daily_data",
#             description="Get all daily data (transport, finance, weather) in one call"
#         )
#     ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_transport_data":
            data = await data_loader.load_transport_data()
            text = _format_transport_data(data)
            
        elif name == "get_financial_data":
            days_back = arguments.get("days_back", 7)
            data = await data_loader.load_financial_data_from_snowflake()
            text = _format_financial_data(data)
            
        elif name == "get_weather_data":
            data = await data_loader.load_weather_data()
            text = _format_weather_data(data)
            
        elif name == "get_financial_trends":
            data = await data_loader.load_financial_trend_data()
            trends = data_loader._process_financial_trends(data)
            text = _format_trend_data(trends)
            
        elif name == "get_combined_daily_data":
            transport_data = await data_loader.load_transport_data()
            financial_data = await data_loader.load_financial_data_from_snowflake()
            weather_data = await data_loader.load_weather_data()
            text = _create_daily_report(transport_data, financial_data, weather_data)
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
        return [types.TextContent(type="text", text=text)]
        
    except Exception as e:
        error_text = f"Error executing tool {name}: {str(e)}"
        return [types.TextContent(type="text", text=error_text)]

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources"""
    return [
        types.Resource(
            uri="tfl://lines/info",
            name="tfl-lines-info",
            description="Information about TFL tube lines and modes",
            mimeType="application/json"
        ),
        types.Resource(
            uri="finance://companies/list",
            name="financial-companies", 
            description="List of UK companies tracked in financial data",
            mimeType="application/json"
        ),
        types.Resource(
            uri="weather://london/metrics",
            name="weather-metrics",
            description="London weather measurement definitions",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> types.ResourceContents:
    """Handle resource reads"""
    if uri == "tfl://lines/info":
        content = json.dumps({
            "tube_lines": [
                "Victoria", "Central", "Jubilee", "Northern", "Piccadilly",
                "District", "Circle", "Bakerloo", "Metropolitan", "DLR"
            ],
            "modes": ["tube", "dlr", "overground"],
            "status_categories": [
                "Good Service", "Minor Delays", "Severe Delays", 
                "Part Suspended", "Special Service"
            ]
        }, indent=2)
        
    elif uri == "finance://companies/list":
        content = json.dumps({
            "tracked_companies": [
                {"symbol": "HSBA.L", "name": "HSBC Holdings", "sector": "Banking"},
                {"symbol": "BP.L", "name": "BP", "sector": "Energy"},
                {"symbol": "GSK.L", "name": "GSK", "sector": "Pharmaceuticals"},
                {"symbol": "ULVR.L", "name": "Unilever", "sector": "Consumer Goods"},
                {"symbol": "AZN.L", "name": "AstraZeneca", "sector": "Pharmaceuticals"},
                {"symbol": "RIO.L", "name": "Rio Tinto", "sector": "Mining"},
                {"symbol": "LLOY.L", "name": "Lloyds Banking Group", "sector": "Banking"},
                {"symbol": "BARC.L", "name": "Barclays", "sector": "Banking"}
            ]
        }, indent=2)
        
    elif uri == "weather://london/metrics":
        content = json.dumps({
            "weather_metrics": {
                "temperature": "Celsius",
                "humidity": "Percentage", 
                "precipitation": "mm",
                "weather_code": "WMO code for weather condition"
            },
            "location": "London, UK"
        }, indent=2)
        
    else:
        raise ValueError(f"Unknown resource: {uri}")
    
    return types.ResourceContents(
        contents=[types.TextContent(type="text", text=content)]
    )

# Formatting functions
def _format_transport_data(data: pd.DataFrame) -> str:
    if data.empty:
        return "No transport data available"
    
    output = ["🚇 TFL TRANSPORT STATUS", "=" * 50]
    for _, row in data.iterrows():
        status_emoji = "✅" if row.get('status') == 'Good Service' else "⚠️" if 'Minor' in str(row.get('status')) else "🔴"
        output.append(f"{status_emoji} {row.get('line_name', 'Unknown')}: {row.get('status', 'Unknown')}")
        if row.get('delay_minutes', 0) > 0:
            output.append(f"   ⏰ Delay: {row.get('delay_minutes')} minutes")
        output.append("")
    return "\n".join(output)

def _format_financial_data(data: pd.DataFrame) -> str:
    if data.empty:
        return "No financial data available"
    
    output = ["📊 UK STOCK MARKET DATA", "=" * 50]
    for _, row in data.iterrows():
        output.append(f"📈 {row.get('SYMBOL', 'Unknown')} ({row.get('COMPANY_NAME', 'Unknown')})")
        output.append(f"   💰 Close: £{row.get('CLOSE', 0):.2f}")
        output.append(f"   📊 Volume: {row.get('VOLUME', 0):,}")
        output.append("")
    return "\n".join(output)

def _format_weather_data(data: pd.DataFrame) -> str:
    if data.empty:
        return "No weather data available"
    
    row = data.iloc[0]
    output = ["🌤️ LONDON WEATHER", "=" * 50]
    output.append(f"🌡️ Temperature: {row.get('temperature', 0)}°C")
    output.append(f"💧 Humidity: {row.get('humidity', 0)}%")
    output.append(f"🌧️ Precipitation: {row.get('precipitation', 0)}mm")
    return "\n".join(output)

def _format_trend_data(trends: Dict[str, Any]) -> str:
    output = ["📈 FINANCIAL TREND ANALYSIS", "=" * 50]
    output.append("📊 PERFORMANCE METRICS:")
    for metric in trends.get('performance_metrics', []):
        output.append(f"   • {metric['name']}: {metric['value']}")
    output.append("\n🏆 TOP STOCKS:")
    for stock in trends.get('stock_performance', [])[:3]:
        output.append(f"   • {stock['symbol']}: {stock['company']}")
    return "\n".join(output)

def _create_daily_report(transport: pd.DataFrame, finance: pd.DataFrame, weather: pd.DataFrame) -> str:
    output = ["📅 DAILY LONDON DATA REPORT", "=" * 50]
    
    if not weather.empty:
        temp = weather.iloc[0].get('temperature', 0)
        output.append(f"\n🌤️ WEATHER: {temp}°C in London")
    
    if not transport.empty:
        good_service = len(transport[transport['status'] == 'Good Service'])
        total_lines = len(transport)
        output.append(f"\n🚇 TRANSPORT: {good_service}/{total_lines} lines with good service")
    
    if not finance.empty:
        output.append(f"\n📊 MARKETS: {len(finance)} stock records loaded")
    
    output.append(f"\n🕒 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(output)



async def main():
    """Main function to run the server"""
    logger.info("🚀 Starting TFL Finance Weather MCP Server...")
    
    # Test connections
    if data_loader.snowflake_conn:
        logger.info("✅ Snowflake connection active")
    else:
        logger.warning("⚠️ Snowflake connection not available")
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tfl-finance-weather",
                server_version="1.0.0",
                capabilities={
                    "tools": {},
                    "resources": {},
                    "roots": {}
                }
            )
        )

if __name__ == "__main__":
    asyncio.run(main())