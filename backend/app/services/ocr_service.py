"""
OCR Service using Tesseract
Handles text extraction from images and scanned PDFs
"""
import logging
from io import BytesIO
from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytesseract
from PIL import Image

from ..config import get_settings

logger = logging.getLogger(__name__)


class OCRService:
    """
    Professional OCR service using Tesseract

    Features:
    - Multi-language support
    - Confidence scores
    - Bounding box extraction
    - Async processing
    """

    def __init__(self):
        self.settings = get_settings()
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Configure Tesseract path if provided
        if self.settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.settings.tesseract_cmd

    async def extract_text(
        self,
        image_data: bytes,
        lang: str = "fra"
    ) -> List[Dict[str, Any]]:
        """
        Extract text from image using OCR

        Args:
            image_data: Image data as bytes
            lang: Language code (e.g., 'fra', 'eng')

        Returns:
            List of extracted text elements with bounding boxes and confidence
        """
        try:
            # Run OCR in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_ocr,
                image_data,
                lang
            )
            return result

        except Exception as e:
            logger.error(f"OCR failed: {e}", exc_info=True)
            raise

    def _run_ocr(self, image_data: bytes, lang: str) -> List[Dict[str, Any]]:
        """Run OCR synchronously (executed in thread pool)"""

        # Open image
        image = Image.open(BytesIO(image_data))

        # Run Tesseract with detailed output
        ocr_data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT,
            config='--psm 3'  # Fully automatic page segmentation
        )

        # Parse results
        elements = []
        n_boxes = len(ocr_data['text'])

        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])

            # Skip empty text or low confidence
            if not text or conf < 0:
                continue

            # Get bounding box
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]

            elements.append({
                'text': text,
                'bbox': [x, y, x + w, y + h],
                'confidence': conf / 100.0  # Normalize to 0-1
            })

        logger.info(f"OCR extracted {len(elements)} text elements")
        return elements

    def is_available(self) -> bool:
        """Check if Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def get_available_languages(self) -> List[str]:
        """Get list of available Tesseract languages"""
        try:
            langs = pytesseract.get_languages()
            return langs
        except Exception as e:
            logger.error(f"Failed to get Tesseract languages: {e}")
            return []
