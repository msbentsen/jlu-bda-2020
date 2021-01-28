import subprocess
import os
from scripts.merge_reads import merge_files
from scripts.parser import parse


class data_config:
    """Contains configuration data for the pull_data function.    """

    def __init__(self, genome, biosource, epigenetic_mark, filetype):
        self.genome = genome
        self.biosource = biosource
        self.epigenetic_mark = epigenetic_mark
        self.basepath = os.getcwd()
        self.filetype = filetype


def pull_data(config):
    """Download and normalize data.

    This function attempts to download the data for the genome, biosource and
    epigenetic mark found in deepbluer, normalize it and sort it into a folder-
    structure then used for analyzing. While subfunctions can be called
    independently using this function is the recommended way.

    Args:
        config (class data_confih): [contains parameters for requested data]
    """
    generate_csv(config.path, config.genome,
                 config.biosource, config.epigenetic_mark)
    download_data(config.path)
    validate_convert_files(config.path, config.filetype)
    merge_forward_reversre(config.path)
    normalize(config.path)
    sort_files(config.path)
    generate_dictionaries()


def generate_csv(path, genome, biosource, epigenetic_mark):
    """Ǵenerate a .csv containing all files fitting the parameters.

    Calls csv.r and handles the return value.

    Args:
        path (string): current working directory
        genome (string): requested genome
        biosource (string): requested biosource
        epigenetic_mark (string list): requested epigenetic marks
    """
    rc = subprocess.call(
        [path + "/scripts/csv.r", biosource, genome, epigenetic_mark])
    if rc != 0:
        print("error generating .csv")


def download_data(path):
    """Download files from .csv

    Calls download.r and handles the return value.

    Args:
        path (string): current working directory
    """
    rc = subprocess.call([path + "/scripts/download.r",
                          path + "temp/linking_table.csv"])
    if rc != 0:
        print("error downloading datafiles")


def validate_convert_files(path, filetype):
    """ Validates filetypes and converts them to requested filetype if needed

    Calls convert_files.sh and handles return value

    Args:
        path (string): current working directory
        filetype (string): filetype to convert to (currently only .bw)
    """
    rc = subprocess.call(
        [path + "/scripts/convert_files.sh", "bigwig", path + "/temp"])
    if rc != 0:
        print("error converting datafiles ")


def merge_forward_reversre(path):
    """ merge forward/reverse read files into a single .bw

    Calls scripts.merge_files and handles return value
    Args:
        path (string): current working directory
    """
    rc = merge_files()
    if rc != 0:
        print("error merging datafiles")


def sort_files(path):
    """ merge forward/reverse read files into a single .bw

    Calls scripts.merge_files and handles return value
    Args:
        path (string): current working directory
    """
    rc = subprocess.call([path + "/scripts/sort_files.sh", path])
    if rc != 0:
        print("error sorting datafiles")


def normalize(path):
    """ Normalize files to allow proper analysis

    Calls scripts.normalize and handles return value
    Args:
        path (string): current working directory
    """
    pass


def generate_dictionaries():
    """Generate pickle files for the downloaded data """
    rc = parse()
    if rc != 0:
        print("error generating dictionaries")
