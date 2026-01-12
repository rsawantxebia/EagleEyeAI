import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { map, startWith, switchMap } from 'rxjs/operators';
import { AnprService, Event } from './anpr.service';

/**
 * Construction Site Event - Extended event with construction site specific fields
 * ANPR Solution: Replaces manual entry registers with automated tracking
 */
export interface ConstructionSiteEvent {
  id: number;
  plateNumber: string;
  vehicleCategory: 'Material Truck' | 'Machinery' | 'Staff' | 'Unknown';
  direction: 'Entry' | 'Exit';
  gateName: string; // Derived from source_id or rule_name
  timestamp: string;
  decision: 'ALLOW' | 'ALERT' | 'LOG_ONLY';
  eventType: string;
  description?: string;
  ruleName?: string;
}

/**
 * Material Theft Alert - Unauthorized exit detection
 * ANPR Solution: Prevents material theft by detecting unauthorized exits
 */
export interface MaterialTheftAlert {
  id: number;
  plateNumber: string;
  alertType: 'Unauthorized Exit' | 'No Matching Entry' | 'After Hours Exit';
  message: string;
  timestamp: string;
  description?: string;
}

/**
 * Vendor Delivery Analytics - Delivery tracking by vendor
 * ANPR Solution: Prevents fake delivery claims using historical data
 */
export interface VendorAnalytics {
  vendorName: string;
  deliveriesToday: number;
  averageDuration?: number; // in minutes
  suspiciousExits: number;
  lastDeliveryTime?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ConstructionSiteService {
  private apiUrl = 'http://localhost:8000/api';
  
  // Indian state codes for vendor mapping (first 2 chars of plate)
  private stateCodes: { [key: string]: string } = {
    'MH': 'Maharashtra',
    'DL': 'Delhi',
    'KA': 'Karnataka',
    'TN': 'Tamil Nadu',
    'GJ': 'Gujarat',
    'RJ': 'Rajasthan',
    'UP': 'Uttar Pradesh',
    'WB': 'West Bengal',
    'MP': 'Madhya Pradesh',
    'AP': 'Andhra Pradesh',
    'TS': 'Telangana',
    'KL': 'Kerala',
    'HR': 'Haryana',
    'PB': 'Punjab',
    'OR': 'Odisha',
    'BR': 'Bihar',
    'AS': 'Assam',
    'JH': 'Jharkhand',
    'UT': 'Uttarakhand',
    'HP': 'Himachal Pradesh'
  };

  constructor(
    private http: HttpClient,
    private anprService: AnprService
  ) { }

  /**
   * Get all construction site events
   * Filters events that could be from construction site monitoring
   * ANPR Solution: Replaces manual entry registers
   */
  getConstructionSiteEvents(limit: number = 100): Observable<ConstructionSiteEvent[]> {
    return this.anprService.getEvents(limit, 0).pipe(
      map(events => this.transformToConstructionSiteEvents(events))
    );
  }

  /**
   * Get construction site events with auto-refresh
   * Auto-refreshes every 5 seconds for real-time monitoring
   */
  getConstructionSiteEventsAutoRefresh(intervalMs: number = 5000): Observable<ConstructionSiteEvent[]> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getConstructionSiteEvents(100))
    );
  }

  /**
   * Get material theft alerts
   * ANPR Solution: Detects unauthorized exits to prevent material theft
   */
  getMaterialTheftAlerts(limit: number = 50): Observable<MaterialTheftAlert[]> {
    return this.getConstructionSiteEvents(limit).pipe(
      map(events => this.identifyTheftAlerts(events))
    );
  }

  /**
   * Get material theft alerts with auto-refresh (every 5 seconds)
   */
  getMaterialTheftAlertsAutoRefresh(intervalMs: number = 5000): Observable<MaterialTheftAlert[]> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getMaterialTheftAlerts(50))
    );
  }

  /**
   * Get vendor-wise delivery analytics
   * ANPR Solution: Prevents fake delivery claims using historical tracking
   */
  getVendorAnalytics(): Observable<VendorAnalytics[]> {
    return this.getConstructionSiteEvents(200).pipe(
      map(events => this.calculateVendorAnalytics(events))
    );
  }

  /**
   * Transform API events to construction site events
   * Derives vehicle category, direction, and gate name from event data
   * ANPR Solution: Tracks Entry/Exit by matching plate numbers and timestamps
   * Only ALLOW events are used for entry/exit tracking (authorized movements)
   */
  private transformToConstructionSiteEvents(events: Event[]): ConstructionSiteEvent[] {
    // Sort events by timestamp (oldest first) to track entry/exit sequence
    const sortedEvents = [...events].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    
    // Track vehicle entries to determine exits (only for ALLOW events)
    const vehicleEntries = new Map<string, {
      firstSeen: Date;
      lastSeen: Date;
      entryCount: number;
      exitCount: number;
    }>();
    
    const result: ConstructionSiteEvent[] = [];
    
    sortedEvents.forEach(event => {
      const plateNumber = event.plate_text || 'UNKNOWN';
      if (plateNumber === 'UNKNOWN') {
        return; // Skip unknown plates
      }
      
      // Skip events with invalid plate format (don't track these as entries/exits)
      const gateName = this.determineGateName(event.rule_name, event.description);
      if (gateName === 'Gate invalid_plate_format' || event.rule_name === 'invalid_plate_format') {
        return; // Skip invalid plate format events
      }
      
      const eventTime = new Date(event.timestamp);
      const isAllowEvent = event.event_type === 'ALLOW';
      
      // Only track entry/exit state for ALLOW events (authorized movements)
      if (isAllowEvent) {
        // Initialize tracking for this plate if not seen before
        if (!vehicleEntries.has(plateNumber)) {
          vehicleEntries.set(plateNumber, {
            firstSeen: eventTime,
            lastSeen: eventTime,
            entryCount: 0,
            exitCount: 0
          });
        }
        
        const vehicleState = vehicleEntries.get(plateNumber)!;
        const timeSinceLastSeen = eventTime.getTime() - vehicleState.lastSeen.getTime();
        const timeSinceFirstSeen = eventTime.getTime() - vehicleState.firstSeen.getTime();
        
        // Determine direction based on vehicle state and timing (only for ALLOW events)
        let direction: 'Entry' | 'Exit';
        
        // Strategy 1: If this is the first time seeing this plate, it's an Entry
        if (vehicleState.entryCount === 0 && vehicleState.exitCount === 0) {
          direction = 'Entry';
          vehicleState.entryCount++;
        }
        // Strategy 2: If last seen more than 2 hours ago, treat as new Entry
        else if (timeSinceLastSeen > 2 * 60 * 60 * 1000) {
          direction = 'Entry';
          vehicleState.entryCount++;
          vehicleState.firstSeen = eventTime; // Reset first seen time
        }
        // Strategy 3: If we have more entries than exits, this is likely an Exit
        else if (vehicleState.entryCount > vehicleState.exitCount) {
          direction = 'Exit';
          vehicleState.exitCount++;
        }
        // Strategy 4: Check description for explicit direction indicators
        else {
          const desc = (event.description || '').toLowerCase();
          if (desc.includes('exit') || desc.includes('departure') || desc.includes('leaving')) {
            direction = 'Exit';
            vehicleState.exitCount++;
          } else if (desc.includes('entry') || desc.includes('arrival') || desc.includes('entering')) {
            direction = 'Entry';
            vehicleState.entryCount++;
          }
          // Strategy 5: If time since first seen is short (< 30 min), likely still entry sequence
          else if (timeSinceFirstSeen < 30 * 60 * 1000) {
            direction = 'Entry';
            vehicleState.entryCount++;
          }
          // Strategy 6: Default to Entry if uncertain
          else {
            direction = 'Entry';
            vehicleState.entryCount++;
          }
        }
        
        // Update last seen time (only for ALLOW events)
        vehicleState.lastSeen = eventTime;
        
        // Determine vehicle category from plate or description
        const vehicleCategory = this.determineVehicleCategory(plateNumber, event.description);
        
        // Gate name already determined above (before the isAllowEvent check)
        
        result.push({
          id: event.id,
          plateNumber: plateNumber,
          vehicleCategory: vehicleCategory,
          direction: direction,
          gateName: gateName,
          timestamp: event.timestamp,
          decision: event.event_type as 'ALLOW' | 'ALERT' | 'LOG_ONLY',
          eventType: event.event_type,
          description: event.description,
          ruleName: event.rule_name
        });
      } else {
        // For non-ALLOW events (ALERT, LOG_ONLY), still display them but don't track entry/exit
        // These events are shown for monitoring but don't affect entry/exit state
        // Skip invalid plate format events even for display
        if (gateName === 'Gate invalid_plate_format' || event.rule_name === 'invalid_plate_format') {
          return; // Skip invalid plate format events
        }
        
        const vehicleCategory = this.determineVehicleCategory(plateNumber, event.description);
        
        // For ALERT events, try to infer direction from context
        let direction: 'Entry' | 'Exit' = 'Entry'; // Default
        if (event.event_type === 'ALERT') {
          const desc = (event.description || '').toLowerCase();
          if (desc.includes('exit') || desc.includes('departure') || desc.includes('leaving')) {
            direction = 'Exit';
          } else if (desc.includes('entry') || desc.includes('arrival') || desc.includes('entering')) {
            direction = 'Entry';
          } else {
            // ALERT events without explicit direction are typically unauthorized exits
            direction = 'Exit';
          }
        }
        
        result.push({
          id: event.id,
          plateNumber: plateNumber,
          vehicleCategory: vehicleCategory,
          direction: direction,
          gateName: gateName,
          timestamp: event.timestamp,
          decision: event.event_type as 'ALLOW' | 'ALERT' | 'LOG_ONLY',
          eventType: event.event_type,
          description: event.description,
          ruleName: event.rule_name
        });
      }
    });
    
    // Sort result by timestamp (newest first) for display
    return result.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  /**
   * Determine vehicle category from plate number or description
   * Material trucks typically have specific patterns or are mentioned in description
   */
  private determineVehicleCategory(plateNumber: string, description?: string): 'Material Truck' | 'Machinery' | 'Staff' | 'Unknown' {
    const desc = (description || '').toLowerCase();
    const plate = plateNumber.toUpperCase();
    
    // Check description for keywords
    if (desc.includes('truck') || desc.includes('material') || desc.includes('delivery')) {
      return 'Material Truck';
    }
    if (desc.includes('machinery') || desc.includes('excavator') || desc.includes('crane')) {
      return 'Machinery';
    }
    if (desc.includes('staff') || desc.includes('employee') || desc.includes('personnel')) {
      return 'Staff';
    }
    
    // Default: Material Truck for construction site context
    // (most vehicles at construction sites are material trucks)
    return 'Material Truck';
  }

  /**
   * Determine direction (Entry/Exit) from event type or description
   * NOTE: This method is now deprecated - direction is determined in transformToConstructionSiteEvents
   * using state-based tracking. Kept for backward compatibility.
   */
  private determineDirection(eventType: string, description?: string): 'Entry' | 'Exit' {
    const desc = (description || '').toLowerCase();
    
    if (desc.includes('exit') || desc.includes('departure') || desc.includes('leaving')) {
      return 'Exit';
    }
    if (desc.includes('entry') || desc.includes('arrival') || desc.includes('entering')) {
      return 'Entry';
    }
    
    // Default based on event type
    if (eventType === 'ALERT') {
      // Alerts often indicate unauthorized exits
      return 'Exit';
    }
    
    // Default to Entry (most events are entries)
    return 'Entry';
  }

  /**
   * Determine gate name from rule_name or description
   */
  private determineGateName(ruleName?: string, description?: string): string {
    if (ruleName) {
      // Rule name might contain gate information
      if (ruleName.toLowerCase().includes('gate')) {
        return ruleName;
      }
      return `Gate ${ruleName}`;
    }
    
    if (description) {
      // Try to extract gate name from description
      const gateMatch = description.match(/gate\s*([a-z0-9]+)/i);
      if (gateMatch) {
        return `Gate ${gateMatch[1]}`;
      }
    }
    
    // Default gate name
    return 'Main Gate';
  }

  /**
   * Identify material theft alerts
   * ANPR Solution: Detects unauthorized exits without matching entries
   */
  private identifyTheftAlerts(events: ConstructionSiteEvent[]): MaterialTheftAlert[] {
    const alerts: MaterialTheftAlert[] = [];
    const plateEntries = new Map<string, ConstructionSiteEvent[]>();
    
    // Group events by plate number
    events.forEach(event => {
      if (!plateEntries.has(event.plateNumber)) {
        plateEntries.set(event.plateNumber, []);
      }
      plateEntries.get(event.plateNumber)!.push(event);
    });
    
    // Check each plate for suspicious activity
    plateEntries.forEach((plateEvents, plateNumber) => {
      const exits = plateEvents.filter(e => e.direction === 'Exit' && e.decision === 'ALERT');
      const entries = plateEvents.filter(e => e.direction === 'Entry');
      
      // Alert 1: Unauthorized exits (ALERT decision on exit)
      exits.forEach(exitEvent => {
        alerts.push({
          id: exitEvent.id,
          plateNumber: plateNumber,
          alertType: 'Unauthorized Exit',
          message: 'Unauthorized material movement detected',
          timestamp: exitEvent.timestamp,
          description: exitEvent.description
        });
      });
      
      // Alert 2: Exit without matching entry
      exits.forEach(exitEvent => {
        const hasMatchingEntry = entries.some(entry => {
          const exitTime = new Date(exitEvent.timestamp).getTime();
          const entryTime = new Date(entry.timestamp).getTime();
          // Entry should be before exit and within reasonable time (e.g., 24 hours)
          return entryTime < exitTime && (exitTime - entryTime) < 24 * 60 * 60 * 1000;
        });
        
        if (!hasMatchingEntry) {
          alerts.push({
            id: exitEvent.id,
            plateNumber: plateNumber,
            alertType: 'No Matching Entry',
            message: 'Vehicle exited without recorded entry',
            timestamp: exitEvent.timestamp,
            description: exitEvent.description
          });
        }
      });
      
      // Alert 3: After-hours exits (exits outside 6 AM - 8 PM)
      exits.forEach(exitEvent => {
        const exitDate = new Date(exitEvent.timestamp);
        const hour = exitDate.getHours();
        if (hour < 6 || hour >= 20) {
          alerts.push({
            id: exitEvent.id,
            plateNumber: plateNumber,
            alertType: 'After Hours Exit',
            message: 'Material movement detected outside working hours',
            timestamp: exitEvent.timestamp,
            description: exitEvent.description
          });
        }
      });
    });
    
    // Sort by timestamp (most recent first)
    return alerts.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  /**
   * Calculate vendor-wise delivery analytics
   * ANPR Solution: Prevents fake delivery claims by tracking vendor deliveries
   * Only uses ALLOW events for analytics (authorized deliveries)
   */
  private calculateVendorAnalytics(events: ConstructionSiteEvent[]): VendorAnalytics[] {
    const vendorMap = new Map<string, {
      entries: ConstructionSiteEvent[];
      exits: ConstructionSiteEvent[];
    }>();
    
    // Group events by vendor (derived from plate state code)
    // Only use ALLOW events for analytics (authorized movements)
    events.forEach(event => {
      // Skip non-ALLOW events for analytics
      if (event.decision !== 'ALLOW') {
        return;
      }
      
      const vendorName = this.getVendorName(event.plateNumber);
      
      if (!vendorMap.has(vendorName)) {
        vendorMap.set(vendorName, { entries: [], exits: [] });
      }
      
      const vendorData = vendorMap.get(vendorName)!;
      if (event.direction === 'Entry') {
        vendorData.entries.push(event);
      } else {
        vendorData.exits.push(event);
      }
    });
    
    // Calculate analytics for each vendor
    const analytics: VendorAnalytics[] = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    vendorMap.forEach((vendorData, vendorName) => {
      // Count deliveries today (entries today)
      const deliveriesToday = vendorData.entries.filter(entry => {
        const entryDate = new Date(entry.timestamp);
        entryDate.setHours(0, 0, 0, 0);
        return entryDate.getTime() === today.getTime();
      }).length;
      
      // Calculate average duration (time between entry and exit)
      const durations: number[] = [];
      vendorData.entries.forEach(entry => {
        const matchingExit = vendorData.exits.find(exit => {
          const exitTime = new Date(exit.timestamp).getTime();
          const entryTime = new Date(entry.timestamp).getTime();
          return exitTime > entryTime && (exitTime - entryTime) < 24 * 60 * 60 * 1000;
        });
        
        if (matchingExit) {
          const duration = (new Date(matchingExit.timestamp).getTime() - 
                           new Date(entry.timestamp).getTime()) / (1000 * 60); // minutes
          durations.push(duration);
        }
      });
      
      const averageDuration = durations.length > 0
        ? durations.reduce((a, b) => a + b, 0) / durations.length
        : undefined;
      
      // Count suspicious exits (ALERT exits)
      const suspiciousExits = vendorData.exits.filter(exit => exit.decision === 'ALERT').length;
      
      // Get last delivery time
      const lastEntry = vendorData.entries.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )[0];
      
      analytics.push({
        vendorName: vendorName,
        deliveriesToday: deliveriesToday,
        averageDuration: averageDuration,
        suspiciousExits: suspiciousExits,
        lastDeliveryTime: lastEntry?.timestamp
      });
    });
    
    // Sort by deliveries today (descending)
    return analytics.sort((a, b) => b.deliveriesToday - a.deliveriesToday);
  }

  /**
   * Get vendor name from plate number (state code mapping)
   */
  private getVendorName(plateNumber: string): string {
    if (plateNumber.length >= 2) {
      const stateCode = plateNumber.substring(0, 2).toUpperCase();
      return this.stateCodes[stateCode] || `Vendor ${stateCode}`;
    }
    return 'Unknown Vendor';
  }
}
