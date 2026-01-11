"""
Pydantic schemas for API requests and responses.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DetectionResponse(BaseModel):
    """Response schema for detection results."""
    id: int
    plate_text: str
    confidence: float
    bbox: List[int] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    timestamp: datetime
    vehicle_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class DetectionCreate(BaseModel):
    """Schema for creating a detection."""
    plate_text: str
    confidence: float
    bbox: List[int] = Field(..., description="Bounding box [x1, y1, x2, y2]")
    image_path: Optional[str] = None


class EventResponse(BaseModel):
    """Response schema for events."""
    id: int
    event_type: str = Field(..., description="ALLOW, ALERT, or LOG_ONLY")
    description: Optional[str] = None
    rule_name: Optional[str] = None
    timestamp: datetime
    plate_text: Optional[str] = None
    vehicle_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Response schema for alerts."""
    id: int
    plate_text: str
    event_type: str
    description: str
    timestamp: datetime
    rule_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class DetectionRequest(BaseModel):
    """Request schema for detection endpoint."""
    image_url: Optional[str] = None
    use_camera: bool = False
