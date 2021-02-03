import { Component, OnInit } from '@angular/core';
import { NavigationExtras, Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  constructor(
    private router: Router
    ) { }

  

  ngOnInit(): void {
  }
  readfile(){
    var graphlist : any
    var rawFile = new XMLHttpRequest();
    rawFile.open("GET", "http://localhost:5000/Test/test", false)
    rawFile.onload = function(){
      var jsonResponse = rawFile.response
      console.log(jsonResponse)
      graphlist = jsonResponse
    };
    
    rawFile.send(null)
    let navigationExtras: NavigationExtras = {
      state: {
        graphlist: graphlist
      }
    }
    this.router.navigate(["/graph_home"], navigationExtras)
  }

}
