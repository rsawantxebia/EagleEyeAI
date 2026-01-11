# ANPR System - Automatic Number Plate Recognition

A hackathon-ready ANPR (Automatic Number Plate Recognition) system built with free and open-source technologies. This system detects license plates from camera feeds, validates them, and makes rule-based decisions.

## Features

- **License Plate Detection**: Uses YOLOv8 for object detection
- **OCR Recognition**: EasyOCR for text extraction from license plates
- **Validation**: Regex-based validation for Indian number plate formats
- **Rule-based Events**: Decision making (ALLOW, ALERT, LOG_ONLY) based on configurable rules
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Angular Dashboard**: Modern web interface for monitoring and alerts
- **PostgreSQL Database**: Persistent storage for vehicles, detections, and events

## Architecture

```
ANPR System
├── src/
│   ├── vision/          # Computer vision layer (detection, OCR)
│   ├── agents/          # Business logic agents (vision, validation, event)
│   ├── backend/         # FastAPI REST API
│   └── database/        # Database models and access layer
├── frontend/angular-ui/ # Angular frontend application
├── config/              # Configuration files (rules.json)
├── utils/               # Utility modules (logger)
└── logs/                # Application logs
```

## Technology Stack

### Backend
- Python 3.9/3.10
- FastAPI
- SQLAlchemy (PostgreSQL)
- OpenCV
- YOLOv8 (Ultralytics)
- EasyOCR

### Frontend
- Angular 17
- TypeScript
- Angular Material (optional)

## Installation

### Prerequisites

- Python 3.9 or 3.10
- PostgreSQL database
- Node.js and npm (for Angular frontend)

### Backend Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
# Or with Python 3.9:
python3.9 -m pip install --user -r requirements.txt
```

2. Install and set up PostgreSQL:

   **Quick setup (macOS with Homebrew):**
   ```bash
   ./install_postgres.sh
   ```
   
   **Manual setup:**
   - macOS: `brew install postgresql@15 && brew services start postgresql@15`
   - Linux: `sudo apt install postgresql postgresql-contrib`
   - Windows: Download from https://www.postgresql.org/download/
   
   See `DATABASE_SETUP.md` for detailed instructions.

3. Configure database:
   ```bash
   # .env file is already created with default settings
   # Edit .env if your PostgreSQL credentials differ
   ```

4. Initialize database:
   ```bash
   python3.9 setup_database.py
   ```
   This will create the database and all necessary tables.

5. Run the backend server:
   ```bash
   python3.9 run.py
   ```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend/angular-ui
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:4200`

## Configuration

### Rules Configuration

Edit `config/rules.json` to configure event rules:

```json
{
  "event_rules": [...],
  "blacklisted_plates": ["MH12AB1234"],
  "authorized_plates": []
}
```

## API Endpoints

- `GET /api/detections` - Get all detections
- `GET /api/events` - Get all events
- `POST /api/detect` - Trigger detection
- `GET /api/alerts` - Get alert events

See `/docs` for interactive API documentation.

## Database Schema

- **vehicles**: Registered vehicle information
- **detections**: License plate detection results
- **events**: System events and decisions

## Usage

1. Start the backend server
2. Start the frontend development server
3. Open `http://localhost:4200` in your browser
4. Use the dashboard to view detections and events
5. Trigger detections using the API or dashboard

## Demo Notes

- For demo purposes, mock data may be used if camera hardware is unavailable
- The system is optimized for CPU execution (laptop-friendly)
- All processing happens locally (no paid APIs)

## Development

- Backend code follows strict separation of concerns
- Agents are independent and don't directly access database or camera
- Vision layer outputs standardized format
- All errors are logged via `utils/logger.py`

## License

This project is built for hackathon demonstration purposes.
