import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-graph-home',
  templateUrl: './graph-home.component.html',
  styleUrls: ['./graph-home.component.scss']
})
export class GraphHomeComponent implements OnInit {
  filelist: any
  graphlist: any
  constructor(
    private route: ActivatedRoute,
    private router: Router) { 
      this.filelist = this.router.getCurrentNavigation()?.extras.state
      console.log(this.filelist)
      this.graphlist= this.filelist.filelist["graphs"]
      
  }

  ngOnInit(): void {
    console.log(this.graphlist)
  }


}
