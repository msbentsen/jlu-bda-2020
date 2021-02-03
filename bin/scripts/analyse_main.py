#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 17:40:57 2021

@author: jan
"""
from scripts.interface_scoring import LoadPickle as Input
from scripts.components_fit import GmFit
from scripts.VisualizeData import VisualizeData as VD
from scripts.ema import EMA
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys


class Main:
    
    def __init__(self):
            
            self.evaluate_n = True
            self.eval_size = 15
            
            
    def progress(self, count, total, suffix=''):
        
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
    
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
    
        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()
        
    def mainloop(self, data):
        
        #data = Input().inputHandler(path)
        total = Input().number_of_chr(data)
        
        resultframe =pd.DataFrame(columns=['biosource','tf','means','covariances', 'weights']) 

        i = 0
        
        for biosource, b_value in data.items():
            
            for tf, tf_value in b_value.items():
                
                print('analysing: '+ tf)
                
                scoresarray = []
                
                for chromosome in tf_value.values():
                
                    for array in chromosome:
    
                            scoresarray.append([array[-1], array[-2]])
            
                Main().progress(i, total, '')
                
                
                scaled_scores = Main().scale(scoresarray)
                distribution = np.array(scaled_scores)

                if self.evaluate_n == True:
                    
                    all_diffs = GmFit().getDifference(distribution, self.eval_size)
                    rate, n_components = GmFit().evaluate(all_diffs)
                    plt.plot(all_diffs)
                
                single_result = EMA().emAnalyse(distribution, n_components)
                
                single_result.insert(0,'tf',tf)
                single_result.insert(0,'biosource',biosource)
                
                resultframe = pd.concat([resultframe, single_result])
                
                VD().displayDensityScatter(distribution)
                VD().altitudePlot(distribution, n_components)
                VD().contourPlot(distribution, n_components)
                
                i += 1
                Main().progress(i, total, '')
                
        return resultframe
    
    def scale(self, scoresarray):
        
        count = 0

        max_x = 0
        max_y = 0
        scaled = []
        
        for i in scoresarray:
            
            if i[0] > max_x:
                max_x = i[0]
            
            if i[1] > max_y:
                max_y = i[1]
                
        for k in scoresarray:
            
            scaled_x = ((scoresarray[count][0])/max_x)*100
            scaled_y = ((scoresarray[count][1])/max_y)*100
            
            scaled.append([scaled_x, scaled_y])
            
            count  += 1
            
        return scaled
            
        
        
    
#resultframe = Main().mainloop(data=scores)
#print(resultframe)
        
                
                
            
        