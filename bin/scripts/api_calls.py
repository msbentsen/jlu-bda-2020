# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 16:53:09 2021

@author: Spyro
"""

import repository



def parse_result_csv():
    filename = "result.csv"
    
    biosource_ls=[]
    data_ls=[]
    all_tf_ls=[]
    results = repository.repository().read_csv(filename)
   # print(results)
    
    for index in results.index:
        if results["biosource"][index] not in biosource_ls:
            if biosource_ls != []:
                biosource_ls.append(all_tf_ls)
                data_ls.append(biosource_ls)
            biosource_ls=[]
            biosource_ls.append(results["biosource"][index])
        tf_path_ls = []
        tf_path_ls.append(results["tf"][index])
        tf_path_ls.append(str(index+1))
        all_tf_ls.append(tf_path_ls)
        #print(results["biosource"][index], results["tf"][index])
    biosource_ls.append(all_tf_ls)
    data_ls.append(biosource_ls)
    full_dict = {"data": data_ls}
    return full_dict
