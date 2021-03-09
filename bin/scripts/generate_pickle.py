"""
@author Jasmin
"""

import pickle
import os
import pandas as pd
from collections import defaultdict


def parse(data_path):
    """
    This function creates dictionaries for the bed and bigwig files of the provided data. The dictionaries are stored in
    pickle files. For the bigwig files of ChIP-seq and ATAC-seq a separate pickle file is created for each biosource.
    For the bed files, a separate pickle file is created for each genome.
    """

    # list all genome folders in folder data
    # remove files and folders that are not genomes
    lt = pd.read_csv(os.path.join(data_path, 'linking_table.csv'), sep=';',
                     usecols=['genome', 'epigenetic_mark', 'biosource_name'])
    genomes = set(lt.values[:, 0])
    lt_tfs = set(lt.values[:, 1][lt.values[:, 1] != ('dnasei' or 'dna accessibility')])
    lt_biosources = set(x for x in lt.values[:, 2])

    for genome in genomes:

        # dictionary for the data within the bed files of one genome
        bed = {}

        # create folder structure for pickle files if it does not exist
        if not os.path.exists(os.path.join(data_path, 'pickledata')):
            os.mkdir(os.path.join(data_path, 'pickledata'))
        if not os.path.exists(os.path.join(data_path, 'pickledata', genome)):
            os.mkdir(os.path.join(data_path, 'pickledata', genome))

        # list all biosource folders for one genome
        biosources = [x for x in os.listdir(os.path.join(data_path, genome)) if x in lt_biosources]

        for biosource in biosources:

            # create folder structure for pickle files if it does not exist
            if not os.path.exists(os.path.join(data_path, 'pickledata', genome, 'chip-seq')):
                os.mkdir(os.path.join(data_path, 'pickledata', genome, 'chip-seq'))
            if not os.path.exists(os.path.join(data_path, 'pickledata', genome, 'atac-seq')):
                os.mkdir(os.path.join(data_path, 'pickledata', genome, 'atac-seq'))

            # dictionary for bed data of one biosource
            bs_bed_dict = {}
            # dictionary for paths of chip bigwig files
            chip = {}

            # list all transcription factor folders for one biosource
            tfs = [x for x in os.listdir(os.path.join(data_path, genome, biosource, 'chip-seq')) if x in lt_tfs]

            for tf in tfs:

                # dictionary for bed data of one tf
                tf_bed_dict = {}

                # list all files for chip data of one tf
                files = os.listdir(os.path.join(data_path, genome, biosource, 'chip-seq', tf))

                # test whether the chip file is bigwig or bed
                # bed files are read in with the function read_bed and the data is saved in the dictionary tf_bed_dict
                # the name of the bigwig file is saved in the variable bigwig_file
                for f in files:
                    if f.lower().endswith('.bed'):
                        tf_bed_dict.update(
                            read_bed(os.path.join(data_path, genome, biosource, 'chip-seq', tf, f)))
                    elif f.lower().endswith(('.bigwig', '.bigWig', '.bw')):
                        bigwig_file = f

                # the path of the bigwig file is stored in the chip dictionary as value to the tf as key
                chip[tf] = (os.path.join(data_path, genome, biosource, 'chip-seq', tf, bigwig_file))
                # the bed data of the tf is stored in the chip dictionary for the biosource with tf as key
                bs_bed_dict[tf] = tf_bed_dict

            # a pickle file is created that contains the paths to the chip bigwig files of one biosource
            # it is named after the biosource
            with open(os.path.join(data_path, 'pickledata', genome, 'chip-seq', biosource + '.pickle'), 'wb') as handle:
                pickle.dump(chip, handle, protocol=pickle.HIGHEST_PROTOCOL)

            # the bed data of the biosource is stored in the dictionary for the genome with biosource as key
            bed[biosource] = bs_bed_dict

            # list all files for atac data of one biosource
            # save the path to the bigwig file in variable atac
            # create pickle file containing the path of the atac bigwig named after the biosource
            for f in os.listdir(os.path.join(data_path, genome, biosource, 'atac-seq')):
                if f.lower().endswith(('.bigwig', '.bigWig', '.bw')):
                    atac = os.path.join(data_path, genome, biosource, 'atac-seq', f)
                    with open(os.path.join(data_path, 'pickledata', genome, 'atac-seq', biosource + '.pickle'),
                              'wb') as handle:
                        pickle.dump(atac, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # create pickle file for bed data of one genome named bed.pickle
        with open(os.path.join(data_path, 'pickledata', genome, 'bed.pickle'), 'wb') as handle:
            pickle.dump(bed, handle, protocol=pickle.HIGHEST_PROTOCOL)


def read_bed(file):
    """
    This function reads in a bed-file and returns the contained information in a dictionary.
    :param file: The path of the bed-file
    :return: chromosome is a dictionary with the chromosome as key and [start, stop, score, peak] as value
    """

    chromosome = defaultdict(list)

    f = pd.read_csv(file, sep='\t', usecols=lambda c: c in {'seqnames', 'start', 'end', 'SIGNAL_VALUE', 'PEAK'})

    for index, row in f.iterrows():
        start = int(row['start'])
        end = int(row['end'])
        score = float(row['SIGNAL_VALUE'])

        try:
            peak = row['PEAK']
        except ValueError:
            peak = int((end - start) / 2)

        # tests if a chromosome is already a key in the dictionary
        # if yes, the values are appended to the existing values of the key
        # if not, the key is added with the values
        chromosome[row['seqnames']].append([start, end, score, peak])

    return chromosome
