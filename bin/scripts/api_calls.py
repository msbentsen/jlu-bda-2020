# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 16:53:09 2021

@author: Spyro
"""

import repository

# =============================================================================
# def parse_result_csv():
#     filename = "result.csv"
#     
#     biosource_ls=[]
#     data_ls=[]
#     all_tf_ls=[]
#     results = repository.repository().read_csv(filename)
#    # print(results)
#    
#     
#     for index in results.index:
#         if results["biosource"][index] not in biosource_ls:
#             if biosource_ls != []:
#                 biosource_ls.append(all_tf_ls)
#                 data_ls.append(biosource_ls)
#             biosource_ls=[]
#             biosource_ls.append(results["biosource"][index])
#         tf_path_ls = []
#         tf_path_ls.append(results["tf"][index])
#         tf_path_ls.append(str(index+1))
#         all_tf_ls.append(tf_path_ls)
#         #print(results["biosource"][index], results["tf"][index])
#     biosource_ls.append(all_tf_ls)
#     data_ls.append(biosource_ls)
#     full_dict = {"data": data_ls}
#     return full_dict
# =============================================================================

def get_biosource_list_for_tree():
    filename = "result.csv"
    results = repository.repository().read_csv(filename)
    data_ls = []
    tree_node = {"item": "", "type":"", "belongsTo":"", "checked": False, "children":[]}
    inner_tree_node = {"item": "", "type":"", "belongsTo":"", "checked": False, "children":[]}
    for index in results.index:
        print(index)
        if results["biosource"][index] not in tree_node["item"]:
            if tree_node["item"]!= "":
                data_ls.append(tree_node)
            tree_node["item"] = results["biosource"][index]
        inner_tree_node["item"] = results["tf"][index]
        inner_tree_node["type"] = "tf"
        inner_tree_node["belongsTo"] = results["biosource"][index]
        tree_node["children"].append(inner_tree_node)
        
        print(inner_tree_node)
    data_ls.append(tree_node)
    print()
    print(tree_node)
    print(data_ls)
    
    return {"data": data_ls}

def getPathList(data):
    data_ls = []
    data_dict = {}
    #print(data)
    #data =  {"data":[{'item': 'GM12878', 'type': '', 'belongsTo': '', 'checked': False, 'children': [{'item': 'ATF2_ENCFF210HTZ', 'type': 'tf', 'belongsTo': 'GM12878', 'checked': False, 'children': []}, {'item': 'ATF2_ENCFF210HTZ', 'type': 'tf', 'belongsTo': 'GM12878', 'checked': True, 'children': []}, {'item': 'ATF2_ENCFF210HTZ', 'type': 'tf', 'belongsTo': 'GM12878', 'checked': False, 'children': []}, {'item': 'ATF2_ENCFF210HTZ', 'type': 'tf', 'belongsTo': 'GM12878', 'checked': False, 'children': []}, {'item': 'ATF2_ENCFF210HTZ', 'type': 'tf', 'belongsTo': 'GM12878', 'checked': False, 'children': []}, {'item': 'ATF2_ENCFF210HTZ', 'type': 'tf', 'belongsTo': 'GM12878', 'checked': False, 'children': []}, {'item': 'ATF2_ENCFF210HTZ', 'type': 'tf', 'belongsTo': 'GM12878', 'checked': False, 'children': []}]}]}
    for biosource_obj in data:
        
        biosource = biosource_obj["item"]
        #print(biosource)

        data_dict["biosource"]= biosource
        data_dict["tf_list"]=[]
        for tf_obj in biosource_obj["children"]:
            tempdict = {}
            tf = tf_obj["item"]
            tempdict["tf"]= tf
            tempdict["path"] = "path aus csv"
            if tf_obj["checked"]:
                data_dict["tf_list"].append(tempdict)
        data_ls.append(data_dict)
    #print(data_dict)
    return {"data": data_ls}

