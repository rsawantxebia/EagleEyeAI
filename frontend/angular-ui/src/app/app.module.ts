import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { VehicleLogsComponent } from './components/vehicle-logs/vehicle-logs.component';
import { AlertsComponent } from './components/alerts/alerts.component';
import { ConstructionSiteComponent } from './components/construction-site/construction-site.component';
import { AnprService } from './services/anpr.service';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    VehicleLogsComponent,
    AlertsComponent,
    ConstructionSiteComponent
  ],
  imports: [
    BrowserModule,
    CommonModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
