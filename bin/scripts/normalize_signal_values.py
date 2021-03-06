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
import pyBigWig


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
    # linkage_table_old = linkage_table_old_path if linkage_table_old_path == \
    # "" else pd.read_csv(linkage_table_old_path)
    file_paths_new = list(linkage_table_new["file_path"])
    column_names_new = list(linkage_table_new["format"])
    # file_paths_old = linkage_table_old if linkage_table_old == "" else \
    # list(linkage_table_old["file_path"])
    # column_names_old = linkage_table_old if linkage_table_old == "" else \
    # list(linkage_table_old["format"])
    log_file_paths = []
    min_value = math.inf
    max_value = -math.inf

    # Log scale all newly downloaded files and save the paths to files with
    # log values
    for i in range(0, len(file_paths_new)):
        log_file_path = log_scale_file(file_paths_new[i], column_names_new[i])
        log_file_paths.append(log_file_path)

    # Find global min and global max values


def log_scale_file(file_path, column_names=None):
    """
    Method takes a file and writes a new file from it, which is a copy of the
    old one but with log scaled signal values in case the old file has bigWig
    format or a one column file containing only log signal values in case the
    old file has bed or bedGraph format. The new file is named after the
    old one with an additional ending .log.

    :param file_path: String of path to file to be read in
    :param column_names: List of Strings with column names in file. Is set to
           None, if not given
    :return: log_file_path: String containing path to log-scaled file
    """
    log_file_path = file_path + ".log"

    if is_big_wig(file_path):
        bw = pyBigWig.open(file_path)
        chrs = bw.chroms()
        header = list(chrs.items())
        bw_log = pyBigWig.open(log_file_path, 'w')
        bw_log.addHeader(header)

        for chrom in chrs.keys():
            intervals = bw.intervals(chrom)
            chromosomes = [chrom] * len(intervals)
            starts = [interval[0] for interval in intervals]
            ends = [interval[1] for interval in intervals]
            signal_values = [interval[2] for interval in intervals]
            log_values = numpy.log(signal_values)
            bw_log.addEntries(chromosomes, starts, ends=ends, values=log_values)

        bw.close()
        bw_log.close()

    else:
        idx = get_value_index(column_names)
        signal_values = numpy.loadtxt(file_path, usecols=[idx])
        log_values = numpy.log(signal_values)
        log_values = [str(value) + "\n" for value in log_values]

        with open(log_file_path, 'w') as log_file:
            log_file.writelines(log_values)

    return log_file_path


def get_min_max(log_file_path, min_val=math.inf, max_val=-math.inf):
    """
    Method finds min value and max value in a .log file.

    :param log_file_path: String with path to file with log values
    :param min_val: Start value for min. Is set to math.Inf if not given
    :param max_val: Start value for max. Is set to -math.Inf if not given
    :return: min and max as float
    """
    if is_big_wig(log_file_path):
        log_bw = pyBigWig.open(log_file_path)
        header = log_bw.header()
        tmp_min = header['minVal']
        tmp_max = header['maxVal']
        log_bw.close()

    else:
        signal_values = numpy.loadtxt(log_file_path, usecols=[0])
        tmp_min = min(signal_values)
        tmp_max = max(signal_values)

    min_val = tmp_min if tmp_min < min_val else min_val
    max_val = tmp_max if tmp_max > max_val else max_val

    return min_val, max_val


def min_max_scale_file(file_path, log_file_path, min_val,
                       max_val, column_names=None):
    """
    Method min-max scales values in file to a range between 0 and 1.

    :param file_path: String with path to file to be scaled
    :param log_file_path: String with path to file with log-scaled values of
           original file
    :param max_val: Global max value
    :param min_val: Global min value
    :param column_names: List of strings with names of columns in file,
           only needs to be given, if file is not bigWig format
    """
    tmp_file_path = file_path + ".tmp"

    if is_big_wig(file_path) and is_big_wig(log_file_path):
        bw = pyBigWig.open(file_path)
        log_bw = pyBigWig.open(log_file_path)
        chrs = bw.chroms()
        header = list(chrs.items())
        min_max_bw = pyBigWig.open(tmp_file_path, 'w')
        min_max_bw.addHeader(header)

        for chrom in chrs.keys():
            intervals = bw.intervals(chrom)
            log_intervals = log_bw.intervals(chrom)
            chromosomes = [chrom] * len(intervals)
            starts = [interval[0] for interval in intervals]
            ends = [interval[1] for interval in intervals]
            min_max_values = [(interval[2] - min_val) / (max_val - min_val) for
                              interval in log_intervals]
            min_max_bw.addEntries(chromosomes, starts, ends=ends,
                              values=min_max_values)

        bw.close()
        log_bw.close()
        min_max_bw.close()

    else:
        log_values = numpy.loadtxt(log_file_path, usecols=[0])
        min_max_values = [(x - min_val) / (max_val - min_val) for x in
                          log_values]
        idx = get_value_index(column_names)
        cnt = 0

        with open(file_path, 'r') as file, open(tmp_file_path, 'w') as tmp_file:
            for line in file:
                line_split = line.strip().split("\t")
                line_split[idx] = str(min_max_values[cnt])
                cnt += 1
                line_split.append("\n")
                line_write = "\t".join(line_split)
                tmp_file.write(line_write)

    os.rename(tmp_file_path, file_path)


def get_value_index(column_names):
    """
    Method gets column index of signal value in bed or bedGraph file.

    :param column_names: List of strings with names of columns in file
    :return: index: Integer representing index of column with signal value in
             file
    """
    if "SIGNAL_VALUE" in column_names:
        index = column_names.index("SIGNAL_VALUE")
    else:
        index = column_names.index("VALUE")

    return index


def is_big_wig(file_path):
    """
    Method checks if a file has bigWig format or not.

    :param file_path: String representing path to file
    :return: Boolean value. True if file has bigWig format, False if not
    """
    try:
        bw = pyBigWig.open(file_path)
        is_bw = bw.isBigWig()
        bw.close()
    except:
        is_bw = False

    return is_bw
