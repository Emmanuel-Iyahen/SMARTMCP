
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json

# Import modules
from modules.data_loader import DataLoaderModule
from modules.ai_analyzer import AIAnalyzerModule
from modules.visualization import VisualizationModule

# Import services
from services.dashboard_service import DashboardService
from services.prompt_service import PromptService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Response Models
class DashboardResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    last_updated: str

class FinancialTrendResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    last_updated: str

class SectorData(BaseModel):
    market_trend: Optional[str] = None
    average_change: Optional[float] = None
    advancing_stocks: Optional[int] = None
    declining_stocks: Optional[int] = None
    total_stocks: Optional[int] = None
    all_stocks: Optional[List[Dict[str, Any]]] = None
    top_gainers: Optional[List[Dict[str, Any]]] = None
    top_losers: Optional[List[Dict[str, Any]]] = None
    chart_data: Optional[List[Dict[str, Any]]] = None
    market_summary: Optional[str] = None
    alerts: Optional[List[Dict[str, Any]]] = None

class TrendData(BaseModel):
    market_trends: Optional[List[Dict[str, Any]]] = None
    performance_metrics: Optional[List[Dict[str, Any]]] = None
    trend_indicators: Optional[List[Dict[str, Any]]] = None
    stock_performance: Optional[List[Dict[str, Any]]] = None
    volatility_data: Optional[List[Dict[str, Any]]] = None
    moving_averages: Optional[List[Dict[str, Any]]] = None
    sector_performance: Optional[List[Dict[str, Any]]] = None
    sector_rankings: Optional[List[Dict[str, Any]]] = None

# MCP Authentication
security = HTTPBearer()
MCP_API_KEYS = ["mcp-secret-key-123", "your-mcp-api-key"]  # Move to environment variables in production

async def verify_mcp_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials not in MCP_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid MCP API key")
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing MCP Platform...")
    
    try:
        app.state.data_loader = DataLoaderModule()
        app.state.ai_analyzer = AIAnalyzerModule()
        app.state.visualization = VisualizationModule()
        app.state.dashboard_service = DashboardService(
            app.state.data_loader,
            app.state.ai_analyzer,
            app.state.visualization
        )
        app.state.prompt_service = PromptService(
            app.state.ai_analyzer,
            app.state.data_loader
        )
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCP Platform...")
    try:
        await app.state.data_loader.close()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Universal MCP Platform",
    description="Domain-Agnostic Multi-Sector Data Analysis Platform with MCP Support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Import routers AFTER app is created to avoid circular imports
from routes.dashboard import router as dashboard_router
from routes.prompts import router as prompts_router
from routes.data_sources import router as data_sources_router

# Include routers
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(prompts_router, prefix="/api/prompts", tags=["prompts"])
app.include_router(data_sources_router, prefix="/api/data-sources", tags=["data-sources"])

# ==================== MCP DISCOVERY & ENDPOINTS ====================

@app.get("/.well-known/mcp.json")
async def mcp_discovery():
    """MCP service discovery endpoint - accessible without authentication"""
    return {
        "name": "UK Data MCP Server",
        "description": "TFL transport, UK stock market, and London weather data",
        "version": "1.0.0",
        "endpoints": {
            "tools": "/mcp/tools",
            "resources": "/mcp/resources", 
            "execute": "/mcp/tools/{tool_name}",
            "read": "/mcp/resources/{resource_uri}"
        },
        "capabilities": ["tools", "resources"],
        "authentication": "bearer_token"
    }

@app.get("/mcp/tools")
async def list_mcp_tools(api_key: str = Depends(verify_mcp_api_key)):
    """List available MCP tools"""
    try:
        tools = [
            {
                "name": "get_transport_data",
                "description": "Get real-time TFL transport data including delays and service status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_financial_data", 
                "description": "Get UK stock market data for major companies from Snowflake",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "days_back": {
                            "type": "number",
                            "description": "Number of days of historical data to retrieve",
                            "default": 7
                        }
                    }
                }
            },
            {
                "name": "get_weather_data",
                "description": "Get current London weather data", 
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_financial_trends",
                "description": "Get financial trend analysis and market insights",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "period_days": {
                            "type": "number",
                            "description": "Analysis period in days", 
                            "default": 30
                        }
                    }
                }
            },
            {
                "name": "get_combined_daily_data",
                "description": "Get all daily data (transport, finance, weather) in one call",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")

@app.post("/mcp/tools/{tool_name}")
async def execute_mcp_tool(tool_name: str, arguments: dict = {}, api_key: str = Depends(verify_mcp_api_key)):
    """Execute an MCP tool"""
    try:
        data_loader = app.state.data_loader
        
        if tool_name == "get_transport_data":
            data = await data_loader.load_transport_data()
            result = _format_mcp_transport_data(data)
            
        elif tool_name == "get_financial_data":
            days_back = arguments.get("days_back", 7)
            data = await data_loader.load_financial_data_from_snowflake()
            result = _format_mcp_financial_data(data)
            
        elif tool_name == "get_weather_data":
            data = await data_loader.load_weather_data()
            result = _format_mcp_weather_data(data)
            
        elif tool_name == "get_financial_trends":
            data = await data_loader.load_financial_trend_data()
            trends = data_loader._process_financial_trends(data)
            result = _format_mcp_trend_data(trends)
            
        elif tool_name == "get_combined_daily_data":
            transport_data = await data_loader.load_transport_data()
            financial_data = await data_loader.load_financial_data_from_snowflake()
            weather_data = await data_loader.load_weather_data()
            result = _create_mcp_daily_report(transport_data, financial_data, weather_data)
            
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
            
        return {
            "content": [
                {
                    "type": "text",
                    "text": result
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool {tool_name}: {str(e)}")

@app.get("/mcp/resources")
async def list_mcp_resources(api_key: str = Depends(verify_mcp_api_key)):
    """List available MCP resources"""
    resources = [
        {
            "uri": "tfl://lines/info",
            "name": "tfl-lines-info", 
            "description": "Information about TFL tube lines and modes",
            "mimeType": "application/json"
        },
        {
            "uri": "finance://companies/list",
            "name": "financial-companies",
            "description": "List of UK companies tracked in financial data", 
            "mimeType": "application/json"
        },
        {
            "uri": "weather://london/metrics", 
            "name": "weather-metrics",
            "description": "London weather measurement definitions",
            "mimeType": "application/json"
        }
    ]
    return {"resources": resources}

@app.get("/mcp/resources/{resource_uri:path}")
async def read_mcp_resource(resource_uri: str, api_key: str = Depends(verify_mcp_api_key)):
    """Read an MCP resource"""
    try:
        if resource_uri == "tfl://lines/info":
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
            
        elif resource_uri == "finance://companies/list":
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
            
        elif resource_uri == "weather://london/metrics":
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
            raise HTTPException(status_code=404, detail=f"Unknown resource: {resource_uri}")
        
        return {
            "contents": [
                {
                    "uri": resource_uri,
                    "mimeType": "application/json",
                    "text": content
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading resource: {str(e)}")

# ==================== MCP FORMATTING FUNCTIONS ====================

def _format_mcp_transport_data(data) -> str:
    """Format transport data for MCP response"""
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

def _format_mcp_financial_data(data) -> str:
    """Format financial data for MCP response"""
    if data.empty:
        return "No financial data available"
    
    output = ["📊 UK STOCK MARKET DATA", "=" * 50]
    for _, row in data.iterrows():
        output.append(f"📈 {row.get('SYMBOL', 'Unknown')} ({row.get('COMPANY_NAME', 'Unknown')})")
        output.append(f"   💰 Close: £{row.get('CLOSE', 0):.2f}")
        output.append(f"   📊 Volume: {row.get('VOLUME', 0):,}")
        output.append("")
    return "\n".join(output)

def _format_mcp_weather_data(data) -> str:
    """Format weather data for MCP response"""
    if data.empty:
        return "No weather data available"
    
    row = data.iloc[0]
    output = ["🌤️ LONDON WEATHER", "=" * 50]
    output.append(f"🌡️ Temperature: {row.get('temperature', 0)}°C")
    output.append(f"💧 Humidity: {row.get('humidity', 0)}%")
    output.append(f"🌧️ Precipitation: {row.get('precipitation', 0)}mm")
    return "\n".join(output)

def _format_mcp_trend_data(trends: dict) -> str:
    """Format trend data for MCP response"""
    output = ["📈 FINANCIAL TREND ANALYSIS", "=" * 50]
    output.append("📊 PERFORMANCE METRICS:")
    for metric in trends.get('performance_metrics', []):
        output.append(f"   • {metric['name']}: {metric['value']}")
    output.append("\n🏆 TOP STOCKS:")
    for stock in trends.get('stock_performance', [])[:3]:
        output.append(f"   • {stock['symbol']}: {stock['company']}")
    return "\n".join(output)

def _create_mcp_daily_report(transport, finance, weather) -> str:
    """Create daily report for MCP response"""
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

# ==================== EXISTING ENDPOINTS (UPDATED) ====================

@app.get("/")
async def root():
    return {
        "message": "Universal MCP Platform API with MCP Support",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_discovery": "/.well-known/mcp.json"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        # Basic health check
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "healthy",
                "data_loader": "initialized",
                "ai_analyzer": "initialized",
                "mcp": "enabled"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Universal MCP Platform",
        "version": "1.0.0",
        "description": "Domain-Agnostic Multi-Sector Data Analysis Platform with MCP Support",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "prompts": "/api/prompts", 
            "data_sources": "/api/data-sources",
            "health": "/health",
            "docs": "/docs",
            "mcp_discovery": "/.well-known/mcp.json",
            "mcp_tools": "/mcp/tools",
            "mcp_resources": "/mcp/resources"
        },
        "sectors": ["energy", "transportation", "finance", "weather", "ecommerce", "social_media"],
        "mcp_support": True
    }





import os
import pandas as pd
import snowflake.connector


def init_snowflake():
        """Initialize Snowflake connection with environment variables"""
        try:
            user = os.getenv("user")
            password = os.getenv("password")
            account = os.getenv("account")
            warehouse = os.getenv("warehouse")
            database = os.getenv("database")
            schema = os.getenv("schema")

            if not all([user, password, account]):
                logger.warning("⚠️ Missing Snowflake credentials in environment variables.")
                return None
            
            #logger.info(f"🔧 Connecting to Snowflake as {user}@{account} [{database}.{schema}]...")

            conn = snowflake.connector.connect(
                user=user,
                password=password,
                account=account,
                warehouse=warehouse,
                database=database,
                schema=schema
            )
            logger.info("✅ Successfully connected to Snowflake.")
            return conn

        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return None





@app.get("/api/stock-forecasts")
async def get_stock_forecasts(symbol: str = None, days: int = 7):
    """Get stock forecasts from Snowflake"""
    try:
        conn = init_snowflake()
        cursor = conn.cursor()
        
        if symbol:
            query = """
            SELECT * FROM STOCK_FORECASTS 
            WHERE SYMBOL = %s 
            AND FORECAST_DATE >= CURRENT_DATE()
            ORDER BY FORECAST_DATE
            LIMIT %s
            """
            cursor.execute(query, (symbol, days * 10))  # Buffer for multiple symbols
        else:
            query = """
            SELECT * FROM STOCK_FORECASTS 
            WHERE GENERATED_AT = (
                SELECT MAX(GENERATED_AT) FROM STOCK_FORECASTS
            )
            AND FORECAST_DATE >= CURRENT_DATE()
            ORDER BY SYMBOL, FORECAST_DATE
            """
            cursor.execute(query)
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        df = pd.DataFrame(results, columns=columns)
        
        # Convert to structured format
        forecasts = {}
        for symbol in df['SYMBOL'].unique():
            symbol_data = df[df['SYMBOL'] == symbol]
            forecasts[symbol] = {
                'forecasts': symbol_data[[
                    'FORECAST_DATE', 'FORECAST_PRICE', 
                    'CONFIDENCE_LOWER', 'CONFIDENCE_UPPER'
                ]].to_dict('records'),
                'last_updated': symbol_data['GENERATED_AT'].iloc[0]
            }
        
        return {
            "status": "success",
            "data": forecasts,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecasts: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()





@app.get("/api/trading-signals")
async def get_trading_signals():
    """Get latest trading signals from Snowflake"""
    try:
        conn = init_snowflake()
        cursor = conn.cursor()
        
        query = """
        SELECT * FROM TRADING_SIGNALS 
        WHERE GENERATED_AT = (
            SELECT MAX(GENERATED_AT) FROM TRADING_SIGNALS
        )
        ORDER BY 
            CASE SIGNAL 
                WHEN 'STRONG_BUY' THEN 1
                WHEN 'BUY' THEN 2
                WHEN 'HOLD' THEN 3
                WHEN 'SELL' THEN 4
                WHEN 'STRONG_SELL' THEN 5
                ELSE 6
            END,
            ABS(NEXT_DAY_CHANGE_PCT) DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        signals = pd.DataFrame(results, columns=columns).to_dict('records')
        
        return {
            "status": "success",
            "data": signals,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching signals: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()





@app.get("/api/forecast-summary")
async def get_forecast_summary():
    """Get forecast summary statistics"""
    try:
        conn = init_snowflake()
        cursor = conn.cursor()
        
        # Get signal distribution
        query = """
        SELECT 
            SIGNAL,
            COUNT(*) as count,
            AVG(NEXT_DAY_CHANGE_PCT) as avg_next_day_change,
            AVG(SEVEN_DAY_CHANGE_PCT) as avg_seven_day_change
        FROM TRADING_SIGNALS 
        WHERE GENERATED_AT = (
            SELECT MAX(GENERATED_AT) FROM TRADING_SIGNALS
        )
        GROUP BY SIGNAL
        """
        
        cursor.execute(query)
        signal_stats = cursor.fetchall()
        
        # Get trend distribution
        trend_query = """
        SELECT 
            TREND,
            COUNT(*) as count
        FROM TRADING_SIGNALS 
        WHERE GENERATED_AT = (
            SELECT MAX(GENERATED_AT) FROM TRADING_SIGNALS
        )
        GROUP BY TREND
        """
        
        cursor.execute(trend_query)
        trend_stats = cursor.fetchall()
        
        return {
            "status": "success",
            "data": {
                "signal_distribution": [
                    {"signal": row[0], "count": row[1], "avg_next_day": row[2], "avg_seven_day": row[3]}
                    for row in signal_stats
                ],
                "trend_distribution": [
                    {"trend": row[0], "count": row[1]}
                    for row in trend_stats
                ],
                "total_stocks": sum(row[1] for row in signal_stats),
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()










# Add the missing financial trends endpoint with proper error handling
@app.get("/api/financial-trends", response_model=FinancialTrendResponse)
async def get_financial_trends(request: Request):
    """Get financial trend analysis (separate from daily overview)"""
    try:
        data_loader = request.app.state.data_loader
        
        # Default fallback data structure
        default_trend_data = {
            'market_trends': [],
            'performance_metrics': [
                {'name': '30-Day Return', 'value': '+0.00%'},
                {'name': 'Avg Daily Return', 'value': '+0.00%'},
                {'name': 'Volatility', 'value': '0.00%'}
            ],
            'trend_indicators': [
                {'name': 'Market Trend', 'status': 'Neutral'}
            ],
            'stock_performance': [],
            'volatility_data': [],
            'moving_averages': [],
            'sector_performance': [],
            'sector_rankings': []
        }
        
        # Check if the dashboard service has the trend methods
        if hasattr(data_loader, 'load_financial_trend_data') and hasattr(data_loader, '_process_financial_trends'):
            try:
                trend_data = await data_loader.load_financial_trend_data()
                processed_trends = data_loader._process_financial_trends(trend_data)
                
                # Ensure processed_trends is not None and has the required structure
                if processed_trends is None:
                    logger.warning("Processed trends returned None, using default data")
                    processed_trends = default_trend_data
                else:
                    # Ensure all required fields exist
                    for key in default_trend_data.keys():
                        if key not in processed_trends:
                            processed_trends[key] = default_trend_data[key]
                            logger.warning(f"Missing key '{key}' in trend data, using default")
                            
            except Exception as e:
                logger.error(f"Error processing trend data: {e}")
                processed_trends = default_trend_data
        else:
            # If methods don't exist, try to use sample data
            logger.warning("Trend methods not available, trying sample data")
            try:
                if hasattr(data_loader, '_get_sample_trend_analysis'):
                    processed_trends = data_loader._get_sample_trend_analysis()
                    if processed_trends is None:
                        processed_trends = default_trend_data
                else:
                    processed_trends = default_trend_data
            except Exception as e:
                logger.error(f"Error getting sample trend data: {e}")
                processed_trends = default_trend_data
        
        # Final validation - ensure we have a valid dictionary
        if not isinstance(processed_trends, dict):
            logger.error(f"Processed trends is not a dict: {type(processed_trends)}")
            processed_trends = default_trend_data
        
        response_data = {
            "status": "success",
            "data": processed_trends,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Successfully returning trend data with keys: {list(processed_trends.keys())}")
        return response_data
        
    except Exception as e:
        logger.error(f"Unexpected error in financial trends endpoint: {e}")
        # Return valid response even in error
        return {
            "status": "error",
            "data": {
                'market_trends': [],
                'performance_metrics': [{'name': 'Error', 'value': 'Data unavailable'}],
                'trend_indicators': [{'name': 'System', 'status': 'Error'}],
                'stock_performance': [],
                'volatility_data': [],
                'moving_averages': [],
                'sector_performance': [],
                'sector_rankings': []
            },
            "last_updated": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )