#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 19:27:11 2021

@author: jan
"""
import numpy as np
import pickle

class LoadPickle:
    
        def inputHandler(self, path):
    
            try:
                data = np.load(path, allow_pickle=True)
                
            except:
                
                print("Analyse.EMA.inputHandler.Error: File not found")
    
            return data
    
        def number_of_chr(self,data):
            
            count = 0
            for value in data.values():
                
                for tf in value.values():
                    
                    count += 1
                    
            return count        
            
        def getallScores(self, datadict):
        
            scoresarray = []
            
            biosource = list(datadict.values())[0]
                
            tf = list(biosource.values())[1]
                
            for chromosome in tf.values():
                
                for array in chromosome:

                        scoresarray.append([array[-1], array[-2]])
                        
            return (scoresarray)
        
        
        
        def loadData(self, path):
            
            data = LoadPickle().inputHandler(path)
            scores_list = LoadPickle().getallScores(data)
            scores = np.array(scores_list)
            
            return (scores)
            
        
if __name__ == '__main__':
    
    data = LoadPickle().loadData(path='/home/jan/python-workspace/angewendete_daten_analyse/testsets/calculated_data_3.pickle')
    print(data)
    
    from VisualizeData import VisualizeData as VD
    
    VD().displayDensityScatter(data)
    VD().altitudePlot(data, 5)
    VD().contourPlot(data, 5)
    
    