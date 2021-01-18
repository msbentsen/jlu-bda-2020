"""
Methods for merging reverse/forward reads in ATAC-seq data.


Goes through the following workflow:

- Reads in linkage_table.csv and identifies all ATAC-seq files with
forwar/reverse reads that need merging
- Groups them into pairs to be merged
- Checks if file format is bigWig, if not converts files to bigWig
- Merges files
- Checks if bedGraph is an allowed format since that is the output format of
merging tool, if not files are converted back to bigWig
- Deletes all files that are no longer needed
- Adds entries for merged files to linkage_table.csv


Use as follows:

    import merge_reads

    merge_reads.merge_files()


by Kristina Müller (kmlr81)
"""

import os


def merge_files():
    """
    Method calls the package workflow as described above.
    """
    file_dict = creat_file_dict()
    pairs = find_pairs(file_dict)
    bedgraphs = get_bedgraph_idxs(pairs)
    merged_file_paths = make_merged_file_paths(pairs)
    bw_file_paths = []

    if len(bedgraphs) > 0:
        bw_file_paths = make_bw_file_paths(pairs=pairs, bedgraphs=bedgraphs)
        convert_to_bigwig(bw_file_paths, pairs=pairs)

    bw_file_paths = get_all_bw_file_paths(pairs, bw_file_paths)
    merge_pairs(pairs, bw_file_paths)

    if len(bedgraphs) == 0:
        bw_file_paths = make_bw_file_paths(merged_file_paths=merged_file_paths)
        convert_to_bigwig(bw_file_paths, merged_file_paths=merged_file_paths)

    delete_old_files(bw_file_paths, pairs=pairs)
    add_merged_files_to_csv(merged_file_paths)


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

    lt_path = "linking_table.csv"
    lt_rows = []
    files = []
    genomes = []
    biosources = []

    with open(lt_path) as linkage_table:
        lt_reader = csv.DictReader(linkage_table, delimiter=',')

        for row in lt_reader:
            lt_rows.append(row)

    for row in lt_rows:
        if row["technique"] == "ATAC-seq" and ("forward" in row[
                "filename"].lower() or "reverse" in row["filename"].lower()):
            files.append((row["filename"], row["file_path"]))
            genomes.append(row["genome"])
            biosources.append(row["biosource"])

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
    Method creates filenames and file paths for the new files after merging

    :param pairs: A list of tuples with (file path forward read, filepath
                  reverse read) of file pairs to be merged
    :return: merged_file_paths: A list of file paths for new files after
             merging
    """
    merged_file_paths = []

    for i in range(0, len(pairs)):
        file_path_split = pairs[i][0].rsplit("/", maxsplit=1)
        filename_split = file_path_split[1].split("_")
        merged_filename = filename_split[0] + "_merged." + "bedGraph"
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
    :return: commands: List of commands to be executed for merging
    """
    bigwig_merge = "./tools/bigWigMerge "
    merged_file_paths = make_merged_file_paths(pairs)
    commands = []
    idx = 0

    for i in range(0, len(bw_file_paths) - 1, 2):
        command = bigwig_merge + "\"" + bw_file_paths[i] + "\"" + " " + "\"" \
                  + bw_file_paths[i + 1] + "\"" + " " + "\"" \
                  + merged_file_paths[idx] + "\""
        commands.append(command)
        idx += 1

    return commands


def get_all_bw_file_paths(pairs, bw_file_paths):
    """
    Method checks if there are any paths to files that already have bigWig
    format and didn't need to be converted to bigWig first and adds those to
    bw_file_paths so that they will be merged as well.

    :param pairs: List of touples with pairs of forward/reverse read files
                  that need to be merged
    :param bw_file_paths: List of paths to files in biWig format
    :return: bw_file_paths: Full list of paths to bigWig files in need of
                            merging
    """
    if len(bw_file_paths) == len(pairs) * 2:
        return bw_file_paths
    else:
        for pair in pairs:
            for i in range(0, 2):
                if "bw" in pair[i].rsplit(".", maxsplit=1)[-1].lower():
                    bw_file_paths.append(pair[i])

    return bw_file_paths


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

    :param pairs: List of tuples containing file paths to forward and reverse
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
    If pairs and bedgraphs is given as arguments, then the method returns
    file paths for bigWig files after conversion of files before being merged.
    If merged_file_paths is given as an argument, the method returns paths for
    bigWig files after conversion for already merged files.

    :param pairs: List of tuples containing file paths to forward and reverse
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
    elif bedgraphs is not None and pairs is not None and merged_file_paths is \
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
    If pairs is given, commands for conversion to bigWig will be made for
    files pre-merging.
    If merged_file_paths is given, commands for conversion to bigWig for
    files after merging will be made.

    :param bw_file_paths: List of paths to bigWig files after conversion
    :param pairs: List of tuples containing paths to files that need to be
                  merged
    :param merged_file_paths: List of paths to bedGraph files after merging
                              forward/reverse reads
    :return: commands: List of commands to be executed
    """
    bedgraph_to_bw = "./tools/bedGraphToBigWig "
    chrom_sizes_path = "data/hg19/hg19.chrom.sizes "  # what about other
    # genomes??
    commands = []

    if pairs is not None:
        commands_first_half = []
        for pair in pairs:
            for i in range(0, 2):
                command_first_half = bedgraph_to_bw + "\"" + pair[i] + "\"" \
                                     + " " + chrom_sizes_path
                commands_first_half.append(command_first_half)
        for j in range(0, len(bw_file_paths)):
            command = commands_first_half[j] + "\"" + bw_file_paths[j] + "\""
            commands.append(command)
    elif merged_file_paths is not None:
        for i in range(0, len(merged_file_paths)):
            command = bedgraph_to_bw + "\"" + merged_file_paths[i] + "\"" \
                      + " " + chrom_sizes_path + "\"" + bw_file_paths[i] + "\""
            commands.append(command)

    return commands


def convert_to_bigwig(bw_file_paths, pairs=None, merged_file_paths=None):
    """
    Method converts bedGraph files to bigWig files.
    If pairs is given, then the method converts all forward/reverse files to
    bigWig.
    If merged_file_paths is given, then the method converts all merged files to
    bigWig.

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


def delete_old_files(file_paths, pairs=None):
    """
    Method deletes forward/reverse file pairs after merging.

    :param file_paths: List of paths to bedGraph files that were converted to
                       bigWig and are no longer needed
    :param pairs: List of tuples containing paths to files that need to be
                  merged
    """
    command = "rm "

    if pairs is not None:
        for pair in pairs:
            for i in range(0, 2):
                if pair[i] not in file_paths:
                    os.system(command + "\"" + pair[i] + "\"")

    for file_path in file_paths:
        os.system(command + "\"" + file_path + "\"")


def get_rows(lt_path):
    """
    Method gets all rows of ATAC-seq forward reads in linkage table.

    :param lt_path: Path to file linkage_table.csv
    :return: rows: List of dictionaries; one dictionary for each row of the
                   linkage table with column names as keys and column entry as
                   value
    """
    import csv

    rows = []

    with open(lt_path) as linkage_table:
        lt_reader = csv.DictReader(linkage_table, delimiter=',')

        for row in lt_reader:
            if row["technique"] == "ATAC-seq" and "forward" in row[
                    "filename"].lower():
                rows.append(row)

    return rows


def make_merged_rows(lt_path, merged_file_paths):
    """
    Method takes dicts containing all column entries for forward reads and
    replaces fields filename, file_path and extension with information
    matching the corresponding merged file.

    :param lt_path: File path to linkage_table.csv file
    :param merged_file_paths: List of paths to files after merging
    :return: merged_rows: List of rows with info regarding merged files that
                          need to be added to linkage_table.csv
    """
    rows = get_rows(lt_path)
    merged_rows = []

    for file_path in merged_file_paths:
        file_name = file_path.rsplit("/", maxsplit=1)[-1]
        extension = file_name.rsplit(".", maxsplit=1)[-1]
        identifier = file_name.split(".")[0]
        for row in rows:
            if identifier in row["filename"]:
                row["filename"] = file_name
                row["file_path"] = file_path
                row["extension"] = extension
                merged_rows.append(row)

    return merged_rows


def add_merged_files_to_csv(merged_file_paths):
    """
    Method appends rows with information for merged files to linkage_table.csv.

    :param merged_file_paths: List of paths to merged files
    """
    import csv

    lt_path = "linkage_table.csv"
    merged_rows = make_merged_rows(lt_path, merged_file_paths)

    with open(lt_path, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=merged_rows[1].keys())
        writer.writerows(merged_rows)
