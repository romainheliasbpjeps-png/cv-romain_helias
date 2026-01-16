"""
FastAPI Application Entry Point

Professional production-ready API with:
- CORS configuration
- Error handling
- Logging
- API documentation
- Health checks
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import get_settings
from .api import router
from .utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Create necessary directories
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    Professional PDF to JSON converter with advanced extraction capabilities.

    ## Features
    - **Native text extraction** using PyMuPDF
    - **Table detection** using pdfplumber
    - **OCR support** with Tesseract for scanned documents
    - **Multiple extraction profiles** (fast, balanced, accurate)
    - **Page range selection**
    - **Complete metadata** and traceability

    ## Extraction Profiles
    - **Fast**: Quick extraction, native text only
    - **Balanced**: Native text + table detection + auto OCR
    - **Accurate**: High-quality extraction with forced OCR

    ## Supported Languages
    - French (fra)
    - English (eng)
    - Spanish (spa)
    - German (deu)
    - Italian (ita)
    - Portuguese (por)
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred"
        }
    )


# Include routers
app.include_router(
    router,
    prefix=settings.api_v1_prefix,
    tags=["PDF Extraction"]
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": f"{settings.api_v1_prefix}/docs" if settings.debug else None,
        "endpoints": {
            "extract": f"{settings.api_v1_prefix}/extract",
            "schema": f"{settings.api_v1_prefix}/schema",
            "health": f"{settings.api_v1_prefix}/health",
        }
    }


@app.get("/ping", tags=["Health"])
async def ping():
    """Simple ping endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
