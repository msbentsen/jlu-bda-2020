# -*- coding: utf-8 -*-
"""
Spyder Editor

Dies ist eine temporäre Skriptdatei.
"""

import pickle
import pyBigWig

def findarea(w, genom):
    beddictdict = pickle.load(open("parsedData/"+genom+"/bed.pickle", "rb"))
    print("bed", beddictdict.keys())
    calculateddict = {}
    datadict = {}
    ## get Peak and Area from Bed-Dict and safe it do another Dictionary (datadice)
    for biosource in beddictdict:
        atacdict = pickle.load(open("parsedData/"+genom+"/ATAC-seq/"+biosource+".pickle", "rb"))
        chipdict = pickle.load(open("parsedData/"+genom+"/ChIP-seq/"+biosource+".pickle", "rb"))
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
                    peaklocationstart = peaklocation - w
                    peaklocationend = peaklocation + w
                    
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
        atac=pyBigWig.open(atacdict)
        for tf in datadict[biosource]:
            if (tf not in calculateddict[biosource]):
                calculateddict[biosource][tf]={}
            chip=pyBigWig.open(chipdict[tf])
            for chromosom in datadict[biosource][tf]:
                if (chromosom not in calculateddict[biosource][tf]):
                    calculateddict[biosource][tf][chromosom]=[]
                for binding in datadict[biosource][tf][chromosom]:
                    #print("binding",binding)
                    start = binding[0]
                    end= binding[1]
                    calculationls = []
                    ## call scores between start and end from atac and chip using pyBigWig 
                    if chromosom in chip.chroms() and chromosom in atac.chroms():
                        calculationls.append(start)
                        calculationls.append(end)
                        chip_score=chip.intervals(chromosom,start,end)
                        atac_score=atac.intervals(chromosom,start,end)
                        for i in (chip_score, atac_score):
                            len=0
                            mean=0
                            for interval in i:
                                if interval[1]>end:
                                    l=(interval[1]-interval[0])-(interval[1]-end)
                                else:
                                    l=interval[1]-interval[0]
                                len+=l
                                mean+=l*interval[2]
                            mean=mean/len
                            calculationls.append(mean)
                        calculateddict[biosource][tf][chromosom].append(calculationls)
                print(chromosom, "done")
    #print(calculateddict)
    file_to_write = open("calculated_data.pickle", "wb")
    pickle.dump(calculateddict, file_to_write)
    return


def main():
    genom="genom"
    w=50
    findarea(w,genom)
    
    return


if __name__=='__main__':
    main()
