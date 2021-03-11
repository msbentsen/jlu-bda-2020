import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FlaskApiService } from '../service/flask-api.service';

@Component({
  selector: 'app-graph-biosource',
  templateUrl: './graph-biosource.component.html',
  styleUrls: ['./graph-biosource.component.scss']
})
export class GraphBiosourceComponent implements OnInit {
  
  graphs: any
  path_array:any
  biosource_array:any
  tf_array:any
  filename_array:any
  constructor(
    private router: Router,
    private api_service: FlaskApiService
  ) {this.graphs = api_service.Viszalization_Data.value }

  ngOnInit(): void {
    this.test()
  }

  test(){
    let temp_array = []
    let temp_bio = []
    let temp_tf = []
    
    let temp_file_second = []

    //temp_file_second auch noch für tf falls mehrere biosources
    for (var biosource in this.graphs){
      console.log(biosource)
      temp_bio.push(biosource)
      for (var tf in this.graphs[biosource]){
        console.log(tf)
        temp_tf.push(tf)
        let temp_file = []
        for (var filename of this.graphs[biosource][tf]){
          console.log(filename)
          //temp_array.push(biosource+"/"+tf+"/"+filename)
          temp_array.push(tf+"/"+filename)
          temp_file.push(filename.split("_")[0])
        }
        temp_file_second.push(temp_file)
      }
    }
    this.path_array=temp_array
    this.biosource_array=temp_bio
    this.tf_array=temp_tf
    this.filename_array=temp_file_second
    console.log(this.path_array)
  }

}
