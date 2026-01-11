"""
Number plate detector using YOLOv8.
Handles object detection for license plates.
"""
from typing import List, Tuple, Optional
import numpy as np
from ultralytics import YOLO

from utils.logger import logger


class PlateDetector:
    """YOLOv8-based license plate detector."""
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize the plate detector.
        
        Args:
            model_path: Path to YOLOv8 model file (uses pretrained model by default)
        """
        try:
            self.model = YOLO(model_path)
            logger.info(f"Plate detector initialized with model: {model_path}")
        except Exception as e:
            logger.error(f"Error loading YOLOv8 model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect license plates in a frame.
        
        Args:
            frame: Input frame as NumPy array (BGR format)
        
        Returns:
            List of detections as (x1, y1, x2, y2, confidence) tuples
        """
        try:
            results = self.model(frame, verbose=False)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        
                        # Convert to integers
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        detections.append((x1, y1, x2, y2, confidence))
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during plate detection: {e}")
            return []
