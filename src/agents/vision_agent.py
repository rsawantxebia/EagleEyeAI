"""
Vision Agent - Handles detection and OCR.
Combines plate detection and OCR to extract plate text.
"""
from datetime import datetime
from typing import Dict, Optional
import numpy as np
import cv2

from utils.logger import logger
from src.vision.detector import PlateDetector
from src.vision.ocr_engine import OCREngine


class VisionAgent:
    """Agent responsible for license plate detection and OCR."""
    
    def __init__(self):
        """Initialize vision agent with detector and OCR engine."""
        try:
            self.detector = PlateDetector()
            self.ocr_engine = OCREngine()
            logger.info("Vision agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vision agent: {e}")
            raise
    
    def process_frame(self, frame: np.ndarray) -> Optional[Dict]:
        """
        Process a video frame to detect and read license plate.
        
        Args:
            frame: Input frame as NumPy array (BGR format)
        
        Returns:
            Dictionary with plate_text, confidence, bbox, and timestamp.
            Returns None if no plate detected or OCR fails.
        """
        try:
            # Detect license plates
            detections = self.detector.detect(frame)
            
            if not detections:
                return None
            
            # Use the detection with highest confidence
            best_detection = max(detections, key=lambda x: x[4])
            x1, y1, x2, y2, detection_confidence = best_detection
            
            # Crop the license plate region
            plate_roi = frame[y1:y2, x1:x2]
            
            if plate_roi.size == 0:
                logger.warning("Empty ROI after cropping")
                return None
            
            # Perform OCR on cropped region
            plate_text, ocr_confidence = self.ocr_engine.read_text(plate_roi)
            
            if plate_text is None:
                logger.debug("OCR failed to extract text")
                return None
            
            # Calculate combined confidence
            combined_confidence = (detection_confidence + ocr_confidence) / 2.0
            
            # Format output according to specification
            result = {
                "plate_text": plate_text,
                "confidence": combined_confidence,
                "bbox": [x1, y1, x2, y2],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Plate detected: {plate_text} (confidence: {combined_confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in vision agent processing: {e}")
            return None
