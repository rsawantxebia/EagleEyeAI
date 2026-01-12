import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { AnprService, Detection, Event } from '../../services/anpr.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
  recentDetections: Detection[] = [];
  recentEvents: Event[] = [];
  loading = false;
  error: string | null = null;
  selectedFile: File | null = null;
  imageUrl: string = '';
  showCamera: boolean = false;
  stream: MediaStream | null = null;
  capturedImage: string | null = null;

  constructor(
    private anprService: AnprService,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    // Don't set loading to true here if we're already loading (during detection)
    const wasLoading = this.loading;
    if (!wasLoading) {
      this.loading = true;
    }
    this.error = null;

    this.anprService.getDetections(10, 0).subscribe({
      next: (detections) => {
        this.recentDetections = detections;
        if (!wasLoading) {
          this.loading = false;
        }
        // Force UI update to show new data
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'Failed to load detections';
        if (!wasLoading) {
          this.loading = false;
        }
        console.error(err);
        this.cdr.detectChanges();
      }
    });

    this.anprService.getEvents(10, 0).subscribe({
      next: (events) => {
        this.recentEvents = events;
        // Force UI update to show new events
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to load events', err);
        this.cdr.detectChanges();
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.imageUrl = ''; // Clear URL when file is selected
      this.capturedImage = null; // Clear captured image
    }
  }

  async startCamera(): Promise<void> {
    try {
      this.showCamera = true;
      this.error = null;
      this.capturedImage = null;
      this.selectedFile = null;
      this.imageUrl = '';
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment', // Use back camera if available
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      this.stream = stream;
      this.cdr.detectChanges(); // Ensure Angular updates the view
      
      // Wait for video element to be rendered and ensure it plays
      setTimeout(() => {
        const video = document.getElementById('camera-video') as HTMLVideoElement;
        if (video) {
          // Ensure video plays (some browsers require explicit play)
          video.play().catch(err => {
            console.error('Error playing video:', err);
            this.error = 'Failed to start video playback. Please ensure camera permissions are granted.';
          });
        }
      }, 300);
    } catch (err: any) {
      this.error = 'Failed to access camera: ' + (err.message || 'Permission denied');
      this.showCamera = false;
      this.stream = null;
      console.error('Camera error:', err);
    }
  }

  stopCamera(): void {
    try {
      // Stop camera stream first
      if (this.stream) {
        // Stop all tracks to release camera
        this.stream.getTracks().forEach(track => {
          try {
            track.stop();
            track.enabled = false;
          } catch (e) {
            // Track might already be stopped
            console.debug('Track already stopped:', e);
          }
        });
        this.stream = null;
      }
      
      // Clear video element srcObject to prevent memory leaks
      const video = document.getElementById('camera-video') as HTMLVideoElement;
      if (video) {
        video.srcObject = null;
        video.pause();
      }
      
      // Update state
      this.showCamera = false;
      
      // Don't clear capturedImage or selectedFile here - let triggerDetection handle it
      // This allows the captured image to be displayed briefly before detection
      
      // Use markForCheck to update view without full change detection
      this.cdr.markForCheck();
    } catch (err) {
      console.error('Error stopping camera:', err);
      // Still clear the state even if there's an error
      this.showCamera = false;
      this.stream = null;
      this.cdr.markForCheck();
    }
  }

  capturePhoto(): void {
    if (!this.stream) {
      this.error = 'Camera not started';
      return;
    }

    try {
      const video = document.getElementById('camera-video') as HTMLVideoElement;
      if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) {
        this.error = 'Video not ready. Please wait a moment.';
        return;
      }

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        this.error = 'Failed to get canvas context';
        return;
      }

      // Draw video frame to canvas
      ctx.drawImage(video, 0, 0);
      this.capturedImage = canvas.toDataURL('image/jpeg');
      
      // Convert canvas to blob, then to File, then auto-detect
      canvas.toBlob((blob) => {
        if (!blob) {
          this.error = 'Failed to create image blob';
          this.stopCamera(); // Stop camera on error
          return;
        }

        // Create File from blob
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        this.selectedFile = file;
        this.imageUrl = '';
        
        console.log('Photo captured, file created:', file.name, file.size, 'bytes');
        
        // Stop camera immediately after capture (auto-click cancel button behavior)
        this.stopCamera();
        
        // Force UI update
        this.cdr.detectChanges();
        
        // Auto-detect after capture with small delay
        setTimeout(() => {
          this.triggerDetection();
        }, 100); // Small delay to ensure file is set and camera is stopped
        
      }, 'image/jpeg', 0.95);
    } catch (err: any) {
      this.error = 'Failed to capture photo: ' + (err.message || 'Unknown error');
      console.error('Capture error:', err);
      // Stop camera even on error
      this.stopCamera();
    }
  }

  triggerDetection(): void {
    // Validate that we have something to detect
    if (!this.selectedFile && !this.imageUrl) {
      this.error = 'Please select an image file, enter an image URL, or capture a photo first';
      return;
    }

    this.loading = true;
    this.error = null;
    
    console.log('Triggering detection with:', {
      hasFile: !!this.selectedFile,
      fileName: this.selectedFile?.name,
      fileSize: this.selectedFile?.size,
      imageUrl: this.imageUrl || 'none'
    });
    
    // Regular detection with file upload or image URL
    this.anprService.detectPlate(
      this.selectedFile || undefined,
      this.imageUrl || undefined,
      false  // Don't use backend camera
    ).subscribe({
      next: (detection) => {
        console.log('Detection successful:', detection);
        
        // Ensure camera is stopped (in case it wasn't already)
        if (this.showCamera) {
          this.stopCamera();
        }
        
        // Clear all inputs after successful detection
        this.selectedFile = null;
        this.imageUrl = '';
        this.capturedImage = null;
        
        // Force UI update before reloading data
        this.cdr.detectChanges();
        
        // Reload dashboard data to show new detection (this refreshes the list)
        this.loadDashboardData();
        
        this.loading = false;
        
        // Force another UI update after data reload
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Detection error:', err);
        this.error = 'Failed to trigger detection: ' + (err.error?.detail || err.message || 'Unknown error');
        this.loading = false;
        
        // Ensure camera is stopped even on error
        if (this.showCamera) {
          this.stopCamera();
        }
        
        // Force UI update
        this.cdr.detectChanges();
      }
    });
  }

  ngOnDestroy(): void {
    this.stopCamera();
  }
}
