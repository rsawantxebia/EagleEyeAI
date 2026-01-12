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
            # YOLOv8 default model detects general objects, not specifically license plates
            # We'll use it to detect vehicles/cars, then try to find plates in those regions
            # Or use the entire frame if no vehicles detected
            # Optimized: Fixed image size for faster inference
            results = self.model(frame, verbose=False, conf=0.25, imgsz=640)
            detections = []
            
            # Get all detected objects
            all_boxes = []
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        # Extract bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Convert to integers
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # COCO classes: 2=car, 3=motorcycle, 5=bus, 7=truck
                        # For license plate detection, we're interested in vehicles
                        # But since we don't have a plate-specific model, we'll use the entire frame
                        # or focus on vehicle regions
                        all_boxes.append((x1, y1, x2, y2, confidence, class_id))
            
            # If we have vehicle detections, use those regions
            # Otherwise, use the entire frame (will be handled by OCR on full image)
            if all_boxes:
                # Filter for vehicles (class 2=car, 3=motorcycle, 5=bus, 7=truck)
                vehicle_classes = [2, 3, 5, 7]
                vehicle_boxes = [box for box in all_boxes if box[5] in vehicle_classes]
                
                if vehicle_boxes:
                    # Use the largest vehicle detection
                    largest_vehicle = max(vehicle_boxes, key=lambda x: (x[2]-x[0])*(x[3]-x[1]))
                    x1, y1, x2, y2, conf, _ = largest_vehicle
                    # Expand the region slightly to include potential plate area
                    h, w = frame.shape[:2]
                    x1 = max(0, x1 - 20)
                    y1 = max(0, y1 - 20)
                    x2 = min(w, x2 + 20)
                    y2 = min(h, y2 + 20)
                    detections.append((x1, y1, x2, y2, conf))
                else:
                    # No vehicles detected, use entire frame
                    h, w = frame.shape[:2]
                    detections.append((0, 0, w, h, 0.5))
            else:
                # No detections at all, use entire frame for OCR
                h, w = frame.shape[:2]
                detections.append((0, 0, w, h, 0.5))
                logger.info(f"No objects detected, using entire frame ({w}x{h}) for OCR")
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during plate detection: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback: return entire frame
            h, w = frame.shape[:2]
            return [(0, 0, w, h, 0.5)]
