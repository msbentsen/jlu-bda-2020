import subprocess
import os


class data_config:
    def __init__(self, genome, biosource, epigenetic_mark, filetype):
        self.genome = genome
        self.biosource = biosource
        self.epigenetic_mark = epigenetic_mark
        self.basepath = os.getcwd()


def pull_data(config):
    generate_csv(config.path, config.genome,
                 config.biosource, config.epigenetic_mark)
    download_data(config.path)
    validate_convert_files(config.path, config.filetype)
    merge_forward_reversre(config.path)
    normalize(config.path)
    sort_files(config.path)
    generate_dictionaries()


def install_tools(path, tools):
    pass


def generate_csv(path, genome, biosource, epigenetic_mark):
    pass


def download_data(path):
    pass


def validate_convert_files(path, filetype):
    pass


def merge_forward_reversre(path):
    pass


def sort_files(path):
    pass


def normalize(path):
    pass


def generate_dictionaries():
    pass
