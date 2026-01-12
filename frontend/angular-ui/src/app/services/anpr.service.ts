import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Detection {
  id: number;
  plate_text: string;
  confidence: number;
  bbox: number[];
  timestamp: string;
  vehicle_id?: number;
}

export interface Event {
  id: number;
  event_type: string;
  description?: string;
  rule_name?: string;
  timestamp: string;
  plate_text?: string;
  vehicle_id?: number;
}

export interface Alert {
  id: number;
  plate_text: string;
  event_type: string;
  description: string;
  timestamp: string;
  rule_name?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AnprService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  getDetections(limit: number = 100, skip: number = 0): Observable<Detection[]> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('skip', skip.toString());
    
    return this.http.get<Detection[]>(`${this.apiUrl}/detections`, { params });
  }

  getEvents(limit: number = 100, skip: number = 0, eventType?: string): Observable<Event[]> {
    let params = new HttpParams()
      .set('limit', limit.toString())
      .set('skip', skip.toString());
    
    if (eventType) {
      params = params.set('event_type', eventType);
    }
    
    return this.http.get<Event[]>(`${this.apiUrl}/events`, { params });
  }

  getAlerts(limit: number = 100, hours: number = 24): Observable<Alert[]> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('hours', hours.toString());
    
    return this.http.get<Alert[]>(`${this.apiUrl}/alerts`, { params });
  }

  detectPlate(file?: File, imageUrl?: string, useCamera: boolean = false): Observable<Detection> {
    const formData = new FormData();
    
    // Only append file if it exists and is not empty
    if (file && file.size > 0) {
      formData.append('file', file);
      console.log('Sending file:', file.name, file.size, 'bytes');
    }
    
    // Only append image_url if it exists and is not empty
    if (imageUrl && imageUrl.trim()) {
      formData.append('image_url', imageUrl);
      console.log('Sending image_url:', imageUrl);
    }
    
    // Always append use_camera flag
    formData.append('use_camera', useCamera.toString());
    console.log('use_camera flag:', useCamera);
    
    return this.http.post<Detection>(`${this.apiUrl}/detect`, formData);
  }
}
