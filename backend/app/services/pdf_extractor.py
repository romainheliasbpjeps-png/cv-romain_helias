"""
Main PDF extraction service
Orchestrates extraction using PyMuPDF, pdfplumber, and OCR
"""
import hashlib
import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import fitz  # PyMuPDF
import pdfplumber

from ..models.extraction import (
    ExtractionResult,
    ExtractionRequest,
    ExtractionMetadata,
    Document,
    PDFMetadata,
    Page,
    Element,
    ExtractionArtifacts,
    ElementType,
    SourceMethod,
    BoundingBox,
    OCRMode
)
from ..config import get_settings
from .ocr_service import OCRService

logger = logging.getLogger(__name__)


class PDFExtractorService:
    """
    Professional PDF extraction service

    Combines multiple extraction methods for optimal results:
    - PyMuPDF for fast native text extraction
    - pdfplumber for table detection
    - Tesseract OCR for scanned documents
    """

    def __init__(self):
        self.settings = get_settings()
        self.ocr_service = OCRService()

    async def extract(
        self,
        pdf_path: Path,
        request: ExtractionRequest
    ) -> ExtractionResult:
        """
        Extract structured data from PDF

        Args:
            pdf_path: Path to the PDF file
            request: Extraction parameters

        Returns:
            ExtractionResult with all extracted data
        """
        start_time = time.time()

        logger.info(f"Starting extraction for {pdf_path.name} with profile {request.profile}")

        try:
            # Calculate file hash
            file_hash = self._calculate_hash(pdf_path)
            file_size = pdf_path.stat().st_size

            # Open PDF with PyMuPDF
            pdf_doc = fitz.open(pdf_path)

            # Extract metadata
            pdf_metadata = self._extract_metadata(pdf_doc)

            # Parse page range
            page_indices = self._parse_page_range(
                request.page_range,
                pdf_doc.page_count
            )

            # Extract pages
            pages: List[Page] = []
            pages_with_ocr: List[int] = []
            warnings: List[str] = []
            errors: List[Dict[str, Any]] = []

            for page_idx in page_indices:
                try:
                    page_result = await self._extract_page(
                        pdf_doc=pdf_doc,
                        pdf_path=pdf_path,
                        page_idx=page_idx,
                        request=request
                    )
                    pages.append(page_result)

                    if page_result.is_scanned and request.ocr_mode != OCRMode.OFF:
                        pages_with_ocr.append(page_idx)

                except Exception as e:
                    logger.error(f"Error extracting page {page_idx}: {e}", exc_info=True)
                    errors.append({
                        "page": page_idx,
                        "error": str(e),
                        "type": type(e).__name__
                    })
                    warnings.append(f"Failed to extract page {page_idx + 1}")

            pdf_doc.close()

            # Calculate processing time
            processing_time = time.time() - start_time

            # Build result
            result = ExtractionResult(
                meta=ExtractionMetadata(
                    app_version=self.settings.app_version,
                    extractor_versions=self._get_library_versions(),
                    processing_time_seconds=round(processing_time, 2),
                    warnings=warnings
                ),
                document=Document(
                    file_name=pdf_path.name,
                    file_hash=file_hash,
                    file_size=file_size,
                    pdf_metadata=pdf_metadata,
                    page_count=len(pages)
                ),
                pages=pages,
                artifacts=ExtractionArtifacts(
                    ocr_used=len(pages_with_ocr) > 0,
                    ocr_languages=[request.ocr_lang] if pages_with_ocr else [],
                    extraction_profile=request.profile,
                    pages_with_ocr=pages_with_ocr,
                    errors=errors
                )
            )

            logger.info(
                f"Extraction completed for {pdf_path.name}: "
                f"{len(pages)} pages in {processing_time:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Extraction failed for {pdf_path.name}: {e}", exc_info=True)
            raise

    async def _extract_page(
        self,
        pdf_doc: fitz.Document,
        pdf_path: Path,
        page_idx: int,
        request: ExtractionRequest
    ) -> Page:
        """Extract data from a single page"""

        # Get PyMuPDF page
        fitz_page = pdf_doc[page_idx]

        # Get page dimensions
        rect = fitz_page.rect
        width = rect.width
        height = rect.height
        rotation = fitz_page.rotation

        # Extract native text
        elements: List[Element] = []
        has_native_text = False

        # Try native text extraction first
        text_dict = fitz_page.get_text("dict")
        native_elements = self._extract_native_text(text_dict, height)

        if native_elements:
            elements.extend(native_elements)
            has_native_text = True

        # Detect if page is scanned (no native text or very little)
        is_scanned = not has_native_text or len(native_elements) < 3

        # Use OCR if needed
        if is_scanned and request.ocr_mode != OCRMode.OFF:
            ocr_elements = await self._extract_with_ocr(
                fitz_page,
                request.ocr_lang,
                height
            )
            elements.extend(ocr_elements)
        elif request.ocr_mode == OCRMode.ON:
            # Force OCR even if native text exists
            ocr_elements = await self._extract_with_ocr(
                fitz_page,
                request.ocr_lang,
                height
            )
            elements.extend(ocr_elements)

        # Detect tables if requested
        if request.detect_tables:
            table_elements = self._extract_tables(pdf_path, page_idx, height)
            elements.extend(table_elements)

        # Sort elements by vertical position
        elements.sort(key=lambda e: e.bbox.y0 if e.bbox else 0)

        return Page(
            page_index=page_idx,
            width=width,
            height=height,
            rotation=rotation,
            elements=elements,
            has_native_text=has_native_text,
            is_scanned=is_scanned
        )

    def _extract_native_text(
        self,
        text_dict: Dict[str, Any],
        page_height: float
    ) -> List[Element]:
        """Extract native text using PyMuPDF text dictionary"""
        elements: List[Element] = []

        for block in text_dict.get("blocks", []):
            if block.get("type") != 0:  # Only text blocks
                continue

            for line in block.get("lines", []):
                # Combine all spans in the line
                line_text = ""
                font_sizes = []
                font_names = []
                bbox_coords = line.get("bbox", [0, 0, 0, 0])

                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                    font_sizes.append(span.get("size", 12))
                    font_names.append(span.get("font", ""))

                line_text = line_text.strip()
                if not line_text:
                    continue

                # Calculate average font size
                avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12

                # Detect element type
                element_type = self._detect_element_type(line_text, avg_font_size)

                # Convert bbox (PDF coordinates to standard)
                bbox = BoundingBox(
                    x0=bbox_coords[0],
                    y0=page_height - bbox_coords[3],  # Flip Y
                    x1=bbox_coords[2],
                    y1=page_height - bbox_coords[1]   # Flip Y
                )

                elements.append(Element(
                    type=element_type,
                    text=line_text,
                    bbox=bbox,
                    source_method=SourceMethod.NATIVE_TEXT,
                    confidence=1.0,
                    font_size=avg_font_size,
                    font_name=font_names[0] if font_names else None
                ))

        return elements

    async def _extract_with_ocr(
        self,
        fitz_page: fitz.Page,
        lang: str,
        page_height: float
    ) -> List[Element]:
        """Extract text using OCR"""
        try:
            # Render page to image
            pix = fitz_page.get_pixmap(dpi=self.settings.default_dpi)
            img_data = pix.tobytes("png")

            # Run OCR
            ocr_result = await self.ocr_service.extract_text(img_data, lang)

            elements: List[Element] = []
            for item in ocr_result:
                bbox = BoundingBox(
                    x0=item["bbox"][0],
                    y0=page_height - item["bbox"][3],
                    x1=item["bbox"][2],
                    y1=page_height - item["bbox"][1]
                )

                element_type = self._detect_element_type(item["text"], 12)

                elements.append(Element(
                    type=element_type,
                    text=item["text"],
                    bbox=bbox,
                    source_method=SourceMethod.OCR,
                    confidence=item["confidence"]
                ))

            return elements

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return []

    def _extract_tables(
        self,
        pdf_path: Path,
        page_idx: int,
        page_height: float
    ) -> List[Element]:
        """Extract tables using pdfplumber"""
        elements: List[Element] = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_idx >= len(pdf.pages):
                    return elements

                page = pdf.pages[page_idx]
                tables = page.find_tables()

                for table in tables:
                    bbox_coords = table.bbox
                    bbox = BoundingBox(
                        x0=bbox_coords[0],
                        y0=page_height - bbox_coords[3],
                        x1=bbox_coords[2],
                        y1=page_height - bbox_coords[1]
                    )

                    # Extract table data
                    table_data = table.extract()

                    # Convert table to text representation
                    table_text = self._table_to_text(table_data)

                    elements.append(Element(
                        type=ElementType.TABLE,
                        text=table_text,
                        bbox=bbox,
                        source_method=SourceMethod.TABLE_DETECT,
                        confidence=0.85,
                        metadata={"table_data": table_data}
                    ))

        except Exception as e:
            logger.error(f"Table extraction failed: {e}")

        return elements

    def _detect_element_type(self, text: str, font_size: float) -> ElementType:
        """Detect element type based on content and styling"""

        # Check for list markers
        if text.strip().startswith(("•", "-", "*", "◦", "▪")):
            return ElementType.LIST
        if text.strip() and text.strip()[0].isdigit() and ". " in text[:5]:
            return ElementType.LIST

        # Check for heading (short text with larger font or all caps)
        if len(text) < 100 and (font_size > 14 or text.isupper()):
            return ElementType.HEADING

        # Default to paragraph
        return ElementType.PARAGRAPH

    def _extract_metadata(self, pdf_doc: fitz.Document) -> PDFMetadata:
        """Extract PDF metadata"""
        metadata = pdf_doc.metadata
        return PDFMetadata(
            title=metadata.get("title"),
            author=metadata.get("author"),
            subject=metadata.get("subject"),
            keywords=metadata.get("keywords"),
            creator=metadata.get("creator"),
            producer=metadata.get("producer"),
            created=metadata.get("creationDate"),
            modified=metadata.get("modDate")
        )

    def _parse_page_range(
        self,
        page_range: Optional[str],
        total_pages: int
    ) -> List[int]:
        """Parse page range string into list of page indices"""
        if not page_range:
            return list(range(total_pages))

        indices = set()

        for part in page_range.split(","):
            part = part.strip()

            if "-" in part:
                # Range like "1-5"
                start, end = part.split("-")
                start_idx = int(start.strip()) - 1  # Convert to 0-based
                end_idx = int(end.strip()) - 1
                indices.update(range(start_idx, end_idx + 1))
            else:
                # Single page like "3"
                indices.add(int(part) - 1)

        # Filter valid indices
        return sorted([i for i in indices if 0 <= i < total_pages])

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _table_to_text(self, table_data: List[List[str]]) -> str:
        """Convert table data to text representation"""
        if not table_data:
            return ""

        # Simple text representation
        lines = []
        for row in table_data:
            if row:
                lines.append(" | ".join(str(cell or "") for cell in row))

        return "\n".join(lines)

    def _get_library_versions(self) -> Dict[str, str]:
        """Get versions of all extraction libraries"""
        import pytesseract

        versions = {
            "pymupdf": fitz.version[0],
            "pdfplumber": pdfplumber.__version__,
        }

        try:
            tesseract_version = pytesseract.get_tesseract_version()
            versions["tesseract"] = str(tesseract_version)
        except Exception:
            versions["tesseract"] = "not available"

        return versions
