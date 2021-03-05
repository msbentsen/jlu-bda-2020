import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { GraphHomeComponent } from './graph-home/graph-home.component';
import { AngularDemoComponent } from './angular-demo/angular-demo.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import { GraphBiosourceComponent } from './graph-biosource/graph-biosource.component';
import { GraphTfComponent } from './graph-tf/graph-tf.component';
import { SingleTfComponent } from './single-tf/single-tf.component';
import {MatTreeModule} from '@angular/material/tree';
import { MatIconModule} from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { FormsModule } from '@angular/forms'
import { FlaskApiService } from './service/flask-api.service';
import { FlexLayoutModule } from "@angular/flex-layout"


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    GraphHomeComponent,
    AngularDemoComponent,
    GraphBiosourceComponent,
    GraphTfComponent,
    SingleTfComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatCardModule,
    MatButtonModule,
    MatTreeModule,
    MatIconModule,
    MatCheckboxModule,
    FormsModule,
    FlexLayoutModule
  ],
  providers: [FlaskApiService],
  bootstrap: [AppComponent]
})
export class AppModule { }
