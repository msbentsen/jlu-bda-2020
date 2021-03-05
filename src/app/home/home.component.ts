import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
//import {FlaskApiService} from '../service/flask-api.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  public graphlist: any
  
  constructor(
    private router: Router,
    //private api_service: FlaskApiService
    ) { }

  

  ngOnInit(): void {
  }
  
  toResults(){
    /*this.api_service.getTreeData().then(dataobject =>{
      let navigationExtras: NavigationExtras = {
      state: {
        filelist: dataobject
      }
    }
    console.log(navigationExtras)
    console.log(this.graphlist)
    
    this.router.navigate(["/graph_home"], navigationExtras)
    })*/
    this.router.navigate(["/graph_home"])
    
  }
  
   

}
