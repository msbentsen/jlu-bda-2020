"""
@author Jasmin
"""

import pickle
import os


def parse(path):
    """
    This function creates dictionaries for the bed and bigwig files of the provided data. The dictionaries are stored in
    pickle files. For the bigwig files of ChIP-seq and ATAC-seq a separate pickle file is created for each biosource.
    For the bed files, a separate pickle file is created for each genome.
    """

    # path for downloaded data
    data = path

    # list all genome folders in folder data
    # remove files and folders that are not genomes
    genomes = os.listdir(data)
    for x in ['pickledata', 'temp', 'linking_table.csv']:
        if x in genomes:
            genomes.remove(x)

    for genome in genomes:

        # dictionary for the data within the bed files of one genome
        bed = {}

        # list all biosource folders for one genome
        # remove files that are not biosources
        biosources = os.listdir(data + '/' + genome)
        if str(genome + '.chrom.sizes') in biosources:
            biosources.remove(str(genome + '.chrom.sizes'))

        # create folder structure for pickle files if it does not exist
        if not os.path.exists(data + '/' + 'pickledata'):
            os.mkdir(data + '/' + 'pickledata')
        if not os.path.exists(data + '/' + 'pickledata/' + genome):
            os.mkdir(data + '/' + 'pickledata/' + genome)

        for biosource in biosources:

            # create folder structure for pickle files if it does not exist
            if not os.path.exists(data + '/' + 'pickledata/' + genome + '/ChIP-seq/'):
                os.mkdir(data + '/' + 'pickledata/' + genome + '/ChIP-seq/')
            if not os.path.exists(data + '/' + 'pickledata/' + genome + '/ATAC-seq/'):
                os.mkdir(data + '/' + 'pickledata/' + genome + '/ATAC-seq/')

            # dictionary for bed data of one biosource
            bs_bed_dict = {}
            # dictionary for paths of chip bigwig files
            chip = {}

            # list all transcription factor folders for one biosource
            tfs = os.listdir(data + '/' + genome + '/' + biosource + '/ChIP-seq')

            for tf in tfs:

                # dictionary for bed data of one tf
                tf_bed_dict = {}

                # list all files for chip data of one tf
                files = os.listdir(data + '/' + genome + '/' + biosource + '/ChIP-seq/' + tf)

                # test whether the chip file is bigwig or bed
                # bed files are read in with the function read_bed and the data is saved in the dictionary tf_bed_dict
                # the name of the bigwig file is saved in the variable bigwig_file
                for f in files:
                    if f.split('.')[1] == 'bed':
                        tf_bed_dict.update(
                            read_bed(data + '/' + genome + '/' + biosource + '/ChIP-seq/' + tf + '/' + f))
                    elif f.split('.')[1] == 'bigWig':
                        bigwig_file = f

                # the path of the bigwig file is stored in the chip dictionary as value to the tf as key
                chip[tf] = (data + '/' + genome + '/' + biosource + '/ChIP-seq/' + tf + '/' + bigwig_file)
                # the bed data of the tf is stored in the chip dictionary for the biosource with tf as key
                bs_bed_dict[tf] = tf_bed_dict

            # a pickle file is created that contains the paths to the chip bigwig files of one biosource
            # it is named after the biosource
            with open(data + '/' + 'pickledata/' + genome + '/ChIP-seq/' + biosource + '.pickle', 'wb') as handle:
                pickle.dump(chip, handle, protocol=pickle.HIGHEST_PROTOCOL)

            # the bed data of the biosource is stored in the dictionary for the genome with biosource as key
            bed[biosource] = bs_bed_dict

            # list all files for atac data of one biosource
            # save the path to the bigwig file in variable atac
            # create pickle file containing the path of the atac bigwig named after the biosource
            for f in os.listdir(data + '/' + genome + '/' + biosource + '/ATAC-seq'):
                if f.split('.')[1] == 'bigWig':
                    atac = (data + '/' + genome + '/' + biosource + '/ATAC-seq/' + f)
                    with open(data + '/' + 'pickledata/' + genome + '/ATAC-seq/' + biosource + '.pickle',
                              'wb') as handle:
                        pickle.dump(atac, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # create pickle file for bed data of one genome named bed.pickle
        with open(data + '/' + 'pickledata/' + genome + '/bed.pickle', 'wb') as handle:
            pickle.dump(bed, handle, protocol=pickle.HIGHEST_PROTOCOL)


def read_bed(file):
    """
    This function reads in a bed-file and returns the contained information in a dictionary.
    :param file: The path of the bed-file
    :return: chromosome is a dictionary with the chromosome as key and [start, stop, score, peak] as value
    """

    chromosome = {}

    # bed file is read by line and the lines are parsed into a dictionary
    for line in open(file):
        s = line.split('\t')
        start = int(s[1])
        stop = int(s[2])
        score = float(s[6])

        # test if the input bed-file is in narrowPeak format (>9 columns)
        # if yes, the value in the 10th (index 9) column is returned as peak
        # if not, the middle between start and stop is returned as peak
        if len(s) <= 9:
            peak = int((int(s[2]) - int(s[1])) / 2)
        else:
            peak = int(s[9])

        # tests if a chromosome is already a key in the dictionary
        # if yes, the values are appended to the existing values of the key
        # if not, the key is added with the values
        if s[0] in chromosome:
            chromosome[s[0]].append([start, stop, score, peak])
        else:
            chromosome[s[0]] = [[start, stop, score, peak]]

    return chromosome
