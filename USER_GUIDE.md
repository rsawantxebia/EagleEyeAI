# EagleEyeAI User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard - License Plate Detection](#dashboard---license-plate-detection)
3. [Understanding Detection Results](#understanding-detection-results)
4. [Vehicle Logs](#vehicle-logs)
5. [Alerts](#alerts)
6. [Construction Site Monitoring](#construction-site-monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing the Application

1. **Start the Backend Server** (if not already running):
   ```bash
   python3.9 run.py
   ```
   The backend will be available at `http://localhost:8000`

2. **Start the Frontend Application** (if not already running):
   ```bash
   cd frontend/angular-ui
   npm start
   ```
   The frontend will open automatically at `http://localhost:4200`

3. **Open in Browser**: Navigate to `http://localhost:4200` if it doesn't open automatically

---

## Dashboard - License Plate Detection

The Dashboard is the main interface for detecting license plates. You can detect plates using two methods:

### Method 1: Upload an Image File

**Step-by-Step Instructions:**

1. **Navigate to Dashboard**:
   - Click on the "Dashboard" tab in the navigation bar (top of the page)

2. **Select an Image File**:
   - Click on the "Choose File" button or the file input field
   - Browse your computer to find an image file containing an Indian license plate
   - Supported formats: JPG, JPEG, PNG
   - **Recommended**: Clear, well-lit images with the license plate visible

3. **Upload and Detect**:
   - After selecting the file, click the "Upload Image" button
   - The system will automatically:
     - Upload the image to the backend
     - Process it using YOLOv8 detection and EasyOCR
     - Validate the plate format
     - Make a decision (ALLOW/ALERT/LOG_ONLY)
     - Save the detection and event to the database

4. **View Results**:
   - The detection result will appear in the "Recent Detections" section
   - The corresponding event will appear in the "Recent Events" section
   - The page will automatically refresh to show the new data

**Best Practices for Image Upload:**
- Use clear, high-resolution images
- Ensure the license plate is fully visible
- Good lighting conditions improve accuracy
- Avoid blurry or angled images
- Indian license plates work best (format: XX##XX####, e.g., MH12AB1234)

### Method 2: Capture Using Frontend Camera

**Step-by-Step Instructions:**

1. **Navigate to Dashboard**:
   - Click on the "Dashboard" tab in the navigation bar

2. **Start Camera**:
   - Click the "Use Camera" button
   - Your browser will ask for camera permission - click "Allow"
   - The camera feed will appear in a preview window
   - Position the license plate in the camera view

3. **Capture Photo**:
   - Once the license plate is clearly visible in the camera preview
   - Click the "Capture & Detect" button
   - The system will:
     - Capture the current frame from your camera
     - Automatically stop the camera
     - Process the captured image
     - Detect and recognize the license plate
     - Display results in the dashboard

4. **Cancel Camera** (if needed):
   - Click the "Cancel" button to stop the camera without capturing
   - The camera will close and return to the normal view

**Camera Tips:**
- Use good lighting
- Hold the camera steady
- Ensure the license plate fills a reasonable portion of the frame
- Wait for the camera to focus before capturing
- The camera automatically stops after capture

**Troubleshooting Camera:**
- If camera doesn't start: Check browser permissions in settings
- If "Permission denied": Allow camera access in browser settings
- If camera is blurry: Ensure good lighting and wait for autofocus
- If detection fails: Try capturing again with better lighting/angle

---

## Understanding Detection Results

### Recent Detections Section

The "Recent Detections" section shows all license plate detections in reverse chronological order (newest first).

**Information Displayed:**

1. **Plate Number**: The detected license plate text (e.g., MH12AB1234)
   - This is the OCR result after character correction
   - Format: Indian number plate format (State Code + District + Series + Number)

2. **Confidence**: A score between 0.0 and 1.0 indicating detection accuracy
   - **0.90 - 1.0**: Very high confidence (excellent detection)
   - **0.75 - 0.89**: High confidence (good detection)
   - **0.60 - 0.74**: Medium confidence (acceptable detection)
   - **Below 0.60**: Low confidence (may need verification)

3. **Timestamp**: Date and time when the detection occurred
   - Format: Date and time in your local timezone
   - Shows when the image was processed

4. **Bounding Box**: Coordinates of the detected license plate in the image
   - Technical information (x1, y1, x2, y2)
   - Used internally for image processing

**What Each Detection Means:**
- Each row represents one successful license plate detection
- Detections are saved to the database for historical tracking
- You can click on detections to see more details (if implemented)

### Recent Events Section

The "Recent Events" section shows system decisions made for each detection.

**Event Types:**

1. **ALLOW** (Green badge):
   - **Meaning**: Vehicle is authorized and allowed entry/exit
   - **When it occurs**: 
     - Plate format is valid
     - Vehicle is in authorized list (if configured)
     - Vehicle is not blacklisted
   - **Action**: Normal operation, vehicle can proceed

2. **ALERT** (Red badge):
   - **Meaning**: Security alert - requires attention
   - **When it occurs**:
     - Vehicle is blacklisted
     - Vehicle is unauthorized (not in authorized list)
     - Suspicious activity detected
   - **Action**: Security should be notified, vehicle should be stopped

3. **LOG_ONLY** (Blue badge):
   - **Meaning**: Event logged but no action required
   - **When it occurs**:
     - Plate format is invalid
     - Suspicious but not critical activity
     - System logging for audit purposes
   - **Action**: Review later, no immediate action needed

**Information Displayed:**

1. **Event Type**: ALLOW, ALERT, or LOG_ONLY
2. **Description**: Human-readable explanation of the event
3. **Rule Name**: The rule that triggered this event (e.g., "normal_entry", "blacklisted_vehicle")
4. **Timestamp**: When the event occurred
5. **Plate Number**: The license plate that triggered the event

**Understanding Event Flow:**
```
Image Upload/Capture
    ↓
Detection (OCR)
    ↓
Validation (Format Check)
    ↓
Event Decision (ALLOW/ALERT/LOG_ONLY)
    ↓
Saved to Database
    ↓
Displayed in Events Section
```

---

## Vehicle Logs

The Vehicle Logs page shows a comprehensive history of all detections.

**How to Access:**
- Click on "Vehicle Logs" in the navigation bar

**Features:**
- **Pagination**: Browse through historical detections
- **Filtering**: Filter by date range, plate number, or event type (if implemented)
- **Search**: Search for specific license plates
- **Export**: Export logs for reporting (if implemented)

**Information Available:**
- Complete detection history
- All events associated with each detection
- Vehicle information (if registered)
- Timestamps for all activities
- Confidence scores for accuracy tracking

**Use Cases:**
- Review historical access records
- Audit trail for security purposes
- Track specific vehicles over time
- Generate reports for management

---

## Alerts

The Alerts page shows all security alerts that require attention.

**How to Access:**
- Click on "Alerts" in the navigation bar

**Alert Types:**

1. **Blacklisted Vehicle Alert**:
   - Vehicle is on the blacklist
   - Immediate security action required
   - Description: "Blacklisted vehicle detected: [PLATE]"

2. **Unauthorized Entry Alert**:
   - Vehicle not in authorized list
   - May require verification
   - Description: "Unauthorized vehicle detected: [PLATE]"

3. **Invalid Plate Format Alert**:
   - Plate doesn't match Indian format
   - May indicate fake or damaged plate
   - Description: "Invalid plate format detected"

**Alert Information:**
- **Plate Number**: The license plate that triggered the alert
- **Alert Type**: Category of the alert
- **Description**: Detailed explanation
- **Timestamp**: When the alert occurred
- **Rule Name**: Which rule triggered the alert

**Actions:**
- Review alerts regularly
- Take appropriate security measures
- Update blacklist/authorized lists as needed
- Export alerts for reporting

---

## Construction Site Monitoring

The Construction Site Monitoring tab provides specialized tracking for construction site operations, replacing manual entry registers with automated ANPR tracking.

### How to Access

1. Click on "Construction Site" in the navigation bar
2. The page will load with three main sections

### Section A: Live Material Truck Tracking

**Purpose**: Real-time tracking of all vehicle movements at the construction site.

**What You'll See:**

A table showing all vehicle movements with the following columns:

1. **Plate Number**: The detected license plate (e.g., MH04MF2221)
2. **Vehicle Category**: 
   - **Material Truck**: Delivery vehicles carrying construction materials
   - **Machinery**: Construction equipment (excavators, cranes)
   - **Staff**: Employee vehicles
   - **Unknown**: Unclassified vehicles
3. **Entry/Exit**: 
   - **Entry**: Vehicle entering the construction site
   - **Exit**: Vehicle leaving the construction site
4. **Gate Name**: Which gate the vehicle used (e.g., "Main Gate", "Gate 1")
5. **Time**: Timestamp of the movement
6. **Decision**: 
   - **ALLOW**: Authorized movement
   - **ALERT**: Unauthorized or suspicious movement
   - **LOG_ONLY**: Logged for record-keeping

**How to Review Entry and Exit Records:**

1. **Understanding Entry/Exit Tracking**:
   - The system automatically tracks when vehicles enter and exit
   - **Entry**: First detection of a vehicle or detection after 2+ hours gap
   - **Exit**: Subsequent detection of same vehicle within 2 hours
   - Only **ALLOW** events are used for entry/exit tracking (authorized movements)

2. **Reviewing Records**:
   - Scroll through the table to see all movements
   - Look for patterns:
     - Vehicles that entered but haven't exited (still on site)
     - Vehicles that exited without entry (potential security issue)
     - Frequent entries/exits (delivery patterns)

3. **Identifying Issues**:
   - **Missing Exit**: Vehicle entered but no exit recorded (check if still on site)
   - **Unexpected Exit**: Exit without matching entry (investigate)
   - **After-Hours Movement**: Exits outside 6 AM - 8 PM (check alerts)

**Best Practices:**
- Review the table regularly to monitor site activity
- Check for vehicles that entered but haven't exited
- Verify that all material deliveries have corresponding entries
- Use the data to track vendor delivery patterns

### Section B: Material Theft Alerts

**Purpose**: Real-time alerts for unauthorized material movements.

**What You'll See:**

Alert cards highlighting suspicious activities:

1. **Unauthorized Exit Alert**:
   - Vehicle exiting with ALERT decision
   - Indicates unauthorized material movement
   - Message: "Unauthorized material movement detected"

2. **No Matching Entry Alert**:
   - Vehicle exited without a recorded entry
   - Potential fake delivery claim
   - Message: "Vehicle exited without recorded entry"

3. **After Hours Exit Alert**:
   - Exit detected outside working hours (6 AM - 8 PM)
   - Suspicious timing
   - Message: "Material movement detected outside working hours"

**Alert Information:**
- **Alert Type**: Category of the alert
- **Plate Number**: Vehicle involved
- **Time**: When the alert occurred
- **Message**: Description of the issue

**Auto-Refresh:**
- Alerts automatically refresh every 5 seconds
- New alerts appear immediately
- Red highlighting draws attention to critical issues

**Actions to Take:**
- Review alerts immediately
- Verify with security personnel
- Check gate logs if available
- Update vehicle authorization status if needed

### Section C: Vendor-Wise Delivery Analytics

**Purpose**: Track vendor deliveries to prevent fake delivery claims.

**What You'll See:**

Summary cards for each vendor showing:

1. **Vendor Name**: Derived from license plate state code
   - Example: "Maharashtra" (from MH), "Delhi" (from DL)
   - Each state represents a vendor

2. **Deliveries Today**: Number of deliveries made today
   - Counts entry events for today
   - Helps track daily delivery volume

3. **Average Duration**: Average time vehicles spend on site
   - Calculated from entry to exit time
   - Helps identify suspiciously short or long stays
   - Format: "Xh Ymin" or "X min"

4. **Suspicious Exits**: Number of ALERT exits for this vendor
   - High number indicates potential issues
   - Requires investigation

5. **Last Delivery Time**: Most recent delivery timestamp
   - Helps track vendor activity patterns

**How to Use Vendor Analytics:**

1. **Review Delivery Patterns**:
   - Check which vendors deliver most frequently
   - Identify vendors with unusual patterns
   - Track delivery times and durations

2. **Detect Fake Deliveries**:
   - Look for vendors with high "Suspicious Exits"
   - Check for entries without matching exits
   - Verify delivery durations (too short = suspicious)

3. **Monitor Vendor Performance**:
   - Track delivery frequency
   - Monitor average delivery duration
   - Identify reliable vs. problematic vendors

**Example Scenarios:**

- **Normal Delivery**: Entry → Exit within 30-60 minutes (unloading time)
- **Suspicious**: Entry → Exit within 5 minutes (may not have delivered)
- **Fake Delivery**: Exit without entry (claiming delivery without entering)

---

## Troubleshooting

### Detection Issues

**Problem**: No plate detected in image
- **Solution**: 
  - Ensure license plate is clearly visible
  - Use better lighting
  - Try a different angle
  - Use higher resolution image

**Problem**: Incorrect plate text detected
- **Solution**:
  - Image quality may be poor
  - Try preprocessing the image (better lighting, contrast)
  - Ensure plate is not at extreme angles
  - System includes character correction, but accuracy depends on image quality

**Problem**: Low confidence scores
- **Solution**:
  - Improve image quality
  - Better lighting conditions
  - Ensure plate is in focus
  - Avoid blurry images

### Camera Issues

**Problem**: Camera doesn't start
- **Solution**:
  - Check browser permissions (Settings → Privacy → Camera)
  - Allow camera access when prompted
  - Try a different browser
  - Ensure no other application is using the camera

**Problem**: Camera is blurry
- **Solution**:
  - Wait for autofocus to complete
  - Improve lighting
  - Hold camera steady
  - Move closer to the license plate

**Problem**: Detection fails with camera
- **Solution**:
  - Ensure good lighting
  - Wait for camera to focus before capturing
  - Try capturing multiple times
  - Use the upload method as alternative

### Application Issues

**Problem**: Frontend can't connect to backend
- **Solution**:
  - Ensure backend is running on `http://localhost:8000`
  - Check backend logs for errors
  - Verify CORS settings
  - Check browser console for errors

**Problem**: Data not refreshing
- **Solution**:
  - Refresh the page manually
  - Check if backend is responding
  - Clear browser cache
  - Check browser console for errors

**Problem**: Construction Site tab shows no data
- **Solution**:
  - Ensure you have events in the database
  - Run `python3.9 seed_database.py` to populate sample data
  - Check that events have valid plate numbers
  - Verify backend API is working

---

## Tips for Best Results

### Image Quality
- **Resolution**: Use images with at least 640x480 pixels
- **Lighting**: Ensure good, even lighting on the license plate
- **Angle**: License plate should be relatively straight (not heavily angled)
- **Focus**: Image should be in focus, not blurry
- **Contrast**: Good contrast between plate background and text

### Indian License Plate Format
- **Format**: XX##XX#### (e.g., MH12AB1234)
  - XX: State code (2 letters)
  - ##: District code (2 digits)
  - XX: Series (1-2 letters)
  - ####: Number (1-4 digits)
- **Examples**: MH12AB1234, DL01CD5678, KA03EF9012

### Construction Site Monitoring
- **Regular Review**: Check entry/exit records daily
- **Alert Response**: Respond to alerts promptly
- **Vendor Tracking**: Monitor vendor analytics weekly
- **Data Verification**: Cross-check with physical gate logs if available

---

## Support

For technical issues or questions:
- Check the browser console for error messages
- Review backend logs in the `logs/` directory
- Consult the `ARCHITECTURE.md` for technical details
- Check `README.md` for setup instructions

---

## Quick Reference

### Keyboard Shortcuts
- **Refresh Page**: F5 or Ctrl+R (Cmd+R on Mac)
- **Open Developer Tools**: F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)

### Important URLs
- **Frontend**: `http://localhost:4200`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### Common Tasks
1. **Detect a plate**: Dashboard → Upload Image or Use Camera
2. **View history**: Vehicle Logs tab
3. **Check alerts**: Alerts tab
4. **Monitor site**: Construction Site tab
5. **Review entries/exits**: Construction Site → Live Material Truck Tracking table

---

**Last Updated**: 2026-01-12
**Version**: 1.0.0
**Application**: EagleEyeAI
