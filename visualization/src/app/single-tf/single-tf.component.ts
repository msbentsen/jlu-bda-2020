import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-single-tf',
  templateUrl: './single-tf.component.html',
  styleUrls: ['./single-tf.component.scss']
})
export class SingleTfComponent implements OnInit {

  tf_name: any
  tf_path: any

  constructor(
    private route: ActivatedRoute,
    private router: Router) {
      var navdata: any
      navdata = this.router.getCurrentNavigation()?.extras.state
      
      this.tf_name = navdata["tf"]
      this.tf_path = navdata["path"]


     }

  ngOnInit(): void {
    console.log(this.tf_name)
    console.log(this.tf_path)
  }

}
