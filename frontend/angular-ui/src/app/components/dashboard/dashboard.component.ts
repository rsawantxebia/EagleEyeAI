import { Component, OnInit } from '@angular/core';
import { AnprService, Detection, Event } from '../../services/anpr.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  recentDetections: Detection[] = [];
  recentEvents: Event[] = [];
  loading = false;
  error: string | null = null;
  selectedFile: File | null = null;
  imageUrl: string = '';

  constructor(private anprService: AnprService) { }

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading = true;
    this.error = null;

    this.anprService.getDetections(10, 0).subscribe({
      next: (detections) => {
        this.recentDetections = detections;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load detections';
        this.loading = false;
        console.error(err);
      }
    });

    this.anprService.getEvents(10, 0).subscribe({
      next: (events) => {
        this.recentEvents = events;
      },
      error: (err) => {
        console.error('Failed to load events', err);
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.imageUrl = ''; // Clear URL when file is selected
    }
  }

  triggerDetection(): void {
    this.loading = true;
    this.error = null;
    
    this.anprService.detectPlate(
      this.selectedFile || undefined,
      this.imageUrl || undefined,
      false
    ).subscribe({
      next: () => {
        this.loadDashboardData();
        this.selectedFile = null;
        this.imageUrl = '';
      },
      error: (err) => {
        this.error = 'Failed to trigger detection: ' + (err.error?.detail || err.message || 'Unknown error');
        this.loading = false;
        console.error(err);
      }
    });
  }
}
