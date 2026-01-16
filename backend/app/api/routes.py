"""
API Routes for PDF extraction
RESTful endpoints with proper error handling and validation
"""
import logging
from pathlib import Path
from typing import Optional
import aiofiles
import secrets

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    status,
    Form,
    Depends
)
from fastapi.responses import JSONResponse

from ..models.extraction import (
    ExtractionRequest,
    ExtractionResponse,
    ExtractionResult,
    ExtractionProfile,
    OCRMode
)
from ..services import PDFExtractorService
from ..config import get_settings, Settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_extractor_service() -> PDFExtractorService:
    """Dependency injection for PDF extractor service"""
    return PDFExtractorService()


async def save_upload_file(upload_file: UploadFile, settings: Settings) -> Path:
    """Save uploaded file to temporary directory"""
    # Generate unique filename
    file_ext = Path(upload_file.filename).suffix
    unique_filename = f"{secrets.token_hex(16)}{file_ext}"
    file_path = settings.temp_dir / unique_filename

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)

    return file_path


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract structured data from PDF",
    description="Upload a PDF file and extract its content as structured JSON"
)
async def extract_pdf(
    file: UploadFile = File(..., description="PDF file to extract"),
    profile: ExtractionProfile = Form(
        default=ExtractionProfile.BALANCED,
        description="Extraction quality profile"
    ),
    ocr_mode: OCRMode = Form(
        default=OCRMode.AUTO,
        description="OCR processing mode"
    ),
    ocr_lang: str = Form(
        default="fra",
        description="OCR language code"
    ),
    page_range: Optional[str] = Form(
        default=None,
        description="Page range (e.g., '1-5', '1,3,5')"
    ),
    detect_tables: bool = Form(
        default=True,
        description="Enable table detection"
    ),
    extract_images: bool = Form(
        default=False,
        description="Extract images from PDF"
    ),
    settings: Settings = Depends(get_settings),
    extractor: PDFExtractorService = Depends(get_extractor_service)
):
    """
    Extract structured data from PDF file

    **Parameters:**
    - **file**: PDF file to process (max 50MB)
    - **profile**: Extraction quality (fast/balanced/accurate)
    - **ocr_mode**: OCR processing (auto/on/off)
    - **ocr_lang**: Language for OCR (fra/eng/spa/deu/ita/por)
    - **page_range**: Pages to extract (optional)
    - **detect_tables**: Enable table detection
    - **extract_images**: Extract images

    **Returns:**
    - Complete extraction result with metadata, pages, and elements
    """
    file_path = None

    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )

        # Validate file size
        content = await file.read()
        if len(content) > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum of {settings.max_upload_size / 1024 / 1024}MB"
            )

        # Reset file pointer and save
        await file.seek(0)
        file_path = await save_upload_file(file, settings)

        logger.info(f"Processing PDF: {file.filename} ({len(content)} bytes)")

        # Create extraction request
        request = ExtractionRequest(
            profile=profile,
            ocr_mode=ocr_mode,
            ocr_lang=ocr_lang,
            page_range=page_range,
            detect_tables=detect_tables,
            extract_images=extract_images
        )

        # Extract PDF
        result = await extractor.extract(file_path, request)

        return ExtractionResponse(
            success=True,
            result=result
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )

    finally:
        # Cleanup temporary file
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")


@router.get(
    "/schema",
    summary="Get JSON schema",
    description="Get the JSON schema for extraction results"
)
async def get_schema():
    """Get the JSON schema for ExtractionResult"""
    return JSONResponse(content=ExtractionResult.model_json_schema())


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running and services are available"
)
async def health_check(
    extractor: PDFExtractorService = Depends(get_extractor_service)
):
    """Health check endpoint"""
    ocr_available = extractor.ocr_service.is_available()

    return {
        "status": "healthy",
        "services": {
            "ocr": "available" if ocr_available else "unavailable",
            "pdf_extraction": "available"
        }
    }


@router.get(
    "/ocr/languages",
    summary="Get available OCR languages",
    description="List all available Tesseract OCR languages"
)
async def get_ocr_languages(
    extractor: PDFExtractorService = Depends(get_extractor_service)
):
    """Get list of available OCR languages"""
    languages = extractor.ocr_service.get_available_languages()
    return {"languages": languages}


@router.get(
    "/profiles",
    summary="Get extraction profiles",
    description="Get available extraction profiles and their configurations"
)
async def get_profiles(settings: Settings = Depends(get_settings)):
    """Get available extraction profiles"""
    return {
        "profiles": settings.extraction_profiles,
        "default": "balanced"
    }
