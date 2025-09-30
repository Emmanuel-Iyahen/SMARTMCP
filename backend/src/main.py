# # from fastapi import FastAPI, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.staticfiles import StaticFiles
# # from contextlib import asynccontextmanager
# # import uvicorn

# # from modules.data_loader import DataLoaderModule
# # from modules.ai_analyzer import AIAnalyzerModule
# # from modules.visualization import VisualizationModule
# # from services.dashboard_service import DashboardService
# # from services.prompt_service import PromptService


# # @asynccontextmanager
# # async def lifespan(app: FastAPI):
# #     # Startup
# #     app.state.data_loader = DataLoaderModule()
# #     app.state.ai_analyzer = AIAnalyzerModule()
# #     app.state.visualization = VisualizationModule()
# #     app.state.dashboard_service = DashboardService(
# #         app.state.data_loader,
# #         app.state.ai_analyzer,
# #         app.state.visualization
# #     )
# #     app.state.prompt_service = PromptService(
# #         app.state.ai_analyzer,
# #         app.state.data_loader
# #     )
# #     yield
# #     # Shutdown
# #     await app.state.data_loader.close()

# # app = FastAPI(title="Universal MCP Platform", lifespan=lifespan)

# # # CORS middleware
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # Include routers
# # from routes import dashboard, prompts, data_sources
# # app.include_router(dashboard.router, prefix="/api/dashboard")
# # app.include_router(prompts.router, prefix="/api/prompts")
# # app.include_router(data_sources.router, prefix="/api/data-sources")


# # @app.get("/")
# # async def root():
# #     return {"message": "Universal MCP Platform API"}

# # if __name__ == "__main__":
# #     uvicorn.run(app, host="0.0.0.0", port=8000)




# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
# from contextlib import asynccontextmanager
# import uvicorn
# import logging
# from datetime import datetime

# # Import modules
# from modules.data_loader import DataLoaderModule
# from modules.ai_analyzer import AIAnalyzerModule
# from modules.visualization import VisualizationModule

# # Import services
# from services.dashboard_service import DashboardService
# from services.prompt_service import PromptService

# # Import routers
# from routes.dashboard import router as dashboard_router
# from routes.prompts import router as prompts_router
# from routes.data_sources import router as data_sources_router

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     logger.info("Initializing MCP Platform...")
    
#     try:
#         app.state.data_loader = DataLoaderModule()
#         app.state.ai_analyzer = AIAnalyzerModule()
#         app.state.visualization = VisualizationModule()
#         app.state.dashboard_service = DashboardService(
#             app.state.data_loader,
#             app.state.ai_analyzer,
#             app.state.visualization
#         )
#         app.state.prompt_service = PromptService(
#             app.state.ai_analyzer,
#             app.state.data_loader
#         )
#         logger.info("All services initialized successfully")
#     except Exception as e:
#         logger.error(f"Failed to initialize services: {e}")
#         raise
    
#     yield
    
#     # Shutdown
#     logger.info("Shutting down MCP Platform...")
#     try:
#         await app.state.data_loader.close()
#     except Exception as e:
#         logger.error(f"Error during shutdown: {e}")

# app = FastAPI(
#     title="Universal MCP Platform",
#     description="Domain-Agnostic Multi-Sector Data Analysis Platform",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, restrict to your frontend domains
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # GZip compression for better performance
# app.add_middleware(GZipMiddleware, minimum_size=1000)

# # Include routers
# app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
# app.include_router(prompts_router, prefix="/api/prompts", tags=["prompts"])
# app.include_router(data_sources_router, prefix="/api/data-sources", tags=["data-sources"])

# @app.get("/")
# async def root():
#     return {
#         "message": "Universal MCP Platform API",
#         "version": "1.0.0",
#         "status": "operational",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint for load balancers and monitoring"""
#     try:
#         # Basic health check - you can add more sophisticated checks here
#         return {
#             "status": "healthy",
#             "timestamp": datetime.utcnow().isoformat(),
#             "services": {
#                 "api": "healthy",
#                 "data_loader": "initialized",
#                 "ai_analyzer": "initialized"
#             }
#         }
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         raise HTTPException(status_code=503, detail="Service unhealthy")

# @app.get("/info")
# async def api_info():
#     """API information endpoint"""
#     return {
#         "name": "Universal MCP Platform",
#         "version": "1.0.0",
#         "description": "Domain-Agnostic Multi-Sector Data Analysis Platform",
#         "endpoints": {
#             "dashboard": "/api/dashboard",
#             "prompts": "/api/prompts", 
#             "data_sources": "/api/data-sources",
#             "health": "/health",
#             "docs": "/docs"
#         },
#         "sectors": ["energy", "transportation", "finance", "weather", "ecommerce", "social_media"]
#     }

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,  # Enable auto-reload in development
#         log_level="info"
#     )




from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime

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
    description="Domain-Agnostic Multi-Sector Data Analysis Platform",
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

@app.get("/")
async def root():
    return {
        "message": "Universal MCP Platform API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
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
                "ai_analyzer": "initialized"
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
        "description": "Domain-Agnostic Multi-Sector Data Analysis Platform",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "prompts": "/api/prompts", 
            "data_sources": "/api/data-sources",
            "health": "/health",
            "docs": "/docs"
        },
        "sectors": ["energy", "transportation", "finance", "weather", "ecommerce", "social_media"]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )