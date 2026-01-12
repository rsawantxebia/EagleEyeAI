# Construction Site Monitoring - ANPR Solution

## Overview

The Construction Site Monitoring feature demonstrates how ANPR (Automatic Number Plate Recognition) technology solves real-world problems at Indian construction sites using only open-source technology.

## Problems Solved

### 1. Material Theft Prevention
**Problem:** Unauthorized exit of trucks carrying construction materials
**ANPR Solution:** 
- Automatically tracks all material trucks entering and exiting the site
- Detects unauthorized exits in real-time
- Alerts security when suspicious material movements are detected
- Maintains complete audit trail for investigation

### 2. Fake Delivery Claims Prevention
**Problem:** Trucks claiming delivery without valid entry records
**ANPR Solution:**
- Tracks vendor-wise delivery analytics using historical data
- Identifies trucks that exit without matching entry records
- Provides delivery duration analytics to detect anomalies
- Prevents fake delivery claims through automated verification

### 3. Manual Entry Register Replacement
**Problem:** Paper-based, error-prone manual entry logs
**ANPR Solution:**
- Replaces manual registers with automated ANPR tracking
- Real-time tracking of all material trucks
- Automatic logging of plate number, vehicle category, direction, gate, and time
- Eliminates human error and provides digital audit trail

## Implementation Details

### Files Created

1. **Service:** `frontend/angular-ui/src/app/services/construction-site.service.ts`
   - Fetches and transforms event data from `/api/events`
   - Provides observables for real-time monitoring
   - Implements vendor analytics calculations
   - Detects material theft alerts

2. **Component:** `frontend/angular-ui/src/app/components/construction-site/construction-site.component.ts`
   - Presentational component (no business logic)
   - Manages UI state and data display
   - Auto-refreshes alerts every 5 seconds

3. **Template:** `frontend/angular-ui/src/app/components/construction-site/construction-site.component.html`
   - Three sections: Live Tracking, Theft Alerts, Vendor Analytics
   - Responsive design with loading and error states

4. **Styles:** `frontend/angular-ui/src/app/components/construction-site/construction-site.component.css`
   - Modern, clean UI design
   - Color-coded alerts and decisions
   - Responsive layout for mobile devices

### Features

#### Section A: Live Material Truck Tracking
- Real-time table showing all vehicle movements
- Displays: Plate Number, Vehicle Category, Entry/Exit, Gate Name, Time, Decision
- Replaces manual entry registers
- Data source: `/api/events` endpoint

#### Section B: Material Theft Alerts
- Highlights unauthorized exits
- Detects three types of alerts:
  1. Unauthorized Exit (ALERT decision on exit)
  2. No Matching Entry (exit without recorded entry)
  3. After Hours Exit (exits outside 6 AM - 8 PM)
- Auto-refreshes every 5 seconds
- Red highlight with warning icons

#### Section C: Vendor-Wise Delivery Analytics
- Summary cards for each vendor
- Metrics displayed:
  - Number of deliveries today
  - Average delivery duration
  - Suspicious exits count
  - Last delivery time
- Vendor name derived from plate state code (first 2 characters)
- Prevents fake delivery claims through historical tracking

## Technical Architecture

### Data Flow
1. Frontend requests events from `/api/events`
2. `ConstructionSiteService` transforms events to construction site format
3. Component displays data in three sections
4. Auto-refresh for alerts using RxJS intervals

### Key Design Decisions

1. **No Backend Changes:** All logic is in frontend service layer
2. **Presentational Components:** UI components only display data, no business logic
3. **Vendor Mapping:** Uses Indian state codes (first 2 chars of plate) to identify vendors
4. **Alert Detection:** Client-side logic identifies suspicious patterns from event data
5. **Auto-Refresh:** Uses RxJS `interval` and `switchMap` for efficient polling

## Usage

1. Navigate to "Construction Site" tab in the Angular application
2. View live material truck tracking in Section A
3. Monitor material theft alerts in Section B (auto-refreshes every 5 seconds)
4. Review vendor analytics in Section C

## ANPR Benefits Demonstrated

1. **Automation:** Eliminates manual data entry
2. **Accuracy:** No human error in logging
3. **Real-time:** Immediate alerts on suspicious activity
4. **Audit Trail:** Complete digital record of all movements
5. **Analytics:** Historical data analysis for pattern detection
6. **Cost-effective:** Uses only open-source technology

## Future Enhancements (Not Implemented)

- Integration with gate control systems
- SMS/Email alerts for security
- Advanced analytics dashboards
- Integration with material inventory systems
- Mobile app for security guards

## Notes

- All data is derived from existing `/api/events` endpoint
- No backend modifications were made
- Vendor identification uses plate number prefixes (Indian state codes)
- Alert detection is based on event patterns and timestamps
- The solution is fully functional with existing ANPR pipeline
