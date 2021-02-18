"""
Methods for normalizing ATAC-seq and ChIP-seq signal values.

Goes through the following steps:
- Read in linkage table .csv file as data frame
- Log scale all files
- min-max scale all files (to a range of 0-1)

To-do:
- Bin size problem:
    - Narrow and broad peaks -> narrow peaks only has summit? One value for
      multiple pos? Problem that needs solving
- Min-max scaling:
    - Does it make sense to scale each file individually or do I need a
    global min and max?


Use as follows:

import normalize_signal_values




by Kristina Müller (kmlr81)
"""

import math
import os
import pandas as pd
import numpy


def normalize_all(linkage_table_new_path, linkage_table_old_path=""):
    """
    Method normalizes all files through log scaling first and then
    min-max scaling to a uniform range between 0 and 1.

    :param linkage_table_new_path: String with path to linkage table .csv
    file with files downloaded in current run
    :param linkage_table_old_path: String with path to linkage table .csv
    file with files downloaded in previous runs. If this file does not yet
    exist because there have been no previous runs it can be left with
    default value
    """
    linkage_table_new = pd.read_csv(linkage_table_new_path)
    #linkage_table_old = linkage_table_old_path if linkage_table_old_path == \
        #"" else pd.read_csv(linkage_table_old_path)
    file_paths_new = list(linkage_table_new["file_path"])
    column_names_new = list(linkage_table_new["format"])
    #file_paths_old = linkage_table_old if linkage_table_old == "" else \
        #list(linkage_table_old["file_path"])
    #column_names_old = linkage_table_old if linkage_table_old == "" else \
        #list(linkage_table_old["format"])
    log_file_paths = []
    min = math.inf
    max = -math.inf

    # Log scale all newly downloaded files and save the paths to files with
    # log values
    for i in range(0, len(file_paths_new)):
        log_file_path = log_scale_file(file_paths_new[i], column_names_new[i])
        log_file_paths.append(log_file_path)

    # Find global min and global max values


def log_scale_file(file_path, column_names):
    """
    Method takes a file and writes a new file from it, which is a copy of the
    old one but with log scaled signal values and the new file ending .log.

    :param file_path: String of path to file to be read in
    :param column_names: List of Strings with column names in file
    :return: log_file_path: String containing path to log-scaled file
    """
    log_file_path = file_path + ".log"
    idx = get_value_index(column_names)
    signal_values = numpy.loadtxt(file_path, usecols=[idx])
    log_values = numpy.log(signal_values)
    log_values = [str(value) + "\n" for value in log_values]

    with open(log_file_path, 'w') as tmp_file:
        tmp_file.writelines(log_values)

    return log_file_path


def get_min_max(file_path, min, max, column_names):
    """
    Method finds min value and max value in a file.

    :param file_path: String with path to file
    :param min: Start value for min. If method is called for first time
                math.Inf is recommended.
    :param max: Start value for max. If method is called for the first time
                -math.Inf is recommended.
    :param column_names: Array of Strings of column names in file
    :return: min and max as float
    """
    idx = get_value_index(column_names)
    signal_values = numpy.loadtxt(file_path, usecols=[idx])
    tmp_min = min(signal_values)
    tmp_max = max(signal_values)
    min = tmp_min if tmp_min < min else min
    max = tmp_max if tmp_max > max else max

    return min, max


def min_max_scale_file(file_path, log_file_path, column_names, min, max):
    """
    Method min-max scales values in file to a range between 0 and 1.

    :param file_path: String with path to file to be scaled
    :param log_file_path: String with path to file with log-scaled values of
    original file
    :param column_names: List of strings with names of columns in file
    :param max: Global max value
    :param min: Global min value
    """
    tmp_file_path = file_path.rsplit("/", maxsplit=1)[0] + "/tmp_file.txt"
    idx = get_value_index(column_names)
    log_values = numpy.loadtxt(log_file_path, usecols=[0])
    min_max_values = [str((x - min) / (max - min)) for x in log_values]
    cnt = 0

    with open(file_path, 'r') as file, open(tmp_file_path, 'w') as tmp_file:
        for line in file:
            line_split = line.strip().split("\t")
            line_split[idx] = min_max_values[cnt]
            cnt += 1
            line_split.append("\n")
            line_write = "\t".join(line_split)
            tmp_file.write(line_write)

    os.rename(tmp_file_path, file_path)


def get_value_index(column_names):
    """
    Method gets column index of signal value in file.

    :param column_names: List of strings with names of columns in file
    :return: index: Integer representing index of column with signal value in
                    file
    """
    if "SIGNAL_VALUE" in column_names:
        index = column_names.index("SIGNAL_VALUE")
    else:
        index = column_names.index("VALUE")

    return index
