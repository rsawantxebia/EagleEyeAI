# EagleEyeAI - Automatic Number Plate Recognition System

EagleEyeAI is a hackathon-ready ANPR (Automatic Number Plate Recognition) system built with free and open-source technologies. This system detects license plates from camera feeds, validates them, and makes rule-based decisions.

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
EagleEyeAI
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
   
   The backend server will start on `http://localhost:8000`
   - API Base URL: `http://localhost:8000/api`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

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

## Running the Application

### Start Backend Server

1. Open a terminal window
2. Navigate to the project root directory:
   ```bash
   cd /path/to/ANPR
   ```
3. Start the FastAPI backend:
   ```bash
   python3.9 run.py
   ```
   
   You should see output like:
   ```
   INFO:     Started server process [xxxxx]
   INFO:     Waiting for application startup.
   INFO:     EagleEyeAI API started successfully
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   ```

4. Verify the backend is running:
   - Open `http://localhost:8000/docs` in your browser to see the interactive API documentation
   - Or check `http://localhost:8000/health` for a health check

### Start Frontend Application

1. Open a **new terminal window** (keep the backend running)
2. Navigate to the frontend directory:
   ```bash
   cd /path/to/ANPR/frontend/angular-ui
   ```
3. Start the Angular development server:
   ```bash
   npm start
   ```
   
   You should see output like:
   ```
   ** Angular Live Development Server is listening on localhost:4200 **
   ```
   
   The application will automatically open in your browser at `http://localhost:4200`

4. If the browser doesn't open automatically, manually navigate to:
   ```
   http://localhost:4200
   ```

### Accessing the Application

Once both servers are running:

- **Frontend Dashboard**: `http://localhost:4200`
  - Dashboard: View recent detections and events
  - Vehicle Logs: Browse historical detection records
  - Alerts: Monitor security alerts
  - Construction Site: Construction site monitoring features

- **Backend API**: `http://localhost:8000`
  - API Documentation: `http://localhost:8000/docs` (Swagger UI)
  - Alternative Docs: `http://localhost:8000/redoc` (ReDoc)
  - Health Check: `http://localhost:8000/health`

### Stopping the Applications

- **Backend**: Press `CTRL+C` in the backend terminal
- **Frontend**: Press `CTRL+C` in the frontend terminal

### Troubleshooting

**Backend won't start:**
- Check if port 8000 is already in use: `lsof -i :8000`
- Kill the process if needed: `kill -9 <PID>`
- Ensure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)

**Frontend won't start:**
- Check if port 4200 is already in use: `lsof -i :4200`
- Kill the process if needed: `kill -9 <PID>`
- Clear Angular cache: `rm -rf node_modules/.angular`
- Reinstall dependencies: `rm -rf node_modules && npm install`

**Connection errors between frontend and backend:**
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in `src/backend/main.py`
- Verify API URL in `frontend/angular-ui/src/app/services/anpr.service.ts`

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
