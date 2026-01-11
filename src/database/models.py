"""
Database models for ANPR system.
SQLAlchemy ORM models for vehicles, detections, and events.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Vehicle(Base):
    """Vehicle model to store registered vehicle information."""
    
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), unique=True, index=True, nullable=False)
    vehicle_type = Column(String(50), nullable=True)
    owner_name = Column(String(100), nullable=True)
    is_authorized = Column(Boolean, default=True)
    is_blacklisted = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    detections = relationship("Detection", back_populates="vehicle")
    events = relationship("Event", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle(plate_number='{self.plate_number}')>"


class Detection(Base):
    """Detection model to store number plate detection results."""
    
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, index=True)
    plate_text = Column(String(20), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    bbox_x1 = Column(Integer, nullable=False)
    bbox_y1 = Column(Integer, nullable=False)
    bbox_x2 = Column(Integer, nullable=False)
    bbox_y2 = Column(Integer, nullable=False)
    image_path = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="detections")
    
    def __repr__(self):
        return f"<Detection(plate_text='{self.plate_text}', confidence={self.confidence})>"


class Event(Base):
    """Event model to store system events and decisions."""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # ALLOW, ALERT, LOG_ONLY
    description = Column(Text, nullable=True)
    rule_name = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="events")
    
    def __repr__(self):
        return f"<Event(event_type='{self.event_type}', timestamp='{self.timestamp}')>"
