'''
File for merging reverse/foward reads in ATAC-seq data

by Kristina Müller (kmlr81)
'''


#import os

#os.system("")


def read_linkage_table():
    file_dict = creat_file_dict()






def creat_file_dict():
    '''
    Method reads in .csv linkage table file and creates a dictinary containg
    only information regarding ATAC-seq files.

    :return: file_dict is a dictionary of the following structure:
             key = name of reference genome as string, value = another dictionary
             of the following structure:
                key = name of biosource, value = an array of tuples: (filename, file path)
    '''
    import csv


    lt_path = "Daten/linkage_table.csv"
    lt_rows = []
    file_dict = {}
    files = []
    genomes = []
    biosources = []


    with open(lt_path) as linkage_table:
        lt_reader = csv.DictReader(linkage_table, delimiter= ',')

        for row in lt_reader:
            lt_rows.append(row)


    for row in lt_rows:
        if row["Sequencing_Type"] == "ATAC-seq":
            files.append((row["Filename"], row["File_Path"]))
            genomes.append(row["Reference_Genome"])
            biosources.append(row["Biosource"])


    ref_genome = genomes[0]
    ref_biosource = biosources[0]
    tmp_files = []
    tmp_dict_bs = {}

    for i in range(0,len(genomes)):
        if ref_genome != genomes[i] or i == len(genomes)-1:
            tmp_dict_bs[ref_biosource] = tmp_files
            file_dict[ref_genome] = tmp_dict_bs
            ref_genome = genomes[i]
            tmp_dict_bs.clear()
        else:
            if ref_biosource != biosources[i]:
                tmp_dict_bs[ref_biosource] = tmp_files
                ref_biosource = biosources[i]
                tmp_files.clear()
            else:
                tmp_files.append(files[i])

    return file_dict

