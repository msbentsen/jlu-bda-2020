import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {MatButtonModule} from '@angular/material/button';
import { HomeComponent } from '../home/home.component';
import { NestedTreeControl} from '@angular/cdk/tree';
import {MatTreeFlattener, MatTreeFlatDataSource, MatTreeNestedDataSource} from '@angular/material/tree';
import { BehaviorSubject, Observable, of as observableOf } from 'rxjs';

export class TFItemNode {
  item: string;
  type: string;
  children: TFItemNode[];
}

const Tree_data = {
  Biosource: {
    "one": ["tf1","tf2"],
    "two": ["tf1", "tf2"]
  }
}



@Component({
  selector: 'app-graph-home',
  templateUrl: './graph-home.component.html',
  styleUrls: ['./graph-home.component.scss'],
})
export class GraphHomeComponent implements OnInit {

  nestedTreeControl: NestedTreeControl<TFItemNode>
  nestedDataSource: MatTreeNestedDataSource<TFItemNode>
  dataChange: BehaviorSubject<TFItemNode[]> = new BehaviorSubject<TFItemNode[]>([])

  filelist: any
  graphData: any

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    ) { 
      this.filelist = this.router.getCurrentNavigation()?.extras.state
      this.graphData= this.filelist.filelist["data"]
      

    this.nestedTreeControl= new NestedTreeControl<TFItemNode>(this._getChildren)
    this.nestedDataSource = new MatTreeNestedDataSource()

    this.dataChange.subscribe(data => this.nestedDataSource.data = data)

    this.dataChange.next(
      //Data from API
      [
        {
          item: "Biosource 1", 
          type:"",
          children: [
            {item: "TF1",type:"tf", children: []},
            {item: "TF2",type:"tf", children: []}
          ]
        },
        {
          item: "Biosource 2", 
          type:"",
          children: [
            {item: "TF1",type:"tf", children: []},
            {item: "TF2",type:"tf", children: []}
          ]
        }
      ]
    )
  }

  private _getChildren = (node: TFItemNode ) => { return observableOf(node.children)}

  hasNestedChild = (_: number, nodeData: TFItemNode) => {return !(nodeData.type)}

  ngOnInit(): void {
    console.log(this.graphData)
  }
  goToResults(){
    this.router.navigate(["/graph_biosource"])
  }

}
