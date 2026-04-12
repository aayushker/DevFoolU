"""
FastAPI Backend for DevFoolU Project Recommendation System
Handles single URL scraping, bulk scraping, embedding generation, and similarity search
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional
import asyncio

from routers import scraper, similarity, bulk, auth
from core.config import settings
from core.logger import setup_logging
from services.mongodb import mongodb_client
from services.embedding import embedding_service
from services.mass_ingestor import mass_ingestor_service

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI application"""
    # Startup
    logger.info("Starting DevFoolU API Server...")
    
    # Connect to MongoDB
    try:
        await mongodb_client.connect()
        logger.info("✅ MongoDB connected successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    
    # Initialize embedding model
    try:
        await embedding_service.initialize()
        logger.info("✅ Embedding model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load embedding model: {e}")
        raise

    # Optionally start mass ingestion in background
    try:
        startup_ingest = await mass_ingestor_service.start_on_startup_if_enabled()
        if startup_ingest and startup_ingest.get("started"):
            logger.info(
                "✅ Mass ingest job started on startup (job_id=%s)",
                startup_ingest.get("job_id"),
            )
    except Exception as e:
        logger.error(f"❌ Failed to start mass ingest on startup: {e}")
    
    logger.info("🚀 Server started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down DevFoolU API Server...")
    try:
        await mass_ingestor_service.stop()
    except Exception as e:
        logger.warning(f"Failed to stop mass ingest cleanly: {e}")
    await mongodb_client.close()
    logger.info("✅ MongoDB connection closed")
    logger.info("👋 Server shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="DevFoolU API",
    description="Project recommendation system with web scraping and vector similarity search",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["Scraper"])
app.include_router(similarity.router, prefix="/api/similarity", tags=["Similarity Search"])
app.include_router(bulk.router, prefix="/api/bulk", tags=["Bulk Operations"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "DevFoolU API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "scrape_single": "/api/scraper/scrape",
            "find_similar": "/api/similarity/search",
            "bulk_scrape": "/api/bulk/scrape",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "mongodb": "unknown",
        "embedding_model": "unknown"
    }
    
    # Check MongoDB connection
    try:
        await mongodb_client.ping()
        health_status["mongodb"] = "connected"
    except Exception as e:
        health_status["mongodb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check embedding model
    try:
        if embedding_service.is_ready():
            health_status["embedding_model"] = "loaded"
        else:
            health_status["embedding_model"] = "not loaded"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["embedding_model"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
