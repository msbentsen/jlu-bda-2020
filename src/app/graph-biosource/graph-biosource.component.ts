import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-graph-biosource',
  templateUrl: './graph-biosource.component.html',
  styleUrls: ['./graph-biosource.component.scss']
})
export class GraphBiosourceComponent implements OnInit {

  constructor(
    private router: Router
  ) { }

  ngOnInit(): void {
  }

  goToBiosource(biosource: string){
    console.log(biosource)
    this.router.navigate(["/graph_tf"])
  }
}
