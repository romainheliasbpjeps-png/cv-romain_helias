"""
Data models for PDF extraction
All models use Pydantic for validation and serialization
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ElementType(str, Enum):
    """Types of elements that can be extracted from PDF"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    FIGURE = "figure"
    FOOTER = "footer"
    HEADER = "header"
    CAPTION = "caption"
    CODE = "code"
    FORMULA = "formula"
    UNKNOWN = "unknown"


class SourceMethod(str, Enum):
    """Method used to extract the element"""
    NATIVE_TEXT = "native_text"
    OCR = "ocr"
    TABLE_DETECT = "table_detect"
    IMAGE_EXTRACT = "image_extract"
    LAYOUT_ANALYSIS = "layout_analysis"


class OCRMode(str, Enum):
    """OCR processing modes"""
    AUTO = "auto"  # Use OCR only if no native text detected
    ON = "on"      # Force OCR on all content
    OFF = "off"    # Never use OCR


class ExtractionProfile(str, Enum):
    """Extraction quality profiles"""
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"


class BoundingBox(BaseModel):
    """Bounding box coordinates (in points, origin at bottom-left)"""
    model_config = ConfigDict(frozen=True)

    x0: float = Field(..., description="Left X coordinate")
    y0: float = Field(..., description="Bottom Y coordinate")
    x1: float = Field(..., description="Right X coordinate")
    y1: float = Field(..., description="Top Y coordinate")

    @field_validator('x0', 'x1', 'y0', 'y1')
    @classmethod
    def validate_positive(cls, v: float) -> float:
        """Ensure coordinates are non-negative"""
        if v < 0:
            raise ValueError("Coordinates must be non-negative")
        return v

    @property
    def width(self) -> float:
        """Calculate width"""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Calculate height"""
        return self.y1 - self.y0

    @property
    def area(self) -> float:
        """Calculate area"""
        return self.width * self.height

    def __str__(self) -> str:
        return f"BBox({self.x0:.1f}, {self.y0:.1f}, {self.x1:.1f}, {self.y1:.1f})"


class Element(BaseModel):
    """A single extracted element from the PDF"""
    model_config = ConfigDict(use_enum_values=True)

    type: ElementType = Field(..., description="Element type")
    text: Optional[str] = Field(None, description="Extracted text content")
    bbox: Optional[BoundingBox] = Field(None, description="Bounding box coordinates")
    source_method: SourceMethod = Field(..., description="Extraction method used")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")

    # Styling information
    font_name: Optional[str] = Field(None, description="Font family name")
    font_size: Optional[float] = Field(None, description="Font size in points")
    font_color: Optional[str] = Field(None, description="Font color (hex)")

    # Hierarchy
    level: Optional[int] = Field(None, description="Hierarchical level (for headings)")
    parent_id: Optional[str] = Field(None, description="Parent element ID")
    children: List["Element"] = Field(default_factory=list, description="Child elements")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def __str__(self) -> str:
        text_preview = (self.text[:50] + "...") if self.text and len(self.text) > 50 else self.text
        return f"{self.type}: {text_preview}"


class Page(BaseModel):
    """A single page from the PDF"""
    page_index: int = Field(..., ge=0, description="Zero-based page index")
    width: float = Field(..., gt=0, description="Page width in points")
    height: float = Field(..., gt=0, description="Page height in points")
    rotation: int = Field(default=0, description="Page rotation in degrees")
    elements: List[Element] = Field(default_factory=list, description="Extracted elements")

    # Page metadata
    has_native_text: bool = Field(default=False, description="Whether page has native text")
    is_scanned: bool = Field(default=False, description="Whether page appears to be scanned")
    language: Optional[str] = Field(None, description="Detected language code")

    def __str__(self) -> str:
        return f"Page {self.page_index + 1}: {len(self.elements)} elements"


class PDFMetadata(BaseModel):
    """PDF document metadata"""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None


class Document(BaseModel):
    """PDF document information"""
    file_name: str = Field(..., description="Original filename")
    file_hash: str = Field(..., description="SHA-256 hash of the file")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    pdf_metadata: PDFMetadata = Field(default_factory=PDFMetadata, description="PDF metadata")
    page_count: int = Field(..., gt=0, description="Total number of pages")


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process"""
    app_version: str = Field(..., description="Application version")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Extraction timestamp")
    extractor_versions: Dict[str, str] = Field(
        default_factory=dict,
        description="Versions of extraction libraries used"
    )
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")


class ExtractionArtifacts(BaseModel):
    """Additional information about the extraction"""
    ocr_used: bool = Field(default=False, description="Whether OCR was used")
    ocr_languages: List[str] = Field(default_factory=list, description="OCR languages used")
    extraction_profile: ExtractionProfile = Field(..., description="Extraction profile used")
    pages_with_ocr: List[int] = Field(default_factory=list, description="Pages where OCR was applied")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errors encountered")


class ExtractionResult(BaseModel):
    """Complete extraction result"""
    meta: ExtractionMetadata = Field(..., description="Extraction metadata")
    document: Document = Field(..., description="Document information")
    pages: List[Page] = Field(..., description="Extracted pages")
    artifacts: ExtractionArtifacts = Field(..., description="Extraction artifacts")

    def __str__(self) -> str:
        return f"ExtractionResult: {self.document.file_name} - {len(self.pages)} pages"


class ExtractionRequest(BaseModel):
    """Request parameters for PDF extraction"""
    profile: ExtractionProfile = Field(
        default=ExtractionProfile.BALANCED,
        description="Extraction quality profile"
    )
    ocr_mode: OCRMode = Field(
        default=OCRMode.AUTO,
        description="OCR processing mode"
    )
    ocr_lang: str = Field(
        default="fra",
        description="OCR language code"
    )
    page_range: Optional[str] = Field(
        None,
        description="Page range to extract (e.g., '1-5', '1,3,5')",
        examples=["1-5", "1,3,5", "1-3,7-10"]
    )
    detect_tables: bool = Field(
        default=True,
        description="Enable table detection"
    )
    extract_images: bool = Field(
        default=False,
        description="Extract images from PDF"
    )


class ExtractionResponse(BaseModel):
    """API response for extraction endpoint"""
    success: bool = Field(..., description="Whether extraction succeeded")
    result: Optional[ExtractionResult] = Field(None, description="Extraction result")
    error: Optional[str] = Field(None, description="Error message if failed")
    task_id: Optional[str] = Field(None, description="Task ID for async processing")
