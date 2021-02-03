import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AngularDemoComponent } from './angular-demo/angular-demo.component';
import { GraphHomeComponent } from './graph-home/graph-home.component';
import { HomeComponent } from './home/home.component';

const routes: Routes = [
  {path: "home", component: HomeComponent},
  {path: "graph_home", component: GraphHomeComponent},
  {path: "angular_demo", component: AngularDemoComponent},
  {path: "", redirectTo: "home", pathMatch: "full"}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
