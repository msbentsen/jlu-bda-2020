import subprocess
import os
from scripts.merge_reads import merge_files
from scripts.parser import parse


class data_config:
    def __init__(self, genome, biosource, epigenetic_mark, filetype):
        self.genome = genome
        self.biosource = biosource
        self.epigenetic_mark = epigenetic_mark
        self.basepath = os.getcwd()
        self.filetype = filetype


def pull_data(config):
    generate_csv(config.path, config.genome,
                 config.biosource, config.epigenetic_mark)
    download_data(config.path)
    validate_convert_files(config.path, config.filetype)
    merge_forward_reversre(config.path)
    normalize(config.path)
    sort_files(config.path)
    generate_dictionaries()


def generate_csv(path, genome, biosource, epigenetic_mark):
    rc = subprocess.call(
        [path + "/scripts/csv.r", biosource, genome, epigenetic_mark])
    if rc != 0:
        print("error generating .csv")


def download_data(path):
    rc = subprocess.call([path + "/scripts/download.r",
                          path + "temp/linking_table.csv"])
    if rc != 0:
        print("error downloading datafiles")


def validate_convert_files(path, filetype):
    rc = subprocess.call(
        [path + "/scripts/convert_files.sh", "bigwig", path + "/temp"])
    if rc != 0:
        print("error converting datafiles ")


def merge_forward_reversre(path):
    rc = merge_files()
    if rc != 0:
        print("error merging datafiles")


def sort_files(path):
    rc = subprocess.call([path + "/scripts/sort_files.sh", path])
    if rc != 0:
        print("error sorting datafiles")


def normalize(path):
    pass


def generate_dictionaries():
    rc = parse()
    if rc != 0:
        print("error generating dictionaries")
