#!/usr/bin/env python3
"""
FastAPI Server Runner for Hybrid Resume Screening Pipeline

This script starts the FastAPI server for the hybrid resume screening pipeline.
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from src.schema.api import HealthResponse
from src.api.routes import router
from src.utils.logger import configured_logger
from src.config.system import cfg


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    print("=" * 60)
    configured_logger.info("Starting Hybrid Resume Screening Pipeline API")
    configured_logger.info(f"API Version: {cfg.api_version}")
    configured_logger.info(f"Environment: {getattr(cfg, 'environment', 'development')}")
    
    # Initialize any required services here
    try:
        # Test LLM configuration
        if cfg.openai_api_key:
            configured_logger.info("OpenAI API key configured")
        else:
            configured_logger.warning("OpenAI API key not configured - LLM evaluation may use mock responses")
        
        # Test HuggingFace configuration
        if cfg.hf_token:
            configured_logger.info("HuggingFace token configured")
        else:
            configured_logger.warning("HuggingFace token not configured - some models may not be available")
        
        configured_logger.info("Application startup completed successfully")
        
    except Exception as e:
        configured_logger.error(f"Error during startup: {e}")
        raise

    print("=" * 60)

    
    yield  # Application runs here
    print("=" * 60)

    # Shutdown
    configured_logger.info("Shutting down Hybrid Resume Screening Pipeline API")
    
    # Cleanup any resources here
    try:
        # Add any cleanup logic here (close database connections, etc.)
        configured_logger.info("Application shutdown completed successfully")
        
    except Exception as e:
        configured_logger.error(f"Error during shutdown: {e}")

    print("=" * 60)


app = FastAPI(
    title="Hybrid Resume Screening Pipeline API",
    description="API for evaluating job applications using hybrid structured and unstructured analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )
