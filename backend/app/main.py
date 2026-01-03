"""FastAPI application entry point"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.config import settings
from app.routers import health, budgets, expenses, summary, categories, monthly_budgets
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Home Finance Dashboard API",
    version="0.1.0",
    description="Backend API for home finance management"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_code": "VALIDATION_ERROR"}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions"""
    logger.warning(f"Value error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_code": "VALIDATION_ERROR"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(budgets.router, tags=["budgets"])
app.include_router(expenses.router, tags=["expenses"])
app.include_router(summary.router, tags=["summary"])
app.include_router(categories.router, tags=["categories"])
app.include_router(monthly_budgets.router, tags=["monthly_budgets"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Home Finance Dashboard API")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Timezone: {settings.timezone}")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Home Finance Dashboard API"}
