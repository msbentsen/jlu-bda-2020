#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 17:40:57 2021

@author: jan
"""
from repository import Repository
from components_fit import GmFit
from visualize_data import VisualizeData as VD
from ema import EMA
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os

class Main:
    """
    Main Class of the Analyse Part. This class is to call the whole pipe of this
    part.
    """
    
    def __init__(self):
        """
        Initiation of Variables

        Returns
        -------
        None.

        """
        path_scripts = os.path.dirname(__file__)
        path_bin = os.path.split(path_scripts)
        path_main = os.path.split(path_bin[0])
        self.path_results = os.path.join(path_main[0], 'results')
            
        self.evaluate_n = True
        self.eval_size = 7
            
            
    # def progress(self, count, total, suffix=''):
    #     """
    #     Method to Display a progress bar
        
    #     Parameters
    #     ----------
    #     count : actual status by counted Tfs
    #     total : total Tfs
    #     suffix : TYPE, optional
    #         DESCRIPTION. The default is ''.

    #     Returns
    #     -------
    #     None.

    #     """
        
    #     bar_len = 60
    #     filled_len = int(round(bar_len * count / float(total)))
    
    #     percents = round(100.0 * count / float(total), 1)
    #     bar = '=' * filled_len + '-' * (bar_len - filled_len)
    
    #     sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    #     sys.stdout.flush()
        
    def mainloop(self, data):
        """
        Main method of the analyse part. Here the Transcription Factors of the pickle File 
        is analysed and a dataframe of the results is created. Also the distributions of the 
        ATAC and CHIP data is plotted and safed as png.

        Parameters
        ----------
        path : Input Path

        Returns
        -------
        resultframe : result dataframe

        """
        
        # total = Input().number_of_chr(data)
        
        resultframe =pd.DataFrame(columns=['biosource','tf','means','covariances', 'weights']) 

        # i = 0
        
        for biosource, b_value in data.items():
            
            for tf, tf_value in b_value.items():
                
                print('analysing: '+ tf)
                
                scoresarray = []
                
                for chromosome in tf_value.values():
                
                    for array in chromosome:
    
                            scoresarray.append([array[-1], array[-2]])
            
                # Main().progress(i, total, '')
                
                
                scaled_scores = Main().scale(scoresarray)
                distribution = np.array(scaled_scores)
                
                if self.evaluate_n == True:
                    
                    all_diffs = GmFit().getDifference(distribution, self.eval_size)
                    n_components = GmFit().evaluate(all_diffs)
                    plt.plot(all_diffs)
                
                single_result = EMA().emAnalyse(distribution, n_components)
                
                single_result.insert(0,'tf',tf)
                single_result.insert(0,'biosource',biosource)
                
                
                v= VD(self.path_results, tf)
                path = v.displayDensityScatter(distribution, tf)
                
                v.altitudePlot(distribution, n_components, tf)
                v.contourPlot(distribution, n_components, tf)
                single_result.insert(5, 'path', path)
                
                resultframe = pd.concat([resultframe, single_result])
                
                print (tf + "    Done")
                # i += 1
                # Main().progress(i, total, '')
        #Save resultframe
        Repository().save_csv(resultframe)
            
        return resultframe
    
    def scale(self, scoresarray):
        """
        Method to scale the data to values from 0 to 100 

        Parameters
        ----------
        scoresarray : 2D array of vectors

        Returns
        -------
        scaled : 2D array of vectors

        """
        
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
            
        
if __name__ == '__main__':

    data = Repository().inputHandler(path='/home/jan/python-workspace/angewendete_daten_analyse/testsets/calculated_data_3.pickle')
    resultframe = Main().mainloop(data)
    # dirname = os.path.dirname(__file__)
    # resultframe.to_csv(dirname + '/result.csv', index = False, decimal=(','))
    print(resultframe)
        
                
                
            
        