import { Component, OnInit } from '@angular/core';
import { AnprService, Detection } from '../../services/anpr.service';

@Component({
  selector: 'app-vehicle-logs',
  templateUrl: './vehicle-logs.component.html',
  styleUrls: ['./vehicle-logs.component.css']
})
export class VehicleLogsComponent implements OnInit {
  detections: Detection[] = [];
  loading = false;
  error: string | null = null;
  page = 0;
  pageSize = 50;

  constructor(private anprService: AnprService) { }

  ngOnInit(): void {
    this.loadDetections();
  }

  loadDetections(): void {
    this.loading = true;
    this.error = null;

    this.anprService.getDetections(this.pageSize, this.page * this.pageSize).subscribe({
      next: (detections) => {
        this.detections = detections;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load vehicle logs';
        this.loading = false;
        console.error(err);
      }
    });
  }

  nextPage(): void {
    this.page++;
    this.loadDetections();
  }

  previousPage(): void {
    if (this.page > 0) {
      this.page--;
      this.loadDetections();
    }
  }

  refresh(): void {
    this.page = 0;
    this.loadDetections();
  }
}
