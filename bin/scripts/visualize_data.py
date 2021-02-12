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
import os

class VisualizeData:
        
        def __init__(self,path,tf_id):
            """
            Initialize variables and set up directory if necessary

            Parameters
            ----------
            path : TYPE
                DESCRIPTION.
            tf_id : TYPE
                DESCRIPTION.

            Returns
            -------
            None.

            """
            
            self.path_plots = (os.path.join(path, 'plots')) + "/" + tf_id
            try:
                os.makedirs(self.path_plots)
            except:
                pass
            
        #Make Density Scatter Heatmap
        def displayDensityScatter(self,scores_array, tf_id):
            """
            Method to illustrate distribution via Density Scatter(Heat-Map)

            Parameters
            ----------
            scores_array : 2D array of vectors

            Returns
            -------
            Path.

            """
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
            
            fig, ax = plt.subplots()
            ax.scatter(x, y, c=z, s=50, edgecolors='face')
            
            ax.set(xlim=(0,100), ylim=(0,100))
            plt.xlabel("ATAC")
            plt.ylabel("Chip")
            # plt.colorbar()
            figure_path = self.path_plots + "/DensityScatter_" + tf_id + ".svg"
            plt.savefig(figure_path, format="svg")
            plt.show()
            
            return self.path_plots
        
        #Make contourPlot
        def contourPlot(self, scores_array, n_cgauss, tf_id):
            """
            Method to display distribution via contour-plot

            Parameters
            ----------
            scores_array : 2D array of vectors
            n_cgauss : number of componets for a Gasussian Mixture Model
            Returns
            -------
            None.

            """
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
            figure_path = self.path_plots + "/Contour_" + tf_id + ".svg"
            plt.savefig(figure_path, format="svg")
            
            plt.show()
            
        #Make altitude Plot
        def altitudePlot(self, data, n_cgauss, tf_id):
            """
            Method to display a distribution via altitude-plot. Lines for altitude 
            measurments.

            Parameters
            ----------
            data : 2D array of vectors 
            n_cgauss : number of components 

            Returns
            -------
            None.

            """
        
            gmm = GaussianMixture(n_components=n_cgauss)
            gmm.fit(data)
            
            X, Y = np.meshgrid(np.linspace(start = -1, stop = 100, num = 100), np.linspace(start = -1, stop = 100, num = 100))
            XY = np.array([X.ravel(), Y.ravel()]).T
            Z = gmm.score_samples(XY)
            Z = Z.reshape(100,100)
    
            plt.contour(X,Y,Z)
            plt.scatter(data[:,0], data[:,1])
            
            plt.show()
            
            figure_path = self.path_plots + "/Altitude_" + tf_id + ".svg"
            plt.savefig(figure_path, format="svg")