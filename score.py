# -*- coding: utf-8 -*-
"""
Spyder Editor

Dies ist eine temporäre Skriptdatei.
"""

import numpy as np
import pickle
import os

gamingPC_path = "C:\\Users\\Spyro\\OneDrive\\Uni\\Bioinformatik Master\\BS1-ZusatzC\\Data\\parsedData\\"


def beddata():
    bed = pickle.load(open (gamingPC_path+"bed.pickle", "rb"))
    return bed

def atacdata():
    atac= pickle.load(open (gamingPC_path+"ATAC-seq\\GM12878.pickle", "rb"))
    return atac

def chipdata():
    chip = pickle.load(open (gamingPC_path+"CHIP-seq\\GM12878.pickle", "rb"))
    return chip


def findarea(beddictdict, atacdict, chipdict):
    print("bed", beddictdict.keys())
    print("atac", atacdict.keys())
    print("chip", chipdict.keys())
    calculateddict = {}
    datadict = {}
    ## get Peak and Area from Bed-Dict and safe it do another Dictionary (datadice)
    for biosource in beddictdict:
        if (biosource not in datadict):
            datadict[biosource]={}
        for tf in beddictdict[biosource]:
            if (tf not in datadict[biosource]):
                datadict[biosource][tf]={}
            for chromosom in beddictdict[biosource][tf]:
                
                if (chromosom not in datadict[biosource][tf]):
                    datadict[biosource][tf][chromosom]=[]
                for foundbinding in beddictdict[biosource][tf][chromosom]:
                    start = foundbinding[0]
                    stop = foundbinding[1]
                    score = foundbinding[2]
                    peak = foundbinding[3]
                    #peak von start aus?
                    peaklocation = start + peak
                    #peakbereich hardcoded --> Usereingabe !!
                    peaklocationstart = peaklocation - 50
                    peaklocationend = peaklocation + 50
                    
                    if (peaklocationstart < start ):
                        peaklocationstart = start
                    if (peaklocationend > stop):
                        peaklocationend = stop
                    #print("start", peaklocationstart, "stop", peaklocationend)
                    startendls= []
                    startendls.append(peaklocationstart)
                    startendls.append(peaklocationend)
                    datadict[biosource][tf][chromosom].append(startendls)
                    startendls= []
    
    ## go through datadict for each biosource, then each tf, then each chromosom, then every binding that was found in the bed-file
    for biosource in datadict:
        if (biosource not in calculateddict):
            calculateddict[biosource]={}
        for tf in datadict[biosource]:
            if (tf not in calculateddict[biosource]):
                calculateddict[biosource][tf]={}
            for chromosom in datadict[biosource][tf]:
                if (chromosom not in calculateddict[biosource][tf]):
                    calculateddict[biosource][tf][chromosom]=[]
                for binding in datadict[biosource][tf][chromosom]:
                    #print("binding",binding)
                    start = binding[0]
                    end= binding[1]
                    scorelist = []
                    calculationls = []
                    calculationls.append(start)
                    calculationls.append(end)
                    fullarea_chip = 0
                    fullarea_atac = 0
                    add_to_scores = True
                    ## go through chromosom and search for the wanted start/end in chipseq dict
                    if chromosom in chipdict[tf]:
                        for index,area in enumerate(chipdict[tf][chromosom]):
                            if (area[0] < start and area[1] > start):
                                #print("CHIP START area: ",chipdict[tf][chromosom][index], "index", index)
                                scorelist.append(round(area[2] * (area[1]-start),5))
                                fullarea_chip+=area[1]-start
                            if (area[0] >= start and area[1] <= end):
                                currentarea= area[1]-area[0]
                                scorelist.append(round(area[2]*currentarea,5))
                                fullarea_chip += currentarea
                                if (area[1] == end):
                                    break
                            if (area[0] < end and area[1] > end):
                                #print("CHIP END area: ",chipdict[tf][chromosom][index], "index", index)
                                scorelist.append(round(area[2]* (end - area[0]),5))
                                fullarea_chip+= end - area[0]
                                break
                    else:
                        add_to_scores = False
                    #calcilate mean of chipseq scores in that start/stop area
                    if (scorelist != [] and fullarea_chip != 0):
                        #print(scorelist)
                        calculationls.append(np.sum(scorelist)/fullarea_chip)
                    else:
                        add_to_scores = False
                    scorelist = []
                    
                    fullarea_chip = 0
                    ## go through chromosom and search for the wanted start/end in atac dict
                    if chromosom in atacdict[tf]:
                        for index,area in enumerate(atacdict[tf][chromosom]):
                            
                            if (area[0] < start and area[1] > start):
                                #print("ATAC START area: ",atacdict[tf][chromosom][index], "index", index)
                                scorelist.append(round(area[2] * (area[1]-start),5))
                                fullarea_atac+=area[1]-start
                            if (area[0] >= start and area[1] <= end):
                                currentarea= area[1]-area[0]
                                scorelist.append(round(area[2]*currentarea,5))
                                fullarea_atac += currentarea
                                if (area[1] == end):
                                    break
                            if (area[0] < end and area[1] > end):
                                #print("ATAC END area: ",atacdict[tf][chromosom][index], "index", index)
                                scorelist.append(round(area[2] * (end - area[0]),5))
                                fullarea_atac+= end - area[0]
                                break
                    else:
                        add_to_scores = False
                    
                    #calcilate mean of atacseq scores in that start/stop area
                    if (scorelist != [] and fullarea_atac!=0):
                        calculationls.append(np.sum(scorelist)/fullarea_atac)
                    else:
                        add_to_scores = False
                    fullarea_atac = 0
                    
                    #write mean of chip/atac to a dict: [start, stop, mean of chip scores, mean of atac scores]
                    if add_to_scores == True:
                        calculateddict[biosource][tf][chromosom].append(calculationls)
                print(chromosom, "done")
    print(calculateddict)
    file_to_write = open("calculated_data.pickle", "wb")
    pickle.dump(calculateddict, file_to_write)
    return


def main():
    findarea(beddata(), atacdata(), chipdata())
    
    return


if __name__=='__main__':
    main()