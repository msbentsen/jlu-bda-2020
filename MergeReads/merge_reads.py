'''
Methods for merging reverse/foward reads in ATAC-seq data

by Kristina Müller (kmlr81)
'''


import os

#os.system("")


def merge_files():
    file_dict = creat_file_dict()
    pairs = find_pairs(file_dict)
    convert_to_bigWig(pairs)
    merged_file_paths = make_merged_file_paths(pairs)


def creat_file_dict():
    '''
    Method creates a dictinary containg information regarding
    forward/reverse read ATAC-seq files
    files.

    :return: file_dict: A dictionary of the following structure:
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
    paths for ATAC-seq files in need of merging only

    :return: files: A list containing tuples of (file name, file path)
             genomes: A list containing reference genomes
             biosources: A list containing biosources from the linkage table
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



def find_pairs(file_dict):
    '''
    Method pairs files that need to be merged

    :param file_dict: A dictionary as is returned by the method
                      create_file_dict()
    :return: paris: A list of touples containing the filepaths to the two
                    files that need to be merged with each other
    '''
    pairs = []

    for genome in file_dict.keys():
        for biosource in file_dict[genome].keys():
            for i in range(0,len(file_dict[genome][biosource])):
                filename = file_dict[genome][biosource][i][0]
                project_id = filename.split(".")[0]
                for j in range(i,len(file_dict[genome][biosource])):
                    if project_id in file_dict[genome][biosource][j][0] and j\
                            != i:
                        pair = (file_dict[genome][biosource][i][1],file_dict[
                            genome][biosource][j][1])
                        pairs.append(pair)

    return pairs



def make_merged_file_paths(pairs):
    '''
    Method creates filenames and filepaths for the new files after merging

    :param pairs: A list of tuples with (file path forward read, filepath
                  reverse read) of filepairs to be merged
    :return: merged_file_paths: A list of filepaths for new files after
             mergeing
    '''
    merged_file_paths = []

    for i in range(0,len(pairs)):
        file_path_split = pairs[i][0].rsplit("/", maxsplit=1)
        filename_split = file_path_split[1].split("_")
        file_ending = filename_split[1].split(".")[-1]
        merged_filename = filename_split[0] + "_merged." + file_ending
        merged_file_path = file_path_split[0] + "/" + merged_filename
        merged_file_paths.append(merged_file_path)

    return merged_file_paths


def get_bedgraph_idxs(pairs):
    '''
    Method searches list pairs for files with .bedGraph format and saves
    indexes of said files

    :param pairs: List of tuples containing filepaths to forward and reverse
                  files that need to be merged
    :return: bedgraphs: List of tuples containing indexes of files of type
             .bedGraph that need to be converted to bigWig
    '''
    bedgraphs = []

    for i in range(0,len(pairs)):
        file_ending_1 = pairs[i][0].split(".")[-1]
        file_ending_2 = pairs[i][1].split(".")[-1]

        if file_ending_1.lower() == 'bedgraph':
            bedgraphs.append((i,0))

        if file_ending_2.lower() == 'bedgraph':
            bedgraphs.append((i,1))

    return bedgraphs

def make_bw_file_paths(bedgraphs, pairs):
    '''
    Method makes file paths for files after conversion to bigWig format.

    :param bedgraphs: List of tuples with indexes of .bedGraph files in pairs
                      list
    :param pairs: List of tuples with patsh to files that need to be merged
    :return: List of paths to converted files with bigWig format
    '''
    file_paths_bw = []

    for bedgraph in bedgraphs:
        file_path_split = pairs[bedgraph[0]][bedgraph[1]].rsplit("/",
                                                                 maxsplit=1)
        filename_split = file_path_split[1].rsplit(".", maxsplit=1)
        filename_bw = filename_split[0] + ".bw"
        file_path_bw = file_path_split[0] + "/" + filename_bw
        file_paths_bw.append(file_path_bw)

    return file_paths_bw


def make_commands_bw(pairs, file_paths_bw):
    chrom_sizes_path = "Data/hg19/hg19.chrom.sizes "
    bedgraph_to_bw = "./Data/tools/bedGraphToBigWig "
    commands_first_half = []
    commands = []

    for pair in pairs:
        for i in range(0,2):
            command_first_half = bedgraph_to_bw + pair[i] + " " + \
                                chrom_sizes_path
            commands_first_half.append(command_first_half)

    for j in range(0,len(file_paths_bw)):
        command = commands_first_half[j] + file_paths_bw[j]
        commands.append(command)

    return commands


def convert_to_bigWig(pairs):
    bedgraphs = get_bedgraph_idxs(pairs)
    file_paths_bw = make_bw_file_paths(bedgraphs,pairs)
    commands = make_commands_bw(pairs,file_paths_bw)

    for command in commands:
        os.system(command)


