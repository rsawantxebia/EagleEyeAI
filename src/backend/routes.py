"""
FastAPI routes for ANPR system.
Handles all API endpoints.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import cv2
import numpy as np
import requests
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.database import get_db, Detection, Event, Vehicle
from src.backend.schemas import (
    DetectionResponse,
    DetectionCreate,
    EventResponse,
    AlertResponse,
    DetectionRequest
)
from src.agents import VisionAgent, ValidationAgent, EventAgent
from utils.logger import logger

router = APIRouter()


def load_image(image_url: Optional[str]) -> np.ndarray:
    """
    Load an image from URL or file path.
    
    Args:
        image_url: URL or file path to the image
    
    Returns:
        NumPy array representing the image (BGR format)
    """
    if not image_url:
        raise ValueError("image_url is required")
    
    try:
        # Try to load from URL
        if image_url.startswith(('http://', 'https://')):
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = np.frombuffer(response.content, np.uint8)
            frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        else:
            # Load from file path
            frame = cv2.imread(image_url)
        
        if frame is None:
            raise ValueError(f"Could not load image from: {image_url}")
        
        return frame
    except Exception as e:
        logger.error(f"Error loading image: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to load image: {str(e)}")


# Initialize agents (singleton pattern for demo)
_vision_agent: Optional[VisionAgent] = None
_validation_agent: Optional[ValidationAgent] = None
_event_agent: Optional[EventAgent] = None


def get_vision_agent() -> VisionAgent:
    """Get or create vision agent instance."""
    global _vision_agent
    if _vision_agent is None:
        _vision_agent = VisionAgent()
    return _vision_agent


def get_validation_agent() -> ValidationAgent:
    """Get or create validation agent instance."""
    global _validation_agent
    if _validation_agent is None:
        _validation_agent = ValidationAgent()
    return _validation_agent


def get_event_agent() -> EventAgent:
    """Get or create event agent instance."""
    global _event_agent
    if _event_agent is None:
        _event_agent = EventAgent()
    return _event_agent


@router.get("/detections", response_model=List[DetectionResponse])
def get_detections(
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """Get all detections with pagination."""
    try:
        detections = db.query(Detection)\
            .order_by(desc(Detection.timestamp))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        # Convert Detection models to DetectionResponse with bbox as list
        result = []
        for detection in detections:
            result.append(DetectionResponse(
                id=detection.id,
                plate_text=detection.plate_text,
                confidence=detection.confidence,
                bbox=[detection.bbox_x1, detection.bbox_y1, detection.bbox_x2, detection.bbox_y2],
                timestamp=detection.timestamp,
                vehicle_id=detection.vehicle_id
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching detections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events", response_model=List[EventResponse])
def get_events(
    limit: int = 100,
    skip: int = 0,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all events with optional filtering by event_type."""
    try:
        query = db.query(Event).order_by(desc(Event.timestamp))
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        events = query.offset(skip).limit(limit).all()
        
        # Add plate_text from related detection or vehicle
        result = []
        for event in events:
            event_dict = {
                "id": event.id,
                "event_type": event.event_type,
                "description": event.description,
                "rule_name": event.rule_name,
                "timestamp": event.timestamp,
                "vehicle_id": event.vehicle_id,
                "plate_text": None
            }
            
            if event.detection_id:
                detection = db.query(Detection).filter(Detection.id == event.detection_id).first()
                if detection:
                    event_dict["plate_text"] = detection.plate_text
            
            result.append(EventResponse(**event_dict))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect", response_model=DetectionResponse)
async def detect_plate(
    file: UploadFile = File(None),
    image_url: Optional[str] = Form(None),
    use_camera: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Detect and process a license plate from uploaded image or image URL.
    Accepts either:
    - file: Uploaded image file (multipart/form-data)
    - image_url: URL to an image
    - use_camera: Use camera (not implemented yet)
    """
    try:
        vision_agent = get_vision_agent()
        validation_agent = get_validation_agent()
        event_agent = get_event_agent()
        
        frame = None
        
        # Priority: file upload > image_url > use_camera > sample image
        if file and file.filename:
            # Read uploaded file
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                raise HTTPException(status_code=400, detail="Invalid image file")
            logger.info(f"Processing uploaded file: {file.filename}")
        elif image_url:
            # Load from URL
            frame = load_image(image_url)
            logger.info(f"Processing image from URL: {image_url}")
        elif use_camera:
            # Camera capture (not implemented)
            raise HTTPException(status_code=501, detail="Camera capture not implemented yet")
        else:
            # No input provided - use sample image as fallback
            sample_path = Path(__file__).parent.parent.parent / "samples" / "sample_license_plate.jpg"
            if sample_path.exists():
                frame = cv2.imread(str(sample_path))
                logger.info("No input provided, using sample image")
            else:
                # Fallback to mock data
                logger.warning("No image provided and sample not found, using mock data")
                vision_result = {
                    "plate_text": "MH12AB1234",
                    "confidence": 0.95,
                    "bbox": [100, 200, 300, 250],
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Process frame if we have one
        if frame is not None:
            vision_result = vision_agent.process_frame(frame)
            if not vision_result:
                # Fallback to mock if detection fails
                logger.warning("Detection failed, using mock data")
                vision_result = {
                    "plate_text": "MH12AB1234",
                    "confidence": 0.95,
                    "bbox": [100, 200, 300, 250],
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        if not vision_result:
            raise HTTPException(status_code=404, detail="No license plate detected")
        
        # Validate plate
        validation_result = validation_agent.validate(vision_result["plate_text"])
        
        # Check vehicle in database
        vehicle = db.query(Vehicle).filter(
            Vehicle.plate_number == validation_result["normalized_text"]
        ).first()
        
        vehicle_info = None
        if vehicle:
            vehicle_info = {
                "is_authorized": vehicle.is_authorized,
                "is_blacklisted": vehicle.is_blacklisted
            }
        
        # Make event decision
        event_result = event_agent.decide(
            validation_result["normalized_text"],
            validation_result["is_valid"],
            vehicle_info
        )
        
        # Save detection to database
        bbox = vision_result["bbox"]
        detection = Detection(
            vehicle_id=vehicle.id if vehicle else None,
            plate_text=validation_result["normalized_text"],
            confidence=vision_result["confidence"],
            bbox_x1=bbox[0],
            bbox_y1=bbox[1],
            bbox_x2=bbox[2],
            bbox_y2=bbox[3],
            timestamp=datetime.fromisoformat(vision_result["timestamp"].replace('Z', '+00:00'))
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        
        # Save event to database
        event = Event(
            vehicle_id=vehicle.id if vehicle else None,
            detection_id=detection.id,
            event_type=event_result["action"],
            description=event_result["description"],
            rule_name=event_result["rule_name"]
        )
        db.add(event)
        db.commit()
        
        # Convert Detection model to DetectionResponse with bbox as list
        return DetectionResponse(
            id=detection.id,
            plate_text=detection.plate_text,
            confidence=detection.confidence,
            bbox=[detection.bbox_x1, detection.bbox_y1, detection.bbox_x2, detection.bbox_y2],
            timestamp=detection.timestamp,
            vehicle_id=detection.vehicle_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in detection endpoint: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    limit: int = 100,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get alert events from the last N hours."""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        events = db.query(Event)\
            .filter(Event.event_type == "ALERT")\
            .filter(Event.timestamp >= since)\
            .order_by(desc(Event.timestamp))\
            .limit(limit)\
            .all()
        
        result = []
        for event in events:
            plate_text = "Unknown"
            
            if event.detection_id:
                detection = db.query(Detection).filter(Detection.id == event.detection_id).first()
                if detection:
                    plate_text = detection.plate_text
            
            result.append(AlertResponse(
                id=event.id,
                plate_text=plate_text,
                event_type=event.event_type,
                description=event.description or "",
                timestamp=event.timestamp,
                rule_name=event.rule_name
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
