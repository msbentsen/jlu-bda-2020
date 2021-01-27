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

    merge_reads.merge_all(linkage_table_path, chrom_sizes_paths,
    conversion_tool_path, merge_tool_path)


by Kristina Müller (kmlr81)
"""

import os
import csv
import pandas as pd


def merge_all(linkage_table_path, chrom_sizes_paths, conversion_tool_path,
              merge_tool_path):
    """
    Method merges all forward/reverse ATAC-seq files after converting them to
    bigWig format if necessary, checks if merged files need to be converted
    to bigWig and does so if true, then deletes old files nad adds entires for
    new files to the linkage table .csv file.

    :param linkage_table_path: String containing path to linking_table.csv
    :param chrom_sizes_paths: Array of Strings containing paths to all
           chrom.sizes files
    :param conversion_tool_path: String with path to bedGraphToBigWig tool
    :param merge_tool_path: String with path to bigWigMerge tool
    """

    linkage_frame = read_linkage_table(linkage_table_path)
    pairs = find_pairs(linkage_frame)
    column_names = linkage_frame.columns

    old_files = []
    merged_files = []
    rows = []

    #If file format of forward/reverse reads is bedGrapfh, then convert to
    #bigWig for merging tool and save paths of pre-conversion files to be
    #deleted later
    for pair in pairs:
        for i in range(0, len(pair)):
            if ".begraph" in pair[i].lower():
                genome = linkage_frame.loc[linkage_frame["file_path"] ==
                                           pair[i]]["genome"]
                #Find the right chrom.sizes file for genome
                chrom_sizes = [el for el in chrom_sizes_paths if genome in el]
                bw_file_path = convert_bedgraph_to_bigwig(pair[i],
                                                          chrom_sizes[0],
                                                          conversion_tool_path)
                old_files.append(pair[i])
                pair[i] = bw_file_path

    #Merge all file pairs with tool and save paths to new files
    for pair in pairs:
        merged_files.append(merge_pair(pair[0], pair[1], merge_tool_path))

    #add option to convert merged files to bigWig format

    #Check if there are any file paths saved from having converted
    #forward/reverse files to bigWig, if so delete them
    if len(old_files) > 0:
        for file in old_files:
            delete_file(file)

    #Delete all forward/reverse files in bigWig format now that they have
    #been merged
    for pair in pairs:
        for i in range(0, len(pair)):
            delete_file(pair[i])

    #Generate rows to append to linkage table .csv file for merged files
    for i in range(0, len(merged_files)):
        row = linkage_frame.loc[linkage_frame["file_path"] == pairs[i][0]]
        row["file_path"] = merged_files[i]
        row = row.to_csv()
        rows.append(row)

    #add merged file entries to linkage table
    #for row in rows:
        #add_row(row, linkage_table_path, column_names)


def read_linkage_table(linkage_table):
    """
    Method reads in .csv linkage table file via the given file path and
    returns a data frame with information on genome, bio-source and the file
    path for forward/reverse read ATAC-seq files.

    :return: linkage_frame: A data frame containing the columns "genome",
             "biosource", "file_path" for all forward/reverse reads files in
             need of merging
    """

    lt_path = linkage_table
    linkage_frame = pd.DataFrame()

    with open(lt_path) as lt:
        lt_reader = csv.DictReader(lt, delimiter=',')

        for row in lt_reader:
            if row["technique"].lower() == "atac-seq" and \
                    ("forward" in row["filename"].lower() or
                     "reverse" in row["filename"].lower()):
                tmp_series = pd.Series(row)
                linkage_frame = linkage_frame.append(tmp_series,
                                                     ignore_index=True)
    return linkage_frame


def find_pairs(linkage_frame):
    """
    Method pairs files that need to be merged

    :param linkage_frame: Data frame containing all important info for files
                          to be merged
    :return: paris: A list of tuples containing the file paths to the two
                    files that need to be merged with each other
    """

    pairs = []

    for i in range(0, len(linkage_frame["file_path"]) - 1):
        filename = linkage_frame["file_path"][i].split("/")[-1]
        file_id = filename.split(".")[0]
        if "chr" not in filename.lower():
            chrom = ""
        else:
            chrom = filename.split(".")[-2]

        for j in range(i + 1, len(linkage_frame["file_path"])):
            if linkage_frame["genome"][i] == linkage_frame["genome"][j] and \
                    linkage_frame["biosource"][i] == \
                    linkage_frame["biosource"][j] and file_id in \
                    linkage_frame["file_path"][j]:
                if len(chrom) > 0:
                    if chrom in linkage_frame["file_path"][j]:
                        pairs.append((linkage_frame["file_path"][i],
                                      linkage_frame["file_path"][j]))
                else:
                    pairs.append((linkage_frame["file_path"][i],
                                  linkage_frame["file_path"][j]))

    return pairs


def convert_bedgraph_to_bigwig(bg_file_path, chrom_sizes_path,
                               conversion_tool_path):
    """
    Method converts a bedGraph file into a bigWig file.

    :param bg_file_path: String containing path to bedGraph file
    :param chrom_sizes_path: String containing path to chrom.sizes file
    :param conversion_tool_path: String containing path to conversion tool
    :return: Path to new bigWig file
    """

    bw_file_path = "\"" + bg_file_path.rsplit(".", maxsplit=1)[0] + ".bw\""

    command = conversion_tool_path + " \"" + bg_file_path + "\" " + \
              chrom_sizes_path + " " + bw_file_path

    os.system(command)

    return bw_file_path


def merge_pair(bw_file_path_1, bw_file_path_2, merge_tool_path):
    """
    Method merges two bigWig forward/reverse read files into one bedGraph file

    :param bw_file_path_1: String containing path to first file
    :param bw_file_path_2: String containing path to second file
    :param merge_tool_path: String containing path to merging tool
    :return: Path to new merged file
    """

    merged_file_path = "\"" + bw_file_path_1.split("_")[0] + \
                       "_merged.bedGraph\""

    command = merge_tool_path + " \"" + bw_file_path_1 + "\" \"" + \
              bw_file_path_2 + "\" " + merged_file_path

    os.system(command)

    return merged_file_path


def delete_file(file_path):
    """
    Method deletes a file.

    :param file_path: Path to file in that needs to be deleted
    """
    command = "rm \"" + file_path + "\""

    os.system(command)