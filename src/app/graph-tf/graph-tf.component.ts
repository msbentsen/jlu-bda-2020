import { Component, OnInit } from '@angular/core';
import { NavigationExtras, Router } from '@angular/router';

@Component({
  selector: 'app-graph-tf',
  templateUrl: './graph-tf.component.html',
  styleUrls: ['./graph-tf.component.scss']
})
export class GraphTfComponent implements OnInit {

  constructor(
    private router: Router
  ) { }

  ngOnInit(): void {
  }
  goToTF(tf: string){
    console.log(tf)
    let navigationExtras: NavigationExtras = {
      state: {
        tf: tf,
        path: "path"+tf
      }
    }
    this.router.navigate(["/single_tf"],navigationExtras)
  }
}
