"""
FastAPI application main file.
Entry point for the ANPR backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.routes import router
from src.database import init_db
from utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="ANPR System API",
    description="Automatic Number Plate Recognition System API",
    version="1.0.0"
)

# Configure CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["anpr"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("ANPR API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ANPR System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
