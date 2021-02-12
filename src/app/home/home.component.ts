import { Component, OnInit } from '@angular/core';
import { NavigationExtras, Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  public graphlist: any
  
  constructor(
    private router: Router
    ) { }

  

  ngOnInit(): void {
  }
  
  readfile(){
    return new Promise(resolve =>{
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", "http://localhost:5000/getGraphls", false)
    rawFile.onload = function(){
      var res = rawFile.response
      var resolvedJSON = JSON.parse(res)
      console.log(resolvedJSON)
      resolve(resolvedJSON)
    };
    console.log("json2", rawFile)
    rawFile.send(null)
    })
  }

  toResults(){
    this.readfile().then(dataobject =>{
      let navigationExtras: NavigationExtras = {
      state: {
        filelist: dataobject
      }
    }
    console.log(navigationExtras)
    console.log(this.graphlist)
    this.router.navigate(["/graph_home"], navigationExtras)
    })
     
  }
  
   

}
