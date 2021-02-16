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
  belongsTo: string;
  checked: boolean;
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
          item: "Biosource1", 
          type:"",
          belongsTo: "",
          checked: false,
          children: [
            {item: "TF1",type:"tf",belongsTo: "Biosource1",checked: false, children: []},
            {item: "TF2",type:"tf",belongsTo: "Biosource1",checked: false, children: []}
          ]
        },
        {
          item: "Biosource2", 
          type:"",
          belongsTo: "",
          checked: false,
          children: [
            {item: "TF1",type:"tf",belongsTo: "Biosource2",checked: false, children: []},
            {item: "TF2",type:"tf",belongsTo: "Biosource2",checked: false, children: []}
          ]
        }
      ]
    )
  }

  private _getChildren = (node: TFItemNode ) => { return observableOf(node.children)}

  hasNestedChild = (_: number, nodeData: TFItemNode) => {return !(nodeData.type)}


  ngOnInit(): void {
  }

  goToResults(){
    console.log(this.nestedDataSource.data)
    //this.router.navigate(["/graph_biosource"])
  }

  updateAllChecked(node:TFItemNode){
    console.log(node)
    this.nestedDataSource.data.forEach(element => {
      if (element.item == node.belongsTo){
        element.checked = element.children.every(t => t.checked == true)
      }
    })
  }

  checkAll(node:TFItemNode){

    console.log(node)
    if (node.checked){
    node.children.forEach(element => {
      element.checked = true
      console.log(element)
      });
    } else {
      node.children.forEach(element => {
        element.checked = false
        console.log(element)
        });
  }
    //node.children.forEach(tf => tf.checked = true)
  }

  someChecked(node:TFItemNode): boolean{
    return node.children.filter(tf => tf.checked).length > 0 && !node.checked
  }
}
