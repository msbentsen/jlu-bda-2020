#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 22:51:02 2020

@author: jan
"""
import numpy as np
from sklearn.mixture import GaussianMixture
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

class EMA:
    
    # #Read generated Testdata // NOT NEEDED IN FINAL VERSION
    # def inputHandler(self, raw):
        
    #     if raw == True: 
            
    #         try:
    #             data = np.load('/home/jan/python-workspace/angewendete_daten_analyse/testsets/data.npy', allow_pickle=True)
                
    #         except:
                
    #             print("Analyse.EMA.inputHandler.Error: File not found")
    #     else:
    #         try:
    #             data = pickle.load(open('/home/jan/python-workspace/angewendete_daten_analyse/testsets/data.txt', 'rb'))
            
    #         except:
    #             print("Analyse.EMA.inputHandler.Error: File not found")
        
    #     return data
    
    
    # #Get scores of whole dataset as array of vectors ATAC = X; CHIP = Y
    # def transformDicttoArray(self, datadict):
    
    #         scoresarray = []
            
    #         for biosource in datadict.values():
                
    #             for tf in biosource.values():
                    
    #                 for chromosome in tf.values():
                        
    #                     for array in chromosome:

    #                         scoresarray.append([array[-1], array[-2]])
                        
    #         return (scoresarray)
    
    #Perform Gaussian Mixture Model //NOT THE FINAL VERSION SOME PLUGINS MISSING
    def emAnalyse(self, X_train, n_cgauss):
        
        gmm = GaussianMixture(n_components=n_cgauss)
        gmm.fit(X_train)
        
        means = gmm.means_
        covariances = gmm.covariances_
        weights = gmm.weights_
        
        data_array = []
        
        for i in range(0, len(means)):
            
            data_array.append([means[i],covariances[i],weights[i]])
      
        dataframe = pd.DataFrame(data_array, columns=('means','covariances','weights'))
        
        
        return dataframe
    
    #Method extracts component with the highest weight //(TEST) PROPABLY NOT INCLUDED
    def getsignificant(self, dataframe):
        
        array = dataframe.values
        x = 0
        pos = 1
        i = -1
        for item in array:
            i += 1
            weight = item[2]
            if weight > x:
                x = weight
                pos = i
        feature = dataframe.loc[pos:pos]

        
        return feature
        
        
        
if __name__ == '__main__':
    
    from VisualizeData import VisualizeData as VD
    from Interface_Scoring import LoadPickle as IP
    from components_fit import GmFit as GF
    #define type of input data
    #raw = true if import is a vector array[[X,Y]....[X,Y]]
    raw = True
    
    #n_cgauss = 5
    max_components = 15
    data = IP().loadData(path='/home/jan/python-workspace/angewendete_daten_analyse/testsets/calculated_data_3.pickle')
    #data = EMA().inputHandler(raw)
    print(data)
    n_cgauss = GF.evaluate_componets(data, max_components)
    dataframe = EMA().emAnalyse(data, n_cgauss)
    VD().altitudePlot(data, n_cgauss)
    VD().contourPlot(data, n_cgauss)
    VD().displayDensityScatter(data)
    EMA().getsignificant(dataframe)
    print(dataframe)

        