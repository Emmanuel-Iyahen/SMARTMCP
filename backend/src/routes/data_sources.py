

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from modules.data_loader import DataLoaderModule

router = APIRouter()
logger = logging.getLogger(__name__)

def get_data_loader() -> DataLoaderModule:
    """Dependency injection for data loader"""
    from main import app  # Import locally to avoid circular import
    return app.state.data_loader

@router.get("/", response_model=Dict[str, Any])
async def get_available_data_sources():
    """Get list of available data sources"""
    data_sources = [
        {
            "id": "energy",
            "name": "UK Energy Data",
            "description": "Real-time energy pricing and consumption data",
            "provider": "National Grid ESO",
            "update_frequency": "15 minutes",
            "endpoints": [
                "/api/data-sources/energy/latest",
                "/api/data-sources/energy/historical"
            ],
            "available_from": "2020-01-01",
            "fields": ["timestamp", "price", "energy_type", "region", "demand"]
        },
        {
            "id": "transportation",
            "name": "Transport for London (TFL) Data",
            "description": "Real-time transport status and delays",
            "provider": "Transport for London",
            "update_frequency": "30 seconds",
            "endpoints": [
                "/api/data-sources/transportation/status",
                "/api/data-sources/transportation/delays"
            ],
            "available_from": "2023-01-01",
            "fields": ["timestamp", "line_name", "status", "delay_minutes", "reason"]
        },
        {
            "id": "finance",
            "name": "UK Financial Markets",
            "description": "Stock prices and market data",
            "provider": "London Stock Exchange",
            "update_frequency": "1 minute",
            "endpoints": [
                "/api/data-sources/finance/prices",
                "/api/data-sources/finance/indices"
            ],
            "available_from": "2022-01-01",
            "fields": ["timestamp", "symbol", "price", "volume", "change"]
        },
        {
            "id": "weather",
            "name": "UK Weather Data",
            "description": "Weather conditions and forecasts",
            "provider": "Met Office",
            "update_frequency": "1 hour",
            "endpoints": [
                "/api/data-sources/weather/current",
                "/api/data-sources/weather/forecast"
            ],
            "available_from": "2023-06-01",
            "fields": ["timestamp", "temperature", "precipitation", "wind_speed", "condition"]
        }
    ]
    
    return {
        "status": "success",
        "count": len(data_sources),
        "data_sources": data_sources
    }

@router.get("/{source_id}/latest", response_model=Dict[str, Any])
async def get_latest_data(
    source_id: str,
    data_loader: DataLoaderModule = Depends(get_data_loader)
):
    """Get latest data from a specific source"""
    try:
        if source_id == "energy":
            data = await data_loader.load_uk_energy_data()
        elif source_id == "transportation":
            data = await data_loader.load_transport_data()
        elif source_id == "finance":
            data = await data_loader.load_financial_data()
        elif source_id == "weather":
            data = await data_loader.load_weather_data()
        else:
            raise HTTPException(status_code=404, detail=f"Data source '{source_id}' not found")
        
        # Convert to list for JSON serialization
        if hasattr(data, 'to_dict'):
            records = data.tail(10).to_dict('records')  # Last 10 records
        else:
            records = data[-10:] if isinstance(data, list) else [data]
        
        return {
            "status": "success",
            "source": source_id,
            "record_count": len(records),
            "last_updated": datetime.utcnow().isoformat(),
            "data": records
        }
    except Exception as e:
        logger.error(f"Error fetching latest {source_id} data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch {source_id} data")

@router.get("/{source_id}/historical", response_model=Dict[str, Any])
async def get_historical_data(
    source_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    data_loader: DataLoaderModule = Depends(get_data_loader)
):
    """Get historical data for a specific source and date range"""
    try:
        # Validate dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        if (end - start).days > 365:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 1 year")
        
        # Placeholder implementation
        return {
            "status": "success",
            "source": source_id,
            "start_date": start_date,
            "end_date": end_date,
            "message": f"Historical data for {source_id} from {start_date} to {end_date}",
            "record_count": 0,
            "data_available": True
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error fetching historical {source_id} data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch historical {source_id} data")

@router.get("/{source_id}/status", response_model=Dict[str, Any])
async def get_data_source_status(source_id: str):
    """Get status and health of a data source"""
    status_info = {
        "energy": {
            "status": "active",
            "last_successful_update": datetime.utcnow().isoformat(),
            "update_frequency": "15 minutes",
            "data_freshness": "current",
            "issues": []
        },
        "transportation": {
            "status": "active",
            "last_successful_update": datetime.utcnow().isoformat(),
            "update_frequency": "30 seconds",
            "data_freshness": "current",
            "issues": []
        },
        "finance": {
            "status": "active",
            "last_successful_update": datetime.utcnow().isoformat(),
            "update_frequency": "1 minute",
            "data_freshness": "current",
            "issues": []
        }
    }
    
    if source_id not in status_info:
        raise HTTPException(status_code=404, detail=f"Status information not available for {source_id}")
    
    return {
        "status": "success",
        "source": source_id,
        "health": status_info[source_id]
    }