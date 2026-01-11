import { Component, OnInit } from '@angular/core';
import { AnprService, Alert } from '../../services/anpr.service';

@Component({
  selector: 'app-alerts',
  templateUrl: './alerts.component.html',
  styleUrls: ['./alerts.component.css']
})
export class AlertsComponent implements OnInit {
  alerts: Alert[] = [];
  loading = false;
  error: string | null = null;
  hours = 24;

  constructor(private anprService: AnprService) { }

  ngOnInit(): void {
    this.loadAlerts();
  }

  loadAlerts(): void {
    this.loading = true;
    this.error = null;

    this.anprService.getAlerts(100, this.hours).subscribe({
      next: (alerts) => {
        this.alerts = alerts;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load alerts';
        this.loading = false;
        console.error(err);
      }
    });
  }

  changeTimeRange(hours: number): void {
    this.hours = hours;
    this.loadAlerts();
  }

  refresh(): void {
    this.loadAlerts();
  }
}
