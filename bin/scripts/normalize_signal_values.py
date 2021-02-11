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


def normalize_all(linkage_table_path):
    """
    Method normalizes all files through log scaling first and then
    min-max scaling to a uniform range between 0 and 1.

    :param linkage_table_path: String with path to linkage table .csv file
    """
    linkage_table = pd.read_csv(linkage_table_path)
    min = math.Inf
    max = -math.Inf


def log_scale_file(file_path, column_names):
    """
    Method reads in all signal values contained in a file and returns them
    for further processing.

    :param file_path: String of path to file to be read in
    :param column_names: List of Strings with column names in file
    """
    tmp_file_path = file_path.rsplit("/", maxsplit=1)[0] + "/" + "tmp_file.txt"
    idx = get_value_index(column_names)

    with open(file_path, 'r') as file, open(tmp_file_path, 'w') as tmp_file:
        for line in file:
            line_split = line.strip().split("\t")
            x = math.log(float(line_split[idx]))
            line_split[idx] = str(x)
            line_split.append("\n")
            line_write = "\t".join(line_split)
            tmp_file.write(line_write)

    os.rename(tmp_file_path, file_path)


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

    with open(file_path) as file:
        for line in file:
            val = float(line.strip().split("\t")[idx])
            min = val if val < min else min
            max = val if val > max else max

    return min, max


def min_max_scale_file(file_path, column_names, min, max):
    """
    Method min-max scales values in file to a range between 0 and 1.

    :param file_path: String with path to file to be scaled
    :param column_names: List of strings with names of columns in file
    """
    tmp_file_path = file_path.rsplit("/", maxsplit=1)[0] + "/" + "tmp_file.txt"
    idx = get_value_index(column_names)

    with open(file_path, 'r') as file, open(tmp_file_path, 'w') as tmp_file:
        for line in file:
            line_split = line.strip().split("\t")
            x = float(line_split[idx])
            line_split[idx] = str((x - min) / (max - min))
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
