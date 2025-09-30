from .dashboard import router as dashboard_router
from .prompts import router as prompts_router
from .data_sources import router as data_sources_router

__all__ = ['dashboard_router', 'prompts_router', 'data_sources_router']