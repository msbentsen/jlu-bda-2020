# -*- coding: utf-8 -*-
"""
Spyder Editor

Dies ist eine temporäre Skriptdatei.
"""

import pickle
import pyBigWig
import os
import scripts.Repository


def findarea(w, genom, biosource_ls, tf_ls, redo_analysis):
    # path to pickledata
    picklepath = str(os.path.dirname(os.path.abspath(__file__)).replace("bin/scripts", "data/pickledata/"))
    exist = False

    beddict = pickle.load(open(picklepath + genom + "/bed.pickle", "rb"))
    calculateddict = {}

    result_csv = scripts.Repository.Repository().read_csv(
        filename=os.path.dirname(os.path.abspath(__file__)).replace("bin/scripts", "result/result.csv"))

    # go through beddict for each biosource, then each tf, then each chromosom, then every binding
    # get Peak and Area from beddict and calculate the scores
    for biosource in beddict:

        # test if biosource was requested by the user
        if biosource in biosource_ls:

            # load dictionarys contaning paths to chip and atac bigwig files
            atacdict = pickle.load(open(picklepath + genom + "/ATAC-seq/" + biosource + ".pickle", "rb"))
            chipdict = pickle.load(open(picklepath + genom + "/ChIP-seq/" + biosource + ".pickle", "rb"))

            # generate key for biosource if it does not exist
            if biosource not in calculateddict:
                calculateddict[biosource] = {}

            # open atac bigwig
            atac = pyBigWig.open(atacdict)

            for tf in beddict[biosource]:

                # test if result for biosource-tf already exists
                if len(result_csv.loc[(result_csv['biosource'] == biosource) & (
                        result_csv['tf'] == tf)]) > 0 and not redo_analysis:
                    exist = True

                else:
                    # test if tf was requested by the user
                    if tf in tf_ls:

                        # generate key for tf if it does not exist
                        if tf not in calculateddict[biosource]:
                            calculateddict[biosource][tf] = {}

                        # open chip bigwig for tf
                        chip = pyBigWig.open(chipdict[tf])

                        for chromosom in beddict[biosource][tf]:

                            # generate key for chromosome if it does not exist
                            if chromosom not in calculateddict[biosource][tf]:
                                calculateddict[biosource][tf][chromosom] = []

                            for binding in beddict[biosource][tf][chromosom]:

                                start = binding[0]
                                peak = binding[3]

                                # calculate the area to be analyzed
                                peaklocation = start + peak
                                peaklocationstart = peaklocation - w
                                peaklocationend = peaklocation + w
                                calculationls = []

                                # call scores between start and end from atac and chip using pyBigWig
                                if chromosom in chip.chroms() and chromosom in atac.chroms():
                                    calculationls.append(peaklocationstart)
                                    calculationls.append(peaklocationend)
                                    chip_score = chip.intervals(chromosom, peaklocationstart, peaklocationend)
                                    atac_score = atac.intervals(chromosom, peaklocationstart, peaklocationend)

                                    # calculate mean of chip and atac scores
                                    for i in (chip_score, atac_score):
                                        length = 0
                                        mean = 0
                                        for interval in i:
                                            if interval[1] > peaklocationend:
                                                interval_length = (interval[1] - interval[0]) - (
                                                        interval[1] - peaklocationend)
                                            else:
                                                interval_length = interval[1] - interval[0]
                                            length += interval_length
                                            mean += interval_length * interval[2]
                                        mean = mean / length
                                        calculationls.append(mean)

                                    # add scores to dictionary
                                    calculateddict[biosource][tf][chromosom].append(calculationls)
                        print(tf, " done")

            # remove key if the value is empty
            if calculateddict[biosource]:
                pass
            else:
                del calculateddict[biosource]

    return calculateddict, exist
