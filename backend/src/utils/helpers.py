import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List
import pandas as pd

async def async_retry(func, max_retries=3, delay=1):
    """Retry decorator for async functions"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff

def validate_timeframe(timeframe: str) -> bool:
    """Validate timeframe parameter"""
    valid_timeframes = ['1h', '24h', '7d', '30d', '90d', '1y']
    return timeframe in valid_timeframes

def sanitize_sector_name(sector: str) -> str:
    """Sanitize and normalize sector names"""
    sector_map = {
        'transport': 'transportation',
        'energy': 'energy',
        'finance': 'finance',
        'financial': 'finance',
        'weather': 'weather',
        'ecommerce': 'ecommerce',
        'social': 'social media'
    }
    return sector_map.get(sector.lower(), sector.lower())