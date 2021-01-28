#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 21:51:08 2020

@author: jan
"""
from TestdataMaker import Testdata_Maker
import random
from EMA import EMA
import pandas as pd
import numpy as np

class TrainDataMaker:
    
    #Method to generate randomised Parameters from user input base
    def gaussParam(self, param):
        
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
            
        #Parameters for the rotation
        x = random.randrange(-1*(param[12]),(param[12]))
        rotation = (param[10]) + x
        
        return loc_x, gain_x, loc_y, gain_y, size, rotation
    
    #Write results of the EM Algorythm to csv
    def writetocsv(self, result, label):
        
        if label == 0:
            result.to_csv('/home/jan/pyhton-workspace/angewendete_daten_analyse/testsets/repressor_features', index = False, decimal=(','))
        if label == 1:
            result.to_csv('/home/jan/pyhton-workspace/angewendete_daten_analyse/testsets/enhancer_features', index = False, decimal=(','))

    #Write log file of the set parameters of the individual runs
    def writelog(self,dist_param):
        
        items = ['loop: ','location_ATAC: ','stda_loc_ATAC: ','gain_ATAC: ','stda_gain_ATAC: ','location_CHIP: ','stda_loc_CHIP: ','gain_CHIP: ','stda_gain_CHIP: ','size: ','stda_size: ','rotation: ','stda_rotation: ']
        with open('/home/jan/pyhton-workspace/angewendete_daten_analyse/testsets/log', 'a') as f:
            for i in range(0, len(dist_param)):
                f.write(items[i])
                f.write("%s\n" % dist_param[i])
            
            f.write("%s\n" % " ")
        f.close()

#Mode: 
#generate_data = True: Means Scores and EMA is performed and features,
#with the same label are written into csv.
generate_data = True

#combine: csv Files with features repressor enhancer are combined and shuffeled.
combine = False
#Output 
train_csv = False
eval_csv = True

#Label of the generated Features:
#0: Repressor low atac, high chip
#1: Enhancer high atac, high chip
label = 0
 
#Parameters for the first gaussian distribution:
loop = 500
location_ATAC = 25
location_CHIP = 70
dist_standard_deviation_loc_ATAC = 15
dist_standard_deviation_loc_CHIP = 15
gain_ATAC = 10
gain_CHIP= 10
dist_rotation = 10
dist_rotation_standard_deviation = 180
dist_standard_deviation_gain_ATAC = 10
dist_standard_deviation_gain_CHIP = 10
size_Gaussian = 3000
dist_standard_deviation_size_Gaussian = 400

#Parameters for linear noise:
noise = True
size_noise = 1000

#Parameters for gaussian noise:
gaussian_Noise = True
noise_loop = 30
location_ATAC_Noise = 50
location_CHIP_Noise = 50
standard_deviation_loc_ATAC = 50
standard_deviation_loc_CHIP = 50
gain_ATAC_Noise = 10
gain_CHIP_Noise = 10
standard_deviation_gain_ATAC = 1
standard_deviation_gain_CHIP = 1
size_GaussianNoise = 400
standard_deviation_size_GaussianNoise = 200


#Parameters for EM-Algorythm

n_cgauss = 5


    #Index of the parameter list
    # 0. loop
    # 1. location_ATAC
    # 2. stda_loc_ATAC
    # 3. gain_ATAC
    # 4. stda_gain_ATAC
    # 5. location_CHIP
    # 6. stda_loc_CHIP
    # 7. gain_CHIP
    # 8. stda_gain_CHIP
    # 9. size
    # 10.stda_size
    
    
param = []
param.append(noise_loop)
param.append(location_ATAC_Noise)
param.append(standard_deviation_loc_ATAC)
param.append(gain_ATAC_Noise)
param.append(standard_deviation_gain_ATAC)    
param.append(location_CHIP_Noise)
param.append(standard_deviation_loc_CHIP)
param.append(gain_CHIP_Noise)
param.append(standard_deviation_gain_CHIP)
param.append(size_GaussianNoise)
param.append(standard_deviation_size_GaussianNoise)

    #Index of the parameter list
    # 0. loop
    # 1. location_ATAC
    # 2. stda_loc_ATAC
    # 3. gain_ATAC
    # 4. stda_gain_ATAC
    # 5. location_CHIP
    # 6. stda_loc_CHIP
    # 7. gain_CHIP
    # 8. stda_gain_CHIP
    # 9. size
    # 10.stda_size
    # 11.rotation
    # 12.stda_rotation

dist_param = []
dist_param.append(loop)
dist_param.append(location_ATAC)
dist_param.append(dist_standard_deviation_loc_ATAC)
dist_param.append(gain_ATAC)
dist_param.append(dist_standard_deviation_gain_ATAC)    
dist_param.append(location_CHIP)
dist_param.append(dist_standard_deviation_loc_CHIP)
dist_param.append(gain_CHIP)
dist_param.append(dist_standard_deviation_gain_CHIP)
dist_param.append(size_Gaussian)
dist_param.append(dist_standard_deviation_size_Gaussian)
dist_param.append(dist_rotation)
dist_param.append(dist_rotation_standard_deviation)


#Testing:


#Execute:
    
if generate_data:
    feature_list = []
        
    for i in range(0, loop):
        #Get param:
        loc_x, gain_x, loc_y, gain_y, size, rotation = TrainDataMaker().gaussParam(dist_param)
        
        scores_array = Testdata_Maker().getScoresArray(loc_x, loc_y, gain_x, gain_y, size)
        
        rotated = Testdata_Maker().rotate(scores_array, loc_x, loc_y, rotation)  
        scores_array = rotated
        
        
        if noise:
            randomized = Testdata_Maker().randomeNoise(size_noise, scores_array)
            scores_array = randomized
        
        if gaussian_Noise:
            g_noise = Testdata_Maker().gaussianNoise(param)
            scores_array.extend(g_noise)
         
        filtered = Testdata_Maker().cutoff(scores_array)
        scores_array = filtered
        print(len(filtered))
        
        dataframe = EMA().emAnalyse(scores_array, n_cgauss)
        feature = EMA().getsignificant(dataframe)
        feature.insert(3,'label',label)
        
        #print(feature)
        feature_list.append(feature)
        
    result = pd.concat(feature_list)
    # print(result)
    result.reset_index(drop=True,inplace=True)
    # print(result)
    TrainDataMaker().writelog(dist_param)
    TrainDataMaker().writetocsv(result,label)
    
    Testdata_Maker().contourPlot(scores_array)
    Testdata_Maker().displayDensityScatter(scores_array)

if combine:
    
    rep_features = pd.read_csv('/home/jan/python-workspace/angewendete_daten_analyse/testsets/repressor_features')    
    enc_features = pd.read_csv('/home/jan/python-workspace/angewendete_daten_analyse/testsets/enhancer_features')
    #print(rep_features.values)
    comb_list = [rep_features, enc_features]
    x = pd.concat(comb_list)

    training_data = x.sample(frac=1).reset_index(drop=True)

    if train_csv:
        training_data.to_csv('/home/jan/python-workspace/angewendete_daten_analyse/testsets/training_data', index=False, decimal = ',')
    
    if eval_csv:
        training_data.to_csv('/home/jan/python-workspace/angewendete_daten_analyse/testsets/eval_data', index=False, decimal=',')
    
    
    

    
    
    
    
    
    
    
    