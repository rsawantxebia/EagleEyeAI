# EagleEyeAI Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Agent-Based Design](#agent-based-design)
4. [Data Flow](#data-flow)
5. [Component Details](#component-details)
6. [Flow Diagrams](#flow-diagrams)
7. [Technology Stack](#technology-stack)

---

## System Overview

EagleEyeAI (Automatic Number Plate Recognition system) is built using an **agent-based architecture** that separates concerns into distinct, modular components. The system follows a **layered architecture** pattern with clear boundaries between vision processing, business logic, API layer, and presentation.

### Core Principles
- **Separation of Concerns**: Each layer has a single responsibility
- **Agent-Based Design**: Business logic is encapsulated in independent agents
- **No Cross-Layer Imports**: Strict boundaries prevent tight coupling
- **Open-Source Only**: All technologies are free and open-source
- **Laptop-Friendly**: CPU-first execution, no GPU requirements

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  Angular Frontend (TypeScript)                               │
│  - Dashboard Component                                       │
│  - Vehicle Logs Component                                    │
│  - Alerts Component                                          │
│  - Construction Site Component                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                     API LAYER                                │
│  FastAPI Backend (Python)                                    │
│  - /api/detect (POST)                                        │
│  - /api/detections (GET)                                     │
│  - /api/events (GET)                                         │
│  - /api/alerts (GET)                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    AGENT LAYER                               │
│  Business Logic Agents (Python)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Vision Agent │  │Validation    │  │ Event Agent  │        │
│  │              │  │Agent         │  │              │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                 │                 │                 │
└─────────┼─────────────────┼─────────────────┼─────────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼─────────────────┐
│                    VISION LAYER                                │
│  Computer Vision Processing (Python)                           │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  Detector    │  │  OCR Engine  │                            │
│  │  (YOLOv8)    │  │  (EasyOCR)   │                            │
│  └──────────────┘  └──────────────┘                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    DATA LAYER                                 │
│  PostgreSQL Database (SQLAlchemy ORM)                         │
│  - vehicles table                                             │
│  - detections table                                           │
│  - events table                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Agent-Based Design

The system uses an **agent-based architecture** where independent agents handle specific responsibilities. Agents are stateless, modular, and can be easily extended or replaced.

### Agent Responsibilities

#### 1. Vision Agent
**Location**: `src/agents/vision_agent.py`

**Purpose**: Orchestrates license plate detection and OCR processing.

**Responsibilities**:
- Receives image frames (NumPy arrays)
- Coordinates between Plate Detector and OCR Engine
- Implements multi-ROI (Region of Interest) processing
- Applies fallback strategies for better accuracy
- Returns structured detection results

**Input**: 
- NumPy array (BGR image format)

**Output**:
```python
{
    "plate_text": str,
    "confidence": float,
    "bbox": [x1, y1, x2, y2],
    "timestamp": ISO-8601 string
}
```

**Key Methods**:
- `process_frame(frame)`: Main processing method
- Uses multiple detection strategies (ROI, bottom third, full frame)
- Early exit on high confidence results

**Dependencies**:
- `PlateDetector` (YOLOv8)
- `OCREngine` (EasyOCR)

---

#### 2. Validation Agent
**Location**: `src/agents/validation_agent.py`

**Purpose**: Validates license plate text against Indian number plate formats.

**Responsibilities**:
- Regex-based validation (no ML)
- Supports Indian plate formats (e.g., MH12AB1234)
- Normalizes plate text
- Returns validation result with normalized text

**Input**:
- Plate text string

**Output**:
```python
{
    "is_valid": bool,
    "normalized_text": str,
    "format": str  # e.g., "XX##XX####"
}
```

**Key Methods**:
- `validate(plate_text)`: Validates and normalizes plate text

**Validation Rules**:
- State code: 2 letters (MH, DL, KA, etc.)
- District code: 2 digits (01-99)
- Series: 1-2 letters (A, AB, etc.)
- Number: 1-4 digits (1, 1234, etc.)

**Dependencies**: None (pure Python regex)

---

#### 3. Event Agent
**Location**: `src/agents/event_agent.py`

**Purpose**: Makes business decisions based on rules and vehicle information.

**Responsibilities**:
- Reads rules from `config/rules.json`
- Makes decisions: ALLOW, ALERT, or LOG_ONLY
- Rule-based logic (no ML)
- Returns decision with description

**Input**:
- Plate text (normalized)
- Validation result (is_valid)
- Vehicle info (is_authorized, is_blacklisted)

**Output**:
```python
{
    "action": "ALLOW" | "ALERT" | "LOG_ONLY",
    "rule_name": str,
    "description": str
}
```

**Key Methods**:
- `decide(plate_text, is_valid, vehicle_info)`: Makes decision based on rules

**Decision Logic**:
1. Invalid plate → LOG_ONLY
2. Blacklisted plate → ALERT
3. Unauthorized plate (if authorization list exists) → ALERT
4. Default → ALLOW

**Dependencies**:
- `config/rules.json` (rule configuration)

---

## Data Flow

### Complete Detection Flow

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. POST /api/detect
       │    (Image file/URL)
       │
┌──────▼──────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  routes.py: detect_plate()                            │  │
│  │  - Receives image                                     │  │
│  │  - Loads/decodes image                                │  │
│  │  - Resizes if needed                                  │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                           │
│                 │ 2. process_frame(image)                   │
│                 │                                           │
│  ┌──────────────▼───────────────────────────────────────┐  │
│  │  Vision Agent                                         │  │
│  │  - Coordinates detection + OCR                       │  │
│  │  - Multi-ROI processing                              │  │
│  │  - Fallback strategies                               │  │
│  └──────┬───────────────────────┬───────────────────────┘  │
│         │                       │                           │
│         │ 3. detect()           │ 4. read_text()           │
│         │                       │                           │
│  ┌──────▼──────┐        ┌───────▼────────┐                 │
│  │  Detector   │        │  OCR Engine    │                 │
│  │  (YOLOv8)   │        │  (EasyOCR)     │                 │
│  │             │        │                │                 │
│  │  - Detects  │        │  - Preprocess  │                 │
│  │    vehicles │        │  - OCR text    │                 │
│  │  - Returns  │        │  - Character   │                 │
│  │    ROI      │        │    correction  │                 │
│  └─────────────┘        └────────────────┘                 │
│         │                       │                           │
│         └───────────┬───────────┘                           │
│                     │                                       │
│                     │ 5. Returns:                           │
│                     │    {plate_text, confidence, bbox}      │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Validation Agent                                     │  │
│  │  - Validates plate format                             │  │
│  │  - Normalizes text                                   │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     │ 6. Returns:                           │
│                     │    {is_valid, normalized_text}        │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Event Agent                                         │  │
│  │  - Checks rules                                      │  │
│  │  - Makes decision                                   │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     │ 7. Returns:                           │
│                     │    {action, rule_name, description}    │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Database (SQLAlchemy)                               │  │
│  │  - Saves Detection                                    │  │
│  │  - Saves Event                                        │  │
│  │  - Links to Vehicle (if exists)                      │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     │ 8. Returns DetectionResponse          │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      │ 9. HTTP Response
                      │    {id, plate_text, confidence, ...}
                      │
┌─────────────────────▼──────┐
│   Client (Browser)         │
│   - Updates UI             │
│   - Shows detection result  │
└────────────────────────────┘
```

### Agent Interaction Flow

```
                    ┌──────────────┐
                    │  FastAPI     │
                    │  /api/detect │
                    └──────┬───────┘
                           │
                           │ 1. Image
                           │
                    ┌──────▼──────────────┐
                    │   Vision Agent      │
                    │                     │
                    │  ┌──────────────┐  │
                    │  │ Plate        │  │
                    │  │ Detector     │  │
                    │  │ (YOLOv8)     │  │
                    │  └──────┬───────┘  │
                    │         │ ROI      │
                    │  ┌──────▼───────┐  │
                    │  │ OCR Engine   │  │
                    │  │ (EasyOCR)    │  │
                    │  └──────┬───────┘  │
                    │         │ Text     │
                    └─────────┼──────────┘
                              │
                              │ 2. plate_text
                              │
                    ┌─────────▼──────────┐
                    │ Validation Agent    │
                    │                     │
                    │ - Regex validation  │
                    │ - Normalize text    │
                    └─────────┬───────────┘
                              │
                              │ 3. normalized_text, is_valid
                              │
                    ┌─────────▼──────────┐
                    │   Event Agent      │
                    │                     │
                    │ - Read rules.json   │
                    │ - Check blacklist   │
                    │ - Check authorized  │
                    │ - Make decision     │
                    └─────────┬───────────┘
                              │
                              │ 4. action, rule_name
                              │
                    ┌─────────▼──────────┐
                    │   Database          │
                    │                     │
                    │ - Save Detection    │
                    │ - Save Event        │
                    └─────────────────────┘
```

---

## Component Details

### Backend Components

#### 1. Vision Layer (`src/vision/`)

**Plate Detector** (`detector.py`):
- Uses YOLOv8 (Ultralytics) for object detection
- Detects vehicles (cars, trucks, buses, motorcycles)
- Extracts ROI (Region of Interest) for license plates
- Multiple strategies: vehicle bottom region, strategic frame regions
- Returns bounding boxes with confidence scores

**OCR Engine** (`ocr_engine.py`):
- Uses EasyOCR for text recognition
- Multiple preprocessing methods (CLAHE, denoise, sharpen)
- Character correction for common OCR errors
- Indian plate format validation
- Returns text with confidence score

#### 2. Agent Layer (`src/agents/`)

**Vision Agent** (`vision_agent.py`):
- Orchestrates detection and OCR
- Multi-ROI processing (tries top 3 detection regions)
- Fallback strategies (bottom third, center-bottom, full frame)
- Early exit on high confidence
- Combines detection and OCR confidence

**Validation Agent** (`validation_agent.py`):
- Regex-based validation
- Indian plate format support
- Text normalization
- Format detection

**Event Agent** (`event_agent.py`):
- Rule-based decision making
- Reads from `config/rules.json`
- Checks blacklist, authorized list
- Returns ALLOW/ALERT/LOG_ONLY decision

#### 3. API Layer (`src/backend/`)

**Routes** (`routes.py`):
- `/api/detect` (POST): Main detection endpoint
- `/api/detections` (GET): List all detections
- `/api/events` (GET): List all events
- `/api/alerts` (GET): List alert events

**Schemas** (`schemas.py`):
- Pydantic models for request/response validation
- DetectionResponse, EventResponse, AlertResponse

**Main** (`main.py`):
- FastAPI application setup
- CORS configuration
- Route registration

#### 4. Database Layer (`src/database/`)

**Models** (`models.py`):
- Vehicle: Registered vehicle information
- Detection: License plate detection results
- Event: System events and decisions

**Connection** (`connection.py`):
- SQLAlchemy engine and session management
- Database initialization
- Connection pooling

### Frontend Components

#### 1. Services (`src/app/services/`)

**ANPR Service** (`anpr.service.ts`):
- HTTP client for backend API
- Methods: getDetections(), getEvents(), getAlerts(), detectPlate()
- Observable-based (RxJS)

**Construction Site Service** (`construction-site.service.ts`):
- Transforms events to construction site format
- Tracks entry/exit state
- Calculates vendor analytics
- Detects material theft alerts

#### 2. Components (`src/app/components/`)

**Dashboard Component**:
- Real-time detection interface
- Camera capture
- Recent detections and events display

**Vehicle Logs Component**:
- Historical detection logs
- Filtering and pagination

**Alerts Component**:
- Alert event display
- Time-based filtering

**Construction Site Component**:
- Live material truck tracking
- Material theft alerts
- Vendor analytics

---

## Flow Diagrams

### 1. Image Processing Flow

```
Image Input
    │
    ├─► File Upload
    ├─► Image URL
    └─► Camera Capture
         │
         ▼
    Image Decode (OpenCV)
         │
         ▼
    Resize (if > 1920x1080)
         │
         ▼
    ┌─────────────────┐
    │  Vision Agent   │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│Detector │      │OCR      │
│(YOLOv8) │      │(EasyOCR)│
└────┬────┘      └────┬────┘
     │                │
     │ ROI            │ Text
     └────────┬───────┘
              │
              ▼
    Combined Result
    (plate_text, confidence, bbox)
```

### 2. Agent Decision Flow

```
Plate Text
    │
    ▼
┌──────────────────┐
│ Validation Agent │
│                  │
│ - Regex check    │
│ - Normalize      │
└────────┬─────────┘
         │
         ├─► is_valid: false ──► LOG_ONLY
         │
         └─► is_valid: true
              │
              ▼
         ┌──────────────────┐
         │   Event Agent    │
         │                  │
         │ - Check rules    │
         │ - Check vehicle  │
         └────────┬─────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
    ┌─────────┐       ┌─────────┐
    │ALLOW    │       │ALERT    │
    │         │       │         │
    │Normal   │       │Blacklist│
    │entry    │       │Unauth.  │
    └─────────┘       └─────────┘
```

### 3. Construction Site Monitoring Flow

```
Events from API
    │
    ▼
┌─────────────────────────────┐
│ Construction Site Service   │
│                             │
│ 1. Filter invalid plates    │
│ 2. Track entry/exit state   │
│    (ALLOW events only)      │
│ 3. Calculate analytics      │
└───────────┬─────────────────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
┌─────────┐    ┌──────────────┐
│Live     │    │Theft Alerts  │
│Tracking │    │              │
│         │    │- Unauthorized│
│- Entry  │    │- No match    │
│- Exit   │    │- After hours │
└─────────┘    └──────────────┘
    │
    ▼
┌──────────────┐
│Vendor        │
│Analytics     │
│              │
│- Deliveries  │
│- Duration    │
│- Suspicious  │
└──────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.9/3.10**: Core language
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM
- **PostgreSQL**: Database
- **OpenCV (cv2)**: Image processing
- **Ultralytics YOLOv8**: Object detection
- **EasyOCR**: OCR engine
- **Pydantic**: Data validation

### Frontend
- **Angular 17**: Framework
- **TypeScript**: Language
- **RxJS**: Reactive programming
- **Angular Material**: UI components (optional)
- **HttpClient**: API communication

### Infrastructure
- **PostgreSQL**: Relational database
- **psycopg2-binary**: Database driver

---

## Key Design Patterns

### 1. Agent Pattern
- **Purpose**: Encapsulate business logic in independent, reusable agents
- **Benefits**: Modularity, testability, extensibility
- **Implementation**: Each agent is a Python class with clear input/output contracts

### 2. Layered Architecture
- **Purpose**: Separate concerns into distinct layers
- **Benefits**: Maintainability, scalability, clear boundaries
- **Implementation**: Strict import rules prevent cross-layer dependencies

### 3. Repository Pattern
- **Purpose**: Abstract database access
- **Benefits**: Database-agnostic business logic
- **Implementation**: SQLAlchemy ORM models and session management

### 4. Service Pattern (Frontend)
- **Purpose**: Centralize API communication
- **Benefits**: Reusability, maintainability
- **Implementation**: Angular services with RxJS observables

---

## Data Models

### Vehicle
```python
{
    id: int
    plate_number: str (unique)
    vehicle_type: str (optional)
    owner_name: str (optional)
    is_authorized: bool
    is_blacklisted: bool
    notes: str (optional)
    created_at: datetime
    updated_at: datetime
}
```

### Detection
```python
{
    id: int
    vehicle_id: int (optional, FK)
    plate_text: str
    confidence: float
    bbox_x1, bbox_y1, bbox_x2, bbox_y2: int
    image_path: str (optional)
    timestamp: datetime
}
```

### Event
```python
{
    id: int
    vehicle_id: int (optional, FK)
    detection_id: int (optional, FK)
    event_type: str ("ALLOW" | "ALERT" | "LOG_ONLY")
    description: str (optional)
    rule_name: str (optional)
    timestamp: datetime
}
```

---

## Configuration

### Rules Configuration (`config/rules.json`)
```json
{
    "blacklisted_plates": ["MH12AB9999"],
    "authorized_plates": ["MH12AB1234", "DL01CD5678"]
}
```

### Environment Variables (`.env`)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=anpr_db
DB_USER=postgres
DB_PASSWORD=postgres
```

---

## Error Handling

### Backend
- Centralized logging via `utils/logger.py`
- HTTP exceptions for API errors
- Graceful degradation (fallback strategies)
- Database rollback on errors

### Frontend
- Observable error handling (RxJS)
- User-friendly error messages
- Loading states
- Retry mechanisms

---

## Performance Optimizations

### Backend
- Image resizing (max 1920x1080)
- Fixed YOLO image size (640x640)
- Early exit on high confidence
- Combined database commits
- Reduced OCR preprocessing methods

### Frontend
- Auto-refresh with RxJS intervals
- Efficient change detection
- Lazy loading (future enhancement)

---

## Security Considerations

- No hardcoded credentials
- Environment variables for sensitive data
- Input validation (Pydantic schemas)
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration for API access

---

## Future Enhancements

1. **Multi-frame Tracking**: Track plates across multiple frames for better accuracy
2. **Real-time Streaming**: WebSocket support for live video streams
3. **Mobile App**: React Native or Flutter mobile application
4. **Advanced Analytics**: Machine learning for pattern detection
5. **Integration**: Gate control systems, SMS/Email alerts
6. **Caching**: Redis for frequently accessed data
7. **Load Balancing**: Multiple backend instances

---

## Conclusion

EagleEyeAI follows a clean, modular architecture with clear separation of concerns. The agent-based design allows for easy extension and maintenance. The layered architecture ensures scalability and testability. All components use open-source technologies, making the system cost-effective and accessible.
