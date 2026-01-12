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
            logger.info(f"Processing frame: shape={frame.shape}, dtype={frame.dtype}")
            
            # Detect license plates (or vehicles/regions of interest)
            detections = self.detector.detect(frame)
            
            if not detections:
                logger.warning("No detections returned from detector")
                return None
            
            logger.info(f"Found {len(detections)} detection(s)")
            
            # Use the detection with highest confidence
            best_detection = max(detections, key=lambda x: x[4])
            x1, y1, x2, y2, detection_confidence = best_detection
            
            logger.info(f"Best detection: bbox=({x1},{y1},{x2},{y2}), conf={detection_confidence:.2f}")
            
            # Ensure coordinates are valid
            h, w = frame.shape[:2]
            x1 = max(0, min(x1, w-1))
            y1 = max(0, min(y1, h-1))
            x2 = max(x1+1, min(x2, w))
            y2 = max(y1+1, min(y2, h))
            
            # Crop the license plate region with padding
            # Add padding to ensure we capture the full plate
            padding = 10
            x1_padded = max(0, x1 - padding)
            y1_padded = max(0, y1 - padding)
            x2_padded = min(w, x2 + padding)
            y2_padded = min(h, y2 + padding)
            
            plate_roi = frame[y1_padded:y2_padded, x1_padded:x2_padded]
            
            if plate_roi.size == 0:
                logger.warning(f"Empty ROI after cropping: ({x1},{y1},{x2},{y2})")
                return None
            
            logger.info(f"ROI shape: {plate_roi.shape}")
            
            # Try multiple strategies for better accuracy
            plate_text = None
            ocr_confidence = 0.0
            best_bbox = (x1, y1, x2, y2)
            
            # Strategy 1: OCR on cropped ROI (optimized - early exit on high confidence)
            plate_text, ocr_confidence = self.ocr_engine.read_text(plate_roi)
            if plate_text and len(plate_text) >= 3 and ocr_confidence >= 0.6:
                # High confidence result - skip fallback strategies for speed
                logger.info(f"OCR succeeded on ROI: {plate_text} (confidence: {ocr_confidence:.2f})")
            elif plate_text and len(plate_text) >= 3:
                # Lower confidence but valid - use it
                logger.info(f"OCR succeeded on ROI: {plate_text} (confidence: {ocr_confidence:.2f})")
            else:
                logger.warning("OCR on ROI failed or result too short")
                plate_text = None
                
                # Strategy 2: If ROI failed, try different regions of the frame
                if not plate_text:
                    # Try bottom third of frame (where plates usually are)
                    bottom_third = frame[int(h*0.67):h, :]
                    plate_text, ocr_confidence = self.ocr_engine.read_text(bottom_third)
                    if plate_text and len(plate_text) >= 3:
                        logger.info(f"OCR succeeded on bottom third: {plate_text}")
                        best_bbox = (0, int(h*0.67), w, h)
                        detection_confidence = 0.4
                    else:
                        plate_text = None
                
                # Strategy 3: Try entire frame as last resort (only if still no result)
                if not plate_text:
                    logger.info("Trying OCR on entire frame as fallback")
                    plate_text, ocr_confidence = self.ocr_engine.read_text(frame)
                    if plate_text and len(plate_text) >= 3:
                        logger.info(f"OCR succeeded on full frame: {plate_text}")
                        best_bbox = (0, 0, w, h)
                        detection_confidence = 0.3
                    else:
                        logger.warning("OCR failed on all strategies")
                        return None
            
            # Update bbox if we used a different region
            x1, y1, x2, y2 = best_bbox
            
            # Clean up plate text
            plate_text = plate_text.strip().upper()
            
            # Filter out obviously invalid results (single characters, very short)
            if len(plate_text) < 3:
                logger.warning(f"Plate text too short: '{plate_text}'")
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
            import traceback
            logger.error(traceback.format_exc())
            return None

