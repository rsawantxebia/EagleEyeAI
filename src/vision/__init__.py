"""Vision layer for EagleEyeAI - detection and OCR."""
from .detector import PlateDetector
from .ocr_engine import OCREngine

__all__ = ["PlateDetector", "OCREngine"]
