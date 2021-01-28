#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 18:15:37 2021

@author: jan
"""

import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np
from sklearn.mixture import GaussianMixture

class VisualizeData:
    
        #Make Density Scatter Heatmap
        def displayDensityScatter(self,scores_array):
        
            x = []
            y = []
            
            for i in range(0, len(scores_array)):
                v = scores_array[i]
                xi = v[0]
                yi = v[1]
                
                x.append(xi)
                y.append(yi)
            
            np.array(x)
            np.array(y)
            
            # Calculate the point density
            xy = np.vstack([x,y])
            z = gaussian_kde(xy)(xy)
        
            # Sort the points by density, so that the densest points are plotted last
            # idx = z.argsort()
            
            # x, y, z = x[idx], y[idx], z[idx]
            
            fig, ax = plt.subplots()
            ax.scatter(x, y, c=z, s=50, edgecolors='face')
            
            ax.set(xlim=(0,60), ylim=(0,14))
            plt.xlabel("ATAC")
            plt.ylabel("Chip")
            #plt.colorbar()
            
            plt.show()
        
        #Make contourPlot
        def contourPlot(self, scores_array, n_cgauss):
        
            x = []
            y = []
            
            gmm = GaussianMixture(n_components=n_cgauss)
            gmm.fit(scores_array)
            
            for i in range(0, len(scores_array)):
                v = scores_array[i]
                xi = v[0]
                yi = v[1]
                
                x.append(xi)
                y.append(yi)
            
            np.array(x)
            np.array(y)
            
            # Calculate the point density
            xy = np.vstack([x,y])
            z = gaussian_kde(xy)(xy)
            
            # Make the plot
            fig = plt.figure()
            ax = fig.gca(projection='3d')
            ax.plot_trisurf(x, y, z, cmap=plt.cm.coolwarm, linewidth=1, antialiased=False)
            # ax.plot_surface(x, y, z, color='b')
            plt.show()
            
        #Make altitude Plot
        def altitudePlot(self, data, n_cgauss):
        
            gmm = GaussianMixture(n_components=n_cgauss)
            gmm.fit(data)
            
            X, Y = np.meshgrid(np.linspace(start = -1, stop = 100, num = 100), np.linspace(start = -1, stop = 100, num = 100))
            XY = np.array([X.ravel(), Y.ravel()]).T
            Z = gmm.score_samples(XY)
            Z = Z.reshape(100,100)
    
            plt.contour(X,Y,Z)
            plt.scatter(data[:,0], data[:,1])
            
            plt.show()