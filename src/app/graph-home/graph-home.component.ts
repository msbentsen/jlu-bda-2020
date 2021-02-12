import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {MatButtonModule} from '@angular/material/button';
import { HomeComponent } from '../home/home.component';
import {FlatTreeControl} from '@angular/cdk/tree';
import {MatTreeFlattener, MatTreeFlatDataSource} from '@angular/material/tree';


@Component({
  selector: 'app-graph-home',
  templateUrl: './graph-home.component.html',
  styleUrls: ['./graph-home.component.scss'],
})
export class GraphHomeComponent implements OnInit {

  filelist: any
  graphlist: any

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    ) { 
      this.filelist = this.router.getCurrentNavigation()?.extras.state
      
      this.graphlist= this.filelist.filelist["data"]
      
  }

  ngOnInit(): void {
    console.log(this.graphlist)
  }
  goToResults(){
    this.router.navigate(["/graph_biosource"])
  }

}
