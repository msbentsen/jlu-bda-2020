import subprocess
import os
import logging
from datetime import datetime
from scripts.merge_reads import merge_all
from scripts.generate_pickle import parse


def setup():
    """
    Setup function to be called once. Sets up logging and
    Ensures proper filestructure is given.
    """
    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.path.pardir))
    time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

    if not os.path.exists('data/temp'):
        os.makedirs('data/temp')
    if not os.path.exists('results'):
        os.makedirs('results')
    if not os.path.exists('logs'):
        os.makedirs('logs')

    filename = path + "/logs/" + time + "_generate_data.log"
    logging.basicConfig(filename=filename, level=logging.INFO)
    return


class DataConfig:
    """Contains configuration data for the pull_data function.    """

    def __init__(self, genome, biosource, epigenetic_mark):
        self.genome = genome
        self.biosource = biosource
        self.epigenetic_mark = epigenetic_mark
        self.basepath = os.path.dirname(os.path.abspath(__file__))
        logging.info(self.genome + " " + self.biosource +
                     " " + self.epigenetic_mark)

    def pull_data(self):
        """ Recommended way to use this wrapper. Calls all needed functions.
        """

        self.generate_csv()
        self.download_data()
        self.validate_convert_files()
        self.merge_forward_reversre()
        self.normalize()
        self.sort_files()
        self.generate_dictionaries()

    def generate_csv(self):
        """Ǵenerate a .csv containing all files fitting the parameters.

        Calls csv.r and handles the return value.

        Args:
            path (string): current working directory
            genome (string): requested genome
            biosource (string): requested biosource
            epigenetic_mark (string list): requested epigenetic marks
        """
        rc = subprocess.call(
            [self.basepath + "/scripts/csv.r", "-b", self.biosource,
             "-g", self.genome,
             "-m", self.epigenetic_mark])
        if rc != 0:
            print("error generating .csv")

    def download_data(self):
        """Download files from .csv

        Calls download.r and handles the return value.

        Args:
            path (string): current working directory
        """
        rc = subprocess.call([self.basepath + "/scripts/export_from_csv.r", "-i",
                              self.basepath + "temp/linking_table.csv", "-o",
                              self.basepath + "temp"])
        if rc != 0:
            logging.error('Error downloading files:')

    def validate_convert_files(self):
        """ Validates filetypes and converts them to requested filetype if needed

        Calls convert_files.sh and handles return value

        Args:
            path (string): current working directory
            filetype (string): filetype to convert to (currently only .bw)
        """
        rc = subprocess.call(
            [self.basepath + "/scripts/convert_files.sh", "bigwig", self.basepath + "/temp"])
        if rc != 0:
            print("error converting datafiles ")

    def merge_forward_reversre(self):
        """ merge forward/reverse read files into a single .bw

        Calls scripts.merge_files and handles return value
        Args:
            path (string): current working directory
        """
        filepath = self.basepath + "/data/temp"
        chrompath = self.basepath + "/data/chromsizes"
        merge_all(filepath, chrompath, "stub", "stub")

    def sort_files(self):
        """ merge forward/reverse read files into a single .bw

        Calls scripts.merge_files and handles return value
        Args:
            path (string): current working directory
        """
        rc = subprocess.call(
            [self.basepath + "/scripts/sort_files.sh", self.basepath])
        if rc != 0:
            print("error sorting datafiles")

    def normalize(self):
        """ Normalize files to allow proper analysis

        Calls scripts.normalize and handles return value
        Args:
            path (string): current working directory
        """
        pass

    def generate_dictionaries(self):
        """Generate pickle files for the downloaded data """
        parse()
