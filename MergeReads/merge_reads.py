'''
Methods for merging reverse/foward reads in ATAC-seq data

by Kristina Müller (kmlr81)
'''


#import os

#os.system("")


def merge_files():
    file_dict = creat_file_dict()






def creat_file_dict():
    '''
    Method creates a dictinary containg information regarding
    forward/reverse read ATAC-seq files
    files.

    :return: file_dict is a dictionary of the following structure:
             key = name of reference genome as string, value = another dictionary
             of the following structure:
                key = name of biosource, value = an array of tuples: (filename, file path)
    '''

    files, genomes, biosources = read_linkage_table()
    file_dict = {}
    ref_genome = genomes[0]
    ref_biosource = biosources[0]
    tmp_files = []
    tmp_dict_bs = {}
    genome_counter = 0

    for j in range(0,len(genomes)):
        if ref_genome == genomes[j]:
            genome_counter += 1
        else:
            for i in range(j-(genome_counter-1), j+1):
                if ref_biosource == biosources[i]:
                    tmp_files.append(files[i])
                else:
                    tmp_dict_bs[ref_biosource] = tmp_files
                    ref_biosource = biosources[i]
                    tmp_files = []
                    tmp_files.append(files[i])
                if i == j:
                    tmp_dict_bs[ref_biosource] = tmp_files
            file_dict[ref_genome] = tmp_dict_bs
            ref_genome = genomes[j]
            tmp_dict_bs = {}
            genome_counter = 0
        if j == len(genomes)-1:
            for i in range(j-(genome_counter-1), j+1):
                if ref_biosource == biosources[i]:
                    tmp_files.append(files[i])
                else:
                    tmp_dict_bs[ref_biosource] = tmp_files
                    ref_biosource = biosources[i]
                    tmp_files = []
                    tmp_files.append(files[i])
                if i == j:
                    tmp_dict_bs[ref_biosource] = tmp_files
            file_dict[ref_genome] = tmp_dict_bs

    return file_dict



def read_linkage_table():
    '''
    Method reads in .csv linkage table file and returns three lists with
    information regarding reference genomes, bio-sources, file names and file
    paths for ATAC-seq data only
    :return: files is a list containing tuples of (file name, file path)
             genomes is a list containing reference genomes
             biosources is a list containing biosources from the linkage table
    '''
    import csv

    lt_path = "Data/linkage_table.csv"
    lt_rows = []
    files = []
    genomes = []
    biosources = []

    with open(lt_path) as linkage_table:
        lt_reader = csv.DictReader(linkage_table, delimiter= ',')

        for row in lt_reader:
            lt_rows.append(row)


    for row in lt_rows:
        if row["Sequencing_Type"] == "ATAC-seq" and ("forward" in row[
            "Filename"].lower() or "reverse" in row["Filename"].lower()):
            files.append((row["Filename"], row["File_Path"]))
            genomes.append(row["Reference_Genome"])
            biosources.append(row["Biosource"])

    return files, genomes, biosources

