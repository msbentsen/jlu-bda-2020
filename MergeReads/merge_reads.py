"""
Methods for merging reverse/foward reads in ATAC-seq data

by Kristina Müller (kmlr81)
"""

import os


def merge_files():
    file_dict = creat_file_dict()
    pairs = find_pairs(file_dict)
    bedgraphs = get_bedgraph_idxs(pairs)
    merged_file_paths = make_merged_file_paths(pairs)

    if len(bedgraphs) > 0:
        bw_file_paths = make_bw_file_paths(pairs=pairs, bedgraphs=bedgraphs)
        convert_to_bigwig(bw_file_paths, pairs=pairs)
    else:
        bw_file_paths = make_bw_file_paths(merged_file_paths=merged_file_paths)
        convert_to_bigwig(bw_file_paths, merged_file_paths=merged_file_paths)


def creat_file_dict():
    """
    Method creates a dictionary containing information regarding
    forward/reverse read ATAC-seq files
    files.

    :return: file_dict: A dictionary of the following structure:
                        key = name of reference genome as string, value =
                        another dictionary of the following structure:
                        key = name of bio-source, value = an array of tuples:
                        (filename, file path)
    """

    files, genomes, biosources = read_linkage_table()
    file_dict = {}
    ref_genome = genomes[0]
    ref_biosource = biosources[0]
    tmp_files = []
    tmp_dict_bs = {}
    genome_counter = 0

    for j in range(0, len(genomes)):
        if ref_genome == genomes[j]:
            genome_counter += 1
        else:
            for i in range(j - (genome_counter - 1), j + 1):
                if ref_biosource == biosources[i]:
                    tmp_files.append(files[i])
                else:
                    tmp_dict_bs[ref_biosource] = tmp_files
                    ref_biosource = biosources[i]
                    tmp_files = [files[i]]
                if i == j:
                    tmp_dict_bs[ref_biosource] = tmp_files
            file_dict[ref_genome] = tmp_dict_bs
            ref_genome = genomes[j]
            tmp_dict_bs = {}
            genome_counter = 0
        if j == len(genomes) - 1:
            for i in range(j - (genome_counter - 1), j + 1):
                if ref_biosource == biosources[i]:
                    tmp_files.append(files[i])
                else:
                    tmp_dict_bs[ref_biosource] = tmp_files
                    ref_biosource = biosources[i]
                    tmp_files = [files[i]]
                if i == j:
                    tmp_dict_bs[ref_biosource] = tmp_files
            file_dict[ref_genome] = tmp_dict_bs

    return file_dict


def read_linkage_table():
    """
    Method reads in .csv linkage table file and returns three lists with
    information regarding reference genomes, bio-sources, file names and file
    paths for ATAC-seq files in need of merging only

    :return: files: A list containing tuples of (file name, file path)
             genomes: A list containing reference genomes
             biosources: A list containing biosources from the linkage table
    """
    import csv

    lt_path = "Data/linkage_table.csv"
    lt_rows = []
    files = []
    genomes = []
    biosources = []

    with open(lt_path) as linkage_table:
        lt_reader = csv.DictReader(linkage_table, delimiter=',')

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
    """
    Method pairs files that need to be merged

    :param file_dict: A dictionary as is returned by the method
                      create_file_dict()
    :return: paris: A list of touples containing the filepaths to the two
                    files that need to be merged with each other
    """
    pairs = []

    for genome in file_dict.keys():
        for biosource in file_dict[genome].keys():
            for i in range(0, len(file_dict[genome][biosource])):
                filename = file_dict[genome][biosource][i][0]
                project_id = filename.split(".")[0]
                single_chrom = "chr" in filename
                chrom = ""
                if single_chrom:
                    chrom += filename.split(".")[-2]
                for j in range(i, len(file_dict[genome][biosource])):
                    if project_id in file_dict[genome][biosource][j][0] and j \
                            != i:
                        if single_chrom:
                            if chrom in file_dict[genome][biosource][j][0]:
                                pair = (
                                    file_dict[genome][biosource][i][1],
                                    file_dict[genome][biosource][j][1])
                                pairs.append(pair)
                        else:
                            pair = (file_dict[genome][biosource][i][1],
                                    file_dict[genome][biosource][j][1])
                            pairs.append(pair)

    return pairs


def make_merged_file_paths(pairs):
    """
    Method creates filenames and filepaths for the new files after merging

    :param pairs: A list of tuples with (file path forward read, filepath
                  reverse read) of filepairs to be merged
    :return: merged_file_paths: A list of filepaths for new files after
             mergeing
    """
    merged_file_paths = []

    for i in range(0, len(pairs)):
        file_path_split = pairs[i][0].rsplit("/", maxsplit=1)
        filename_split = file_path_split[1].split("_")
        file_ending = filename_split[1].split(".")[-1]
        merged_filename = filename_split[0] + "_merged." + file_ending
        merged_file_path = file_path_split[0] + "/" + merged_filename
        merged_file_paths.append(merged_file_path)

    return merged_file_paths


def make_merge_commands(pairs, bw_file_paths):
    """
    Method creates commands needed for merging bigWig file pairs.

    :param bw_file_paths: List of paths to files with bigWig format in need
                          of merging
    :param pairs: List of tuples containing paths to file pairs in need of
                  merging
    :return: commands: List of commands to be executed
    """
    bigwig_merge = "./Data/tools/bigWigMerge "
    merged_file_paths = make_merged_file_paths(pairs)
    commands = []
    idx = 0

    for i in range(0, len(bw_file_paths)-1, 2):
        command = bigwig_merge + bw_file_paths[i] + " " + bw_file_paths[i+1] + \
                  " " + merged_file_paths[idx]
        commands.append(command)
        idx += 1

    return commands


def merge_pairs(pairs, bw_file_paths):
    """
    Method executes merge commands for all bigWig file pairs in need of merging.

    :param bw_file_paths: List of paths to bigWig files in need of merging
    :param pairs: List of tuples containing paths to file pairs in need of
                  merging
    """
    import os

    commands = make_merge_commands(pairs, bw_file_paths)

    for command in commands:
        os.system(command)


def get_bedgraph_idxs(pairs):
    """
    Method searches list pairs for files with .bedGraph format and saves
    indexes of said files

    :param pairs: List of tuples containing filepaths to forward and reverse
                  files that need to be merged
    :return: bedgraphs: List of tuples containing indexes of files of type
             .bedGraph that need to be converted to bigWig
    """
    bedgraphs = []

    for i in range(0, len(pairs)):
        file_ending_1 = pairs[i][0].split(".")[-1]
        file_ending_2 = pairs[i][1].split(".")[-1]

        if file_ending_1.lower() == 'bedgraph':
            bedgraphs.append((i, 0))

        if file_ending_2.lower() == 'bedgraph':
            bedgraphs.append((i, 1))

    return bedgraphs


def make_bw_file_paths(pairs=None, bedgraphs=None, merged_file_paths=None):
    """
    Method makes paths for bigWig files after conversion.

    :param pairs: List of tuples containing filepaths to forward and reverse
                  files that need to be merged
    :param bedgraphs: List of tuples containing indexes of files of type
                      bedGraph that need to be converted to bigWig
    :param merged_file_paths: List of paths to bedGraph files after merging
                              forward/reverse files
    :return: file_paths_bw: List of paths to bigWig files after conversion
    """
    file_paths_bw = []

    if merged_file_paths is not None and bedgraphs is None and pairs is None:
        for merged_file_path in merged_file_paths:
            file_path_split = merged_file_path.rsplit(".", maxsplit=1)
            file_path_bw = file_path_split[0] + ".bw"
            file_paths_bw.append(file_path_bw)
    elif bedgraphs is not None and pairs is not None and merged_file_paths is\
            None:
        for bedgraph in bedgraphs:
            file_path_split = pairs[bedgraph[0]][bedgraph[1]].rsplit(".",
                                                                     maxsplit=1)
            file_path_bw = file_path_split[0] + ".bw"
            file_paths_bw.append(file_path_bw)

    return file_paths_bw


def make_bw_commands(bw_file_paths, pairs=None, merged_file_paths=None):
    """
    Method creates command line prompts for converting bedGraph files to
    bigWig via pre-installed tool.

    :param bw_file_paths: List of paths to bigWig files after conversion
    :param pairs: List of tuples containing paths to files that need to be
                  merged
    :param merged_file_paths: List of paths to bedGraph files after merging
                              forward/reverse reads
    :return: commands: List of commands to be executed
    """
    bedgraph_to_bw = "./Data/tools/bedGraphToBigWig "
    chrom_sizes_path = "Data/hg19/hg19.chrom.sizes "
    commands = []

    if pairs is not None:
        commands_first_half = []
        for pair in pairs:
            for i in range(0, 2):
                command_first_half = bedgraph_to_bw + pair[i] + " " + \
                                     chrom_sizes_path
                commands_first_half.append(command_first_half)
        for j in range(0, len(bw_file_paths)):
            command = commands_first_half[j] + bw_file_paths[j]
            commands.append(command)
    elif merged_file_paths is not None:
        for i in range(0, len(merged_file_paths)):
            command = bedgraph_to_bw + merged_file_paths[i] + \
                      " " + chrom_sizes_path + bw_file_paths[i]
            commands.append(command)

    return commands


def convert_to_bigwig(bw_file_paths, pairs=None, merged_file_paths=None):
    """
    Method converts bedGraph files to bigWig files.

    :param bw_file_paths: List of paths to bigWig files after conversion
    :param pairs: List of tuples containing paths to files that need to be
                  merged
    :param merged_file_paths: List of paths to bedGraph files after merging
                              forward/reverse reads
    """
    if pairs is not None and merged_file_paths is None:
        commands = make_bw_commands(bw_file_paths, pairs=pairs)
    else:
        commands = make_bw_commands(bw_file_paths,
                                    merged_file_paths=merged_file_paths)

    for command in commands:
        os.system(command)


def delete_old_files(pairs):
    """
    Method deletes forward/reverse file pairs after merging
    :param pairs: List of tuples containing paths to files that need to be
                  merged
    """
    command = "rm "
    for pair in pairs:
        for i in range(0, 2):
            os.system(command + pair[i])
