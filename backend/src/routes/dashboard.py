from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from services.dashboard_service import DashboardService
router = APIRouter()
logger = logging.getLogger(__name__)


# Create a dependency that will be injected at runtime
def get_dashboard_service() -> DashboardService:
    """Dependency injection for dashboard service"""
    # This will be overridden when we set up the dependency in main.py
    from main import app  # Import locally to avoid circular import
    return app.state.dashboard_service

@router.get("/", response_model=Dict[str, Any])
async def get_dashboard_overview(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get comprehensive dashboard overview"""
    try:
        overview = await dashboard_service.get_overview()
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "data": overview
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

@router.get("/sector/{sector}", response_model=Dict[str, Any])
async def get_sector_dashboard(
    sector: str,
    timeframe: str = Query("7d", regex="^(1h|24h|7d|30d|90d|1y)$"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get detailed dashboard for a specific sector"""
    try:
        # Validate sector
        valid_sectors = ['energy', 'transportation', 'finance', 'weather', 'ecommerce', 'social_media']  # Fixed hyphen to underscore
        if sector not in valid_sectors:
            raise HTTPException(status_code=400, detail=f"Invalid sector. Must be one of: {valid_sectors}")
        
        sector_data = await dashboard_service.get_sector_dashboard(sector, timeframe)
        
        return {
            "status": "success",
            "sector": sector,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat(),
            "data": sector_data
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching {sector} dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch {sector} data")

@router.get("/sectors", response_model=Dict[str, Any])
async def get_available_sectors():
    """Get list of available sectors"""
    sectors = [
        {
            "id": "transportation",
            "name": "Transportation",
            "description": "TFL transport data and delays",
            "endpoints": ["/api/dashboard/sector/transportation", "/api/data-sources/transportation"],
            "available_metrics": ["delays", "service_status"]
        },
        {
            "id": "finance",
            "name": "Finance",
            "description": "UK financial markets and stock data",
            "endpoints": ["/api/dashboard/sector/finance", "/api/data-sources/finance"],
            "available_metrics": ["stock_prices", "volume", "market_trend"]
        },
        {
            "id": "weather",
            "name": "Weather",
            "description": "UK weather data and forecasts",
            "endpoints": ["/api/dashboard/sector/weather", "/api/data-sources/weather"],
            "available_metrics": ["temperature", "humidity", "condition"]
        }
    ]
    return {
        "status": "success",
        "count": len(sectors),
        "sectors": sectors
    }

@router.get("/alerts", response_model=Dict[str, Any])
async def get_active_alerts(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get active alerts across all sectors"""
    try:
        # This would aggregate alerts from all sectors
        overview = await dashboard_service.get_overview()
        alerts = []
        if overview and isinstance(overview, dict):
            for sector, data in overview.items():
                if sector not in ['last_updated', 'summary'] and isinstance(data, dict):
                    sector_alerts = data.get('alerts', [])
                    for alert in sector_alerts:
                        if isinstance(alert, dict):
                            alert['sector'] = sector
                            alerts.append(alert)
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'warning': 2, 'info': 3}
        alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'info'), 3))
        
        return {
            "status": "success",
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.get('severity') == 'critical']),
            "alerts": alerts[:50]  # Limit to top 50 alerts
        }
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@router.get("/metrics", response_model=Dict[str, Any])
async def get_key_metrics(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get key business metrics across all sectors"""
    try:
        overview = await dashboard_service.get_overview()
        
        metrics = {
            "transportation": {
                "delay_percentage": overview.get('transportation', {}).get('delay_percentage', 0) if overview else 0,
                "major_issues": len(overview.get('transportation', {}).get('major_issues', [])) if overview else 0
            },
            "finance": {
                "ftse_change": overview.get('finance', {}).get('ftse_change', 0) if overview else 0,
                "market_trend": overview.get('finance', {}).get('trend', 'stable') if overview else 'stable'
            }
        }
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")