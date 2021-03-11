import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AngularDemoComponent } from './angular-demo/angular-demo.component';
import { GraphBiosourceComponent } from './graph-biosource/graph-biosource.component';
import { GraphHomeComponent } from './graph-home/graph-home.component';
import { GraphTfComponent } from './graph-tf/graph-tf.component';
import { HomeComponent } from './home/home.component';
import { SingleTfComponent } from './single-tf/single-tf.component';

const routes: Routes = [
  {path: "home", component: HomeComponent},
  {path: "graph_home", component: GraphHomeComponent},
  {path: "angular_demo", component: AngularDemoComponent},
  {path: "graph_tf", component: GraphTfComponent},
  {path: "graph_biosource", component: GraphBiosourceComponent},
  {path: "single_tf", component: SingleTfComponent},


  {path: "", redirectTo: "home", pathMatch: "full"}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
