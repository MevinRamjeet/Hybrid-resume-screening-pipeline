#!/usr/bin/env python3
"""
FastAPI Server Runner for Hybrid Resume Screening Pipeline

This script starts the FastAPI server for the hybrid resume screening pipeline.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from src.schema.api import HealthResponse

# Add the project root to the path



app = FastAPI(
    title="Hybrid Resume Screening Pipeline API",
    description="API for evaluating job applications using hybrid structured and unstructured analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


def main():
    """Run the FastAPI server"""
    print("=" * 60)
    print("HYBRID RESUME SCREENING PIPELINE - FastAPI SERVER")
    print("=" * 60)
    print("Starting server...")
    print("API Documentation will be available at: http://localhost:8000/docs")
    print("Alternative docs at: http://localhost:8000/redoc")
    print("Health check at: http://localhost:8000/health")
    print("=" * 60)

    # Run the server
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
