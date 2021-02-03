import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-graph-home',
  templateUrl: './graph-home.component.html',
  styleUrls: ['./graph-home.component.scss']
})
export class GraphHomeComponent implements OnInit {
  graphlist: any
  constructor(
    private route: ActivatedRoute,
    private router: Router) { 
      this.graphlist = this.router.getCurrentNavigation()?.extras.state
      
  }

  ngOnInit(): void {
    console.log(this.graphlist.graphlist)
  }


}
