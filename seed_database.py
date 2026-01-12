#!/usr/bin/env python3
"""
Database seeding script for EagleEyeAI.
Populates the database with dummy data for frontend demonstration.
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.database import get_db_session, init_db
from src.database.models import Vehicle, Detection, Event
from utils.logger import logger

# Load environment variables
load_dotenv()


def create_sample_vehicles(db):
    """Create sample vehicles."""
    vehicles_data = [
        # Authorized vehicles
        {
            "plate_number": "MH12AB1234",
            "vehicle_type": "Sedan",
            "owner_name": "Rajesh Kumar",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Regular visitor"
        },
        {
            "plate_number": "DL01CD5678",
            "vehicle_type": "SUV",
            "owner_name": "Priya Sharma",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Authorized employee"
        },
        {
            "plate_number": "KA03EF9012",
            "vehicle_type": "Hatchback",
            "owner_name": "Amit Patel",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Guest vehicle"
        },
        {
            "plate_number": "GJ05KL2345",
            "vehicle_type": "Truck",
            "owner_name": "Logistics Corp",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Delivery vehicle - Material Truck"
        },
        {
            "plate_number": "RJ06MN6789",
            "vehicle_type": "Sedan",
            "owner_name": "Anita Mehta",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Regular visitor"
        },
        {
            "plate_number": "WB07OP0123",
            "vehicle_type": "Motorcycle",
            "owner_name": "Ravi Das",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Two-wheeler entry"
        },
        # Construction site material trucks
        {
            "plate_number": "MH04MF2221",
            "vehicle_type": "Truck",
            "owner_name": "BuildTech Materials",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Material Truck - Construction Site Vendor"
        },
        {
            "plate_number": "DL02ST4567",
            "vehicle_type": "Truck",
            "owner_name": "Steel Suppliers Ltd",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Material Truck - Steel delivery"
        },
        {
            "plate_number": "KA05CE7890",
            "vehicle_type": "Truck",
            "owner_name": "Cement Express",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Material Truck - Cement delivery"
        },
        {
            "plate_number": "TN08GH3456",
            "vehicle_type": "Truck",
            "owner_name": "Gravel & Sand Co",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Material Truck - Aggregate delivery"
        },
        {
            "plate_number": "GJ09JK5678",
            "vehicle_type": "Truck",
            "owner_name": "Brick Masters",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Material Truck - Brick delivery"
        },
        # Machinery vehicles
        {
            "plate_number": "MP10NO1234",
            "vehicle_type": "Excavator",
            "owner_name": "Heavy Machinery Rentals",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Machinery - Construction equipment"
        },
        {
            "plate_number": "UP11PQ5678",
            "vehicle_type": "Crane",
            "owner_name": "Lift & Move Services",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Machinery - Crane vehicle"
        },
        # Staff vehicles
        {
            "plate_number": "HR12RS9012",
            "vehicle_type": "Sedan",
            "owner_name": "Site Manager - John Doe",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Staff vehicle - Site manager"
        },
        {
            "plate_number": "PB13TU3456",
            "vehicle_type": "SUV",
            "owner_name": "Engineer - Sarah Smith",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Staff vehicle - Site engineer"
        },
        # Unauthorized/Alert vehicles
        {
            "plate_number": "TN09GH3456",
            "vehicle_type": "Sedan",
            "owner_name": "Suresh Reddy",
            "is_authorized": False,
            "is_blacklisted": False,
            "notes": "Unauthorized entry attempt"
        },
        {
            "plate_number": "UP14IJ7890",
            "vehicle_type": "SUV",
            "owner_name": "Vikram Singh",
            "is_authorized": False,
            "is_blacklisted": True,
            "notes": "Blacklisted vehicle - security alert"
        },
        {
            "plate_number": "OR15VW2345",
            "vehicle_type": "Truck",
            "owner_name": "Unknown",
            "is_authorized": False,
            "is_blacklisted": True,
            "notes": "Blacklisted - Suspicious material movement"
        },
        # Additional authorized vehicles
        {
            "plate_number": "AP16XY6789",
            "vehicle_type": "Sedan",
            "owner_name": "Kiran Reddy",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Regular visitor"
        },
        {
            "plate_number": "TS17ZA0123",
            "vehicle_type": "SUV",
            "owner_name": "Rohit Verma",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Authorized contractor"
        },
        {
            "plate_number": "KL18BC4567",
            "vehicle_type": "Truck",
            "owner_name": "Timber Traders",
            "is_authorized": True,
            "is_blacklisted": False,
            "notes": "Material Truck - Wood delivery"
        }
    ]
    
    vehicles = []
    for data in vehicles_data:
        # Check if vehicle already exists
        existing = db.query(Vehicle).filter(
            Vehicle.plate_number == data["plate_number"]
        ).first()
        
        if not existing:
            vehicle = Vehicle(**data)
            db.add(vehicle)
            vehicles.append(vehicle)
            logger.info(f"Created vehicle: {data['plate_number']}")
        else:
            vehicles.append(existing)
            logger.info(f"Vehicle already exists: {data['plate_number']}")
    
    db.commit()
    return vehicles


def create_sample_detections(db, vehicles):
    """Create sample detections."""
    detections_data = []
    
    # Generate detections for the last 14 days (2 weeks)
    base_time = datetime.utcnow()
    
    # Create more detections (150 total)
    for i in range(150):
        # Random vehicle
        vehicle = random.choice(vehicles)
        
        # Random time in the last 14 days
        hours_ago = random.randint(0, 336)  # 14 days = 336 hours
        detection_time = base_time - timedelta(hours=hours_ago)
        
        # Add some randomness to minutes and seconds for more realistic timestamps
        detection_time = detection_time - timedelta(
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        # Random bounding box (simulated)
        x1 = random.randint(100, 400)
        y1 = random.randint(150, 350)
        x2 = x1 + random.randint(150, 250)
        y2 = y1 + random.randint(40, 80)
        
        # Confidence between 0.70 and 0.99 (more realistic range)
        confidence = round(random.uniform(0.70, 0.99), 2)
        
        detection = Detection(
            vehicle_id=vehicle.id,
            plate_text=vehicle.plate_number,
            confidence=confidence,
            bbox_x1=x1,
            bbox_y1=y1,
            bbox_x2=x2,
            bbox_y2=y2,
            timestamp=detection_time
        )
        
        db.add(detection)
        detections_data.append(detection)
    
    db.commit()
    logger.info(f"Created {len(detections_data)} detections")
    return detections_data


def create_sample_events(db, vehicles, detections):
    """Create sample events."""
    events_data = []
    
    # Map detections to their vehicles
    detection_map = {d.id: d for d in detections}
    
    # Track entry/exit for construction site monitoring
    vehicle_last_seen = {}  # Track last detection time per vehicle
    
    for detection in sorted(detections, key=lambda x: x.timestamp):
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == detection.vehicle_id
        ).first()
        
        if not vehicle:
            continue
        
        # Determine if this is entry or exit based on previous detections
        is_entry = True
        if vehicle.id in vehicle_last_seen:
            time_since_last = (detection.timestamp - vehicle_last_seen[vehicle.id]).total_seconds() / 3600  # hours
            # If last seen more than 2 hours ago, treat as new entry
            if time_since_last < 2:
                is_entry = False  # Likely an exit
        
        vehicle_last_seen[vehicle.id] = detection.timestamp
        
        # Determine event type based on vehicle status
        if vehicle.is_blacklisted:
            event_type = "ALERT"
            rule_name = "blacklisted_vehicle"
            direction = "Entry" if is_entry else "Exit"
            description = f"Blacklisted vehicle detected: {vehicle.plate_number} - {direction}"
        elif not vehicle.is_authorized:
            event_type = "ALERT"
            rule_name = "unauthorized_entry"
            direction = "Entry" if is_entry else "Exit"
            description = f"Unauthorized vehicle detected: {vehicle.plate_number} - {direction}"
        else:
            # Mix of ALLOW and LOG_ONLY for authorized vehicles
            if random.random() < 0.08:  # 8% chance of LOG_ONLY
                event_type = "LOG_ONLY"
                rule_name = "suspicious_activity"
                direction = "Entry" if is_entry else "Exit"
                description = f"Suspicious activity logged for: {vehicle.plate_number} - {direction}"
            else:
                event_type = "ALLOW"
                rule_name = "normal_entry"
                direction = "Entry" if is_entry else "Exit"
                description = f"Vehicle allowed: {vehicle.plate_number} - {direction}"
        
        event = Event(
            vehicle_id=vehicle.id,
            detection_id=detection.id,
            event_type=event_type,
            description=description,
            rule_name=rule_name,
            timestamp=detection.timestamp
        )
        
        db.add(event)
        events_data.append(event)
    
    db.commit()
    logger.info(f"Created {len(events_data)} events")
    return events_data


def main():
    """Main seeding function."""
    print("=" * 60)
    print("EagleEyeAI Database Seeding")
    print("=" * 60)
    
    try:
        # Initialize database (creates tables if they don't exist)
        print("\n1. Initializing database...")
        init_db()
        
        # Get database session
        db = get_db_session()
        
        try:
            # Create vehicles
            print("\n2. Creating sample vehicles...")
            vehicles = create_sample_vehicles(db)
            print(f"   ✅ Created/found {len(vehicles)} vehicles")
            
            # Create detections
            print("\n3. Creating sample detections...")
            detections = create_sample_detections(db, vehicles)
            print(f"   ✅ Created {len(detections)} detections")
            
            # Create events
            print("\n4. Creating sample events...")
            events = create_sample_events(db, vehicles, detections)
            print(f"   ✅ Created {len(events)} events")
            
            # Summary
            print("\n" + "=" * 60)
            print("✅ Database seeding completed successfully!")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  - Vehicles: {len(vehicles)}")
            print(f"  - Detections: {len(detections)}")
            print(f"  - Events: {len(events)}")
            print(f"\n  - ALLOW events: {sum(1 for e in events if e.event_type == 'ALLOW')}")
            print(f"  - ALERT events: {sum(1 for e in events if e.event_type == 'ALERT')}")
            print(f"  - LOG_ONLY events: {sum(1 for e in events if e.event_type == 'LOG_ONLY')}")
            print("\nYou can now view this data in the frontend application!")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
