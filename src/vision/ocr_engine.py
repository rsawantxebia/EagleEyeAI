"""
OCR engine using EasyOCR for license plate text recognition.
Handles text extraction from cropped license plate images.
"""
from typing import Optional, Tuple
import numpy as np
import easyocr

from utils.logger import logger


class OCREngine:
    """EasyOCR-based OCR engine for license plate text recognition."""
    
    def __init__(self):
        """Initialize EasyOCR reader for English language."""
        try:
            self.reader = easyocr.Reader(['en'], gpu=False)  # CPU mode for laptop compatibility
            logger.info("OCR engine initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OCR engine: {e}")
            raise
    
    def read_text(self, image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Extract text from a license plate image.
        
        Args:
            image: Cropped license plate image as NumPy array (BGR format)
        
        Returns:
            Tuple of (text, confidence). Returns (None, 0.0) if no text found.
        """
        try:
            results = self.reader.readtext(image)
            
            if not results:
                return None, 0.0
            
            # Combine all detected text
            texts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                # Clean text (remove spaces, convert to uppercase)
                cleaned_text = text.replace(" ", "").upper().strip()
                if cleaned_text:
                    texts.append(cleaned_text)
                    confidences.append(confidence)
            
            if not texts:
                return None, 0.0
            
            # Combine texts and calculate average confidence
            combined_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.debug(f"OCR result: {combined_text} (confidence: {avg_confidence:.2f})")
            return combined_text, avg_confidence
            
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return None, 0.0
