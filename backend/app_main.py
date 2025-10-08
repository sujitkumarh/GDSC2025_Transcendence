#!/usr/bin/env python3
"""
# 🌱 Transcendence - Green Agents of Change

A sophisticated multi-agent orchestrator that empowers Brazilian youth to explore
green jobs and learning opportunities through intelligent, empathetic guidance.

## Features
- Persona-driven career guidance and skill assessment
- Green job discovery and pathway recommendations
- Multi-agent orchestration with safety guardrails
- Real-time analytics and engagement tracking
- Comprehensive Brazilian youth support ecosystem

"""
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from loguru import logger

# Import API routes
from app.api.v1.personas import router as personas_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.learning import router as learning_router
from app.api.v1.recommendations import router as recommendations_router

# Import core configuration
from app.core.config import settings
from app.core.logging import setup_logging
from app.telemetry.events import EventLogger

# Load environment variables
load_dotenv()

# Global instances
event_logger = EventLogger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("🌱 Starting Transcendence - Green Agents of Change")
    logger.info(f"🔧 Mock Mode: {settings.MOCK_MODE}")
    logger.info(f"🌍 CORS Origins: {settings.CORS_ORIGINS}")
    
    # Initialize services
    await event_logger.initialize()
    
    # Log startup event
    await event_logger.log_event("system_startup", {
        "mock_mode": settings.MOCK_MODE,
        "debug": settings.DEBUG,
        "version": "1.0.0"
    })
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Transcendence")
    await event_logger.log_event("system_shutdown", {})
    await event_logger.close()

# Create FastAPI application
app = FastAPI(
    title="Transcendence - Green Agents of Change",
    description="AI-powered assistant ecosystem for Brazilian youth green job exploration",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(personas_router, prefix="/v1/personas", tags=["personas"])
app.include_router(assistant_router, prefix="/v1/assistant", tags=["assistant"])
app.include_router(analytics_router, prefix="/v1/analytics", tags=["analytics"])
app.include_router(learning_router, prefix="/v1/learning", tags=["learning"])
app.include_router(recommendations_router, prefix="/v1/recommendations", tags=["recommendations"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Transcendence - Green Agents of Change",
        "version": "1.0.0",
        "description": "AI-powered assistant ecosystem for Brazilian youth green job exploration",
        "challenge": "2025 Capgemini Global Data Science Challenge",
        "status": "active",
        "mock_mode": settings.MOCK_MODE,
        "endpoints": {
            "personas": "/v1/personas",
            "assistant": "/v1/assistant",
            "analytics": "/v1/analytics",
            "learning": "/v1/learning",
            "recommendations": "/v1/recommendations",
            "docs": "/docs" if settings.DEBUG else "disabled",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "mock_mode": settings.MOCK_MODE,
            "services": {
                "api": "operational",
                "agents": "operational",
                "data": "operational",
                "analytics": "operational"
            }
        }
        
        # Log health check
        await event_logger.log_event("health_check", {
            "status": "healthy",
            "mock_mode": settings.MOCK_MODE
        })
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}")
    
    # Log error event
    await event_logger.log_event("error", {
        "type": "unhandled_exception",
        "message": str(exc),
        "path": str(request.url.path)
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "type": "internal_error"
        }
    )

# Setup logging
setup_logging()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )