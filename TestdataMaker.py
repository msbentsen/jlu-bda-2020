#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 18:35:13 2020

@author: jan
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import random
import pickle

from mpl_toolkits.mplot3d import Axes3D


class Testdata_Maker:
    
    def __init__(self):
        
        
        #set max value of the generated scores:
        #also used for the plotting
        self.maxScore = 100
        
    #Method to create gauusian distributed scores 
    #return as numpy array
    def normal(self, location, gain, size):

        scores = np.random.normal(location, gain, size)
        #print (data)
        
        return (scores)
    
    #Method to combine scores to vectors
    #Output 2D numpy Array
    def getScoresArray(self, location_ATAC, location_CHIP, gain_ATAC, gain_CHIP, size):
    
        scores_array = []
        
        #Get ATAC-seq Scores
        ATAC_Scores = Testdata_Maker().normal(location_ATAC, gain_ATAC, size)
        
        #Get CHIP-seq Scores
        CHIP_Scores = Testdata_Maker().normal(location_CHIP, gain_CHIP, size)
        


        for i in range(0, len(ATAC_Scores)):
            
            x = ATAC_Scores.item(i)
            y = CHIP_Scores.item(i)
            
            scores_array.append([x,y])
        
        # print ("Number of initially generated Score-Pairs: ")
        # print (len(scores_array))
        
        return scores_array
    
    #Method to generate the rotation matrix:
    #Returns rotation matrix
    def getRotationMatrix(self, rotation):
        
        theta = np.radians(rotation)
        
        r = np.array(( (np.cos(theta), -np.sin(theta)),
                       (np.sin(theta), np.cos(theta)) ))
        
        print ('rotation matrix:')
        print(r)
        
        return r
    
    #Method to rotate the vectors (x,y)
    #returns rotated vectors
    def rotate(self, scores_array, location_ATAC, location_CHIP, rotation):
        
        
        
        r = Testdata_Maker().getRotationMatrix(rotation)
        m = np.array([location_ATAC, location_CHIP])
        
        rotated = []
        
        for i in range(0, len(scores_array)):
            
            v = scores_array[i]
            f = (r.dot(v-m))+m
            rotated.append([f[0],f[1]])
         
        return rotated
    
    #Method to add randome noise:
    def randomeNoise(self, size_noise, scores_array):
        
        
        x_array = np.random.randint(self.maxScore, size = size_noise)
        y_array = np.random.randint(self.maxScore, size = size_noise)
        
        for i in range(0, len(x_array)):
            
            scores_array.append([x_array[i], y_array[i]])
            
        return scores_array
    
    #Method to filter higher scores than given maximum:
    def cutoff(self, scores_array):
        
        normalized_data = []
        
        for i in range(0,len(scores_array)):
            
            a = scores_array[i]
            if a[0]<self.maxScore and a[0]>0 and a[1]<self.maxScore and a[1]>0:
                
                normalized_data.append(a)
                
        return normalized_data
    
    #Method to display the generated data by density in a scatter plot
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
        
        ax.set(xlim=(0,self.maxScore), ylim=(0,self.maxScore))
        plt.xlabel("ATAC")
        plt.ylabel("Chip")
        #plt.colorbar()
        
        plt.show()
    
    
    def write(self, data):
        
        if type(data) is list:
            
            np.save('/home/jan/pyhton-workspace/angewendete_daten_analyse/testsets/data', scores_array)
    
        if type(data) is dict:
            
            output = open('/home/jan/pyhton-workspace/angewendete_daten_analyse/testsets/dict.pkl', 'wb')
            pickle.dump(data, output)
            output.close()
            
        else:
            print('write: type error!')
    
    def gNoiseParam(self, param):
        
        #Parameters of location_ATAC
        x = random.randrange(-1*(param[2]),(param[2]))
        loc_x =(param[1]) + x
        
        #Parameters of location_CHIP
        x = random.randrange(-1*(param[6]),(param[6]))
        loc_y = (param[5]) + x
        
        #Parameters of gain_ATAC
        x = random.randrange(-1*(param[4]),(param[4]))
        gain_x = (param[3]) + x
        
        if gain_x <= 0:
            gain_x = 1
        
        #Parameters of gain_CHIP
        x = random.randrange(-1*(param[8]),(param[8]))
        gain_y = (param[7]) + x
            
        if gain_x <= 0:
            gain_x = 1
        
        #Parameters of size_gaussian_noise
        x = random.randrange(-1*(param[10]),(param[10]))
        size = (param[9]) + x
        
        if size <= 0:
            size = 1
        
        return loc_x, gain_x, loc_y, gain_y, size
        
    
    def gaussianNoise(self, param):
        
        
        noise = []
        
        for i in range(0, param[0]):
            
            loc_x, gain_x, loc_y, gain_y, size = Testdata_Maker().gNoiseParam(param)
            
            scores_array = Testdata_Maker().getScoresArray(loc_x, loc_y, gain_x, gain_y, size)
            noise.extend(scores_array)
            
        return noise
            
    
    def makeDict(self, scores_array):
    
        x = []
        y = []
        
        for i in range(0, len(scores_array)):
            v = scores_array[i]
            xi = v[0]
            yi = v[1]
            
            x.append(xi)
            y.append(yi)
    
        datadict = {"chr1":[],"chr2":[],"chr3":[]}
        location = 0
        
        for i in range(0,len(x)):
            
            datalist = []
            
            location+=1
            datalist.append(location)
            
            location+=1
            datalist.append(location) 
            
            a_score = x[i]
            datalist.append(a_score)
                
            c_score = y[i]
            datalist.append(c_score)
                
            datadict["chr1"].append(datalist)
        
        return datadict
    

    def contourPlot(self, scores_array):
        
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
        
        # Make the plot
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_trisurf(x, y, z, cmap=plt.cm.viridis, linewidth=0.2)
        plt.show()
         
        # to Add a color bar which maps values to colors.
        surf=ax.plot_trisurf(x, y, z, cmap=plt.cm.viridis, linewidth=0.2)
        fig.colorbar( surf, shrink=0.5, aspect=5)
        plt.show()
        
        # # Rotate it
        # ax.view_init(30, 45)
        # plt.show()
         
        # # Other palette
        # ax.plot_trisurf(x, y, z, cmap=plt.cm.jet, linewidth=0.01)
        # plt.show()


    
if __name__ == '__main__':
    
    #Parameters for the first gaussian distribution:
    location_ATAC = 20
    gain_ATAC = 10
    location_CHIP = 70
    gain_CHIP = 10
    size = 3000
    rotation = 30
    
    #Parameters for the second gaussian distribution:
    secondDistribution = True
    location_ATAC_2 = 80
    gain_ATAC_2 = 10
    location_CHIP_2 = 70
    gain_CHIP_2 = 10
    size_2 = 2000  
    rotation_2 = 0    
    
    #Parameters for Gaussian Noise:
    gaussian_Noise = True 
    
    param = []
    
    noise_loop = 50
    param.append(noise_loop)
    
    location_ATAC_Noise = 50
    param.append(location_ATAC_Noise)
    standard_deviation_loc_ATAC = 100
    param.append(standard_deviation_loc_ATAC)
    
    gain_ATAC_Noise = 10
    param.append(gain_ATAC_Noise)
    standard_deviation_gain_ATAC = 1
    param.append(standard_deviation_gain_ATAC)
    
    location_CHIP_Noise = 50
    param.append(location_CHIP_Noise)
    standard_deviation_loc_CHIP = 100
    param.append(standard_deviation_loc_CHIP)
    
    gain_CHIP_Noise = 10
    param.append(gain_CHIP_Noise)
    standard_deviation_gain_CHIP = 5
    param.append(standard_deviation_gain_CHIP)
    
    size_GaussianNoise = 100
    param.append(size_GaussianNoise)
    standard_deviation_size_GaussianNoise = 20
    param.append(standard_deviation_size_GaussianNoise)

    #Parameters for linear noise:
    noise = False
    size_noise = 1000
    
    #Testing:
    
    
    #Execute:
    scores_array = Testdata_Maker().getScoresArray(location_ATAC, location_CHIP, gain_ATAC, gain_CHIP, size)

    rotated = Testdata_Maker().rotate(scores_array, location_ATAC, location_CHIP, rotation)  
    scores_array = rotated
    
    if secondDistribution:
        
        scores_array_2 = Testdata_Maker().getScoresArray(location_ATAC_2, location_CHIP_2, gain_ATAC_2, gain_CHIP_2, size_2)

        rotated = Testdata_Maker().rotate(scores_array_2, location_ATAC_2, location_CHIP_2, rotation_2)  
        scores_array.extend(rotated)
    
    if noise:
        randomized = Testdata_Maker().randomeNoise(size_noise, scores_array)
        scores_array = randomized
    
    if gaussian_Noise:
        g_noise = Testdata_Maker().gaussianNoise(param)
        scores_array.extend(g_noise)
     
    filtered = Testdata_Maker().cutoff(scores_array)
    scores_array = filtered
    
    print(len(filtered))
    
    Testdata_Maker().displayDensityScatter(scores_array)
    
    Testdata_Maker().write(scores_array)
    
    
