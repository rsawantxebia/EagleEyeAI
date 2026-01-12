import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { Subscription } from 'rxjs';
import { ConstructionSiteService, ConstructionSiteEvent, MaterialTheftAlert, VendorAnalytics } from '../../services/construction-site.service';

/**
 * Construction Site Monitoring Component
 * 
 * ANPR Solution Overview:
 * This component demonstrates how ANPR technology solves real-world construction site problems:
 * 
 * 1. Material Theft Prevention:
 *    - Replaces manual entry registers with automated ANPR tracking
 *    - Detects unauthorized exits in real-time
 *    - Alerts security on suspicious material movements
 * 
 * 2. Fake Delivery Prevention:
 *    - Tracks vendor-wise delivery analytics using historical data
 *    - Identifies trucks claiming delivery without valid entry records
 *    - Provides delivery duration analytics to detect anomalies
 * 
 * 3. Automated Logging:
 *    - Eliminates error-prone paper-based registers
 *    - Provides real-time tracking of all material trucks
 *    - Maintains complete audit trail for compliance
 */
@Component({
  selector: 'app-construction-site',
  templateUrl: './construction-site.component.html',
  styleUrls: ['./construction-site.component.css']
})
export class ConstructionSiteComponent implements OnInit, OnDestroy {
  // Section A: Live Material Truck Tracking
  liveEvents: ConstructionSiteEvent[] = [];
  liveEventsLoading = false;
  liveEventsError: string | null = null;
  
  // Section B: Material Theft Alerts
  theftAlerts: MaterialTheftAlert[] = [];
  alertsLoading = false;
  alertsError: string | null = null;
  private alertsRefreshSubscription?: Subscription;
  
  // Section C: Vendor Analytics
  vendorAnalytics: VendorAnalytics[] = [];
  analyticsLoading = false;
  analyticsError: string | null = null;
  
  // Display columns for table
  displayedColumns: string[] = ['plateNumber', 'vehicleCategory', 'direction', 'gateName', 'time', 'decision'];
  
  constructor(
    private constructionSiteService: ConstructionSiteService,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.loadLiveEvents();
    this.loadTheftAlerts();
    this.loadVendorAnalytics();
    
    // Auto-refresh alerts every 5 seconds
    this.startAlertsAutoRefresh();
  }

  ngOnDestroy(): void {
    // Clean up subscriptions
    if (this.alertsRefreshSubscription) {
      this.alertsRefreshSubscription.unsubscribe();
    }
  }

  /**
   * Load live material truck tracking events
   * ANPR Solution: Replaces manual entry registers with automated tracking
   */
  loadLiveEvents(): void {
    this.liveEventsLoading = true;
    this.liveEventsError = null;
    
    this.constructionSiteService.getConstructionSiteEvents(100).subscribe({
      next: (events) => {
        this.liveEvents = events;
        this.liveEventsLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.liveEventsError = 'Failed to load live events';
        this.liveEventsLoading = false;
        console.error('Error loading live events:', err);
        this.cdr.detectChanges();
      }
    });
  }

  /**
   * Load material theft alerts
   * ANPR Solution: Detects unauthorized exits to prevent material theft
   */
  loadTheftAlerts(): void {
    this.alertsLoading = true;
    this.alertsError = null;
    
    this.constructionSiteService.getMaterialTheftAlerts(50).subscribe({
      next: (alerts) => {
        this.theftAlerts = alerts;
        this.alertsLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.alertsError = 'Failed to load theft alerts';
        this.alertsLoading = false;
        console.error('Error loading theft alerts:', err);
        this.cdr.detectChanges();
      }
    });
  }

  /**
   * Start auto-refresh for material theft alerts (every 5 seconds)
   */
  private startAlertsAutoRefresh(): void {
    this.alertsRefreshSubscription = this.constructionSiteService
      .getMaterialTheftAlertsAutoRefresh(5000)
      .subscribe({
        next: (alerts) => {
          this.theftAlerts = alerts;
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error('Error in auto-refresh alerts:', err);
        }
      });
  }

  /**
   * Load vendor-wise delivery analytics
   * ANPR Solution: Prevents fake delivery claims using historical tracking
   */
  loadVendorAnalytics(): void {
    this.analyticsLoading = true;
    this.analyticsError = null;
    
    this.constructionSiteService.getVendorAnalytics().subscribe({
      next: (analytics) => {
        this.vendorAnalytics = analytics;
        this.analyticsLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.analyticsError = 'Failed to load vendor analytics';
        this.analyticsLoading = false;
        console.error('Error loading vendor analytics:', err);
        this.cdr.detectChanges();
      }
    });
  }

  /**
   * Format timestamp for display
   */
  formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }

  /**
   * Format duration in minutes to readable format
   */
  formatDuration(minutes?: number): string {
    if (!minutes) {
      return 'N/A';
    }
    if (minutes < 60) {
      return `${Math.round(minutes)} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}min`;
  }

  /**
   * Get CSS class for decision badge
   */
  getDecisionClass(decision: string): string {
    switch (decision) {
      case 'ALLOW':
        return 'decision-allow';
      case 'ALERT':
        return 'decision-alert';
      case 'LOG_ONLY':
        return 'decision-log';
      default:
        return 'decision-unknown';
    }
  }

  /**
   * Get CSS class for alert type
   */
  getAlertTypeClass(alertType: string): string {
    return 'alert-' + alertType.toLowerCase().replace(/\s+/g, '-');
  }
}
