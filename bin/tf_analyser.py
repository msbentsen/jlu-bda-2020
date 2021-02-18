"""
@author: Jasmin
"""


def main():
    """
    This function ties in all transcription factor analysis functions. It provides the interface for the user to pass
    parameters and run the analysis. The parameters are submitted via the command line.
    parameter  -h : help
    parameter -g / --genome= : genome
    parameter -b / --biosource= : one or more biosources divided by comma
    parameter -t / --tf= : one or more transcription factors divided by comma
    parameter -w / --width= : parameter to define the range that will be analyzed (peak+-w)
    parameter -r / --redo_analysis= : if stated, the analysis will be done for existing results
    parameter -v / --visualize= : if stated, the visualisation will be called for existing results
    """

    # import score, author: Noah
    import scripts.score

    # import analyse_main, author: Jan
    import scripts.analyse_main

    # import generate_data, author: Jonathan
    import generate_data

    # variable to declare if linking_table exists
    linking_table_exist = False

    # if linking_table exists:
    # read in columns of the linking table that contain the names of the downloaded genomes,
    # biosources and transcription factors  and safe every column in a set to remove duplicates
    # set variable linking_table_exist to True
    try:
        lt = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/linking_table.csv'), sep=';',
                         usecols=['genome', 'epigenetic_mark', 'biosource'])
        lt_genomes = set(lt.values[:, 0])
        lt_tfs = set(lt.values[:, 1][lt.values[:, 1] != ('DNaseI' or 'DNA Accessibility')])
        lt_biosources = set(lt.values[:, 2])
        linking_table_exist = True

    # if linking_table does not exist:
    # set list of downloaded genomes, biosources and tfs to "-"
    except FileNotFoundError:
        lt_genomes = "-"
        lt_tfs = "-"
        lt_biosources = "-"

    # links to deepbluer for possible genomes, biosources and tfs
    # given to the user if script is called with -h / --help
    genomelink = '\x1b]8;;https://deepblue.mpi-inf.mpg.de/dashboard.php#ajax/deepblue_view_genomes.php/\aDeepBlueR' \
                 '\x1b]8;;\a '
    biosourcelink = '\x1b]8;;https://deepblue.mpi-inf.mpg.de/dashboard.php#ajax/deepblue_view_biosources.php' \
                    '/\aDeepBlueR\x1b]8;;\a '
    tflink = '\x1b]8;;https://deepblue.mpi-inf.mpg.de/dashboard.php#ajax/deepblue_view_epigenetic_marks.php' \
             '/\aDeepBlueR\x1b]8;;\a '

    # parse arguments submitted by the user
    parser = argparse.ArgumentParser(description='Analysis of transcription factors',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-g', '--genome', default='hg19', type=str,
                        help='Allowed values are genome names from\n'
                             + genomelink + '\n'
                                            'You already downloaded the following genomes:\n' + ', '.join(lt_genomes),
                        metavar='GENOME')
    parser.add_argument('-b', '--biosource', default=['all'], type=str, nargs='+',
                        help='Allowed values are \'all\', \'downloaded\' or biosources from\n'
                             + biosourcelink + '\n'
                                               'You already downloaded the following biosources:\n' + ', '.join(
                            lt_biosources),
                        metavar='BIOSOURCE')
    parser.add_argument('-t', '--tf', default=['all'], type=str, nargs='+',
                        help='Allowed values are \'all\', \'downloaded\' or epigenetic marks from\n'
                             + tflink + '\n'
                                        'You already downloaded the following TFs:\n' + ', '.join(lt_tfs),
                        metavar='TF')
    parser.add_argument('-w', '--width', default=50, type=int,
                        help='parameter to define the range that will be analyzed (peak+-w)')
    parser.add_argument('-r', '--redo_analysis', default=False, type=bool, const=True, nargs='?',
                        help='existing results will be executed again and overwritten if argument is submitted')
    parser.add_argument('-v', '--visualize', default=False, type=bool, const=True, nargs='?',
                        help='visualization will be called for existing results')

    args = parser.parse_args()

    # if -v / --visualize was stated, call visualisation for existing results
    if args.visualize:
        print("Aufruf Visualisierung")

    # compute analysis
    else:

        # call "get_parameter_choices.r" to get all available genomes, biosources and tfs from deepbluer
        # reformat output of r script to get a separate list for genomes, biosources and tfs
        choices = subprocess.check_output("./bin/scripts/get_parameter_choices.r", shell=True).decode("utf-8")
        choices = re.sub(r" {2,}", "", choices)
        choices = re.sub(r"\[[0-9]*] ", "", choices).replace("\n", ",").replace("\"", "").split(";")

        genome_choices = choices[0].split(",")[0:-1]
        biosource_choices = choices[1].split(",")[1:-1]
        biosource_choices.append('all')
        biosource_choices.append('downloaded')
        tf_choices = choices[2].split(",")[1:-1]
        tf_choices.append('all')
        tf_choices.append('downloaded')
        for x in ("DNaseI", "DNA Accessibility"):
            if x in tf_choices:
                tf_choices.remove(x)

        # test if user input for genome, biosource and tf exists in deepbluer
        if args.genome not in genome_choices:
            print(
                "usage: tf_analyser.py [-h] [-g GENOME] [-b BIOSOURCE [BIOSOURCE ...]] [-t TF [TF ...]] [-w WIDTH] ["
                "-r [REDO_ANALYSIS]]")
            print("tf_analyser.py: error: argument -g/--genome: invalid choice: ", args.genome)
            exit(2)

        for bs in args.biosource:
            if bs not in biosource_choices:
                print(
                    "usage: tf_analyser.py [-h] [-g GENOME] [-b BIOSOURCE [BIOSOURCE ...]] [-t TF [TF ...]] [-w "
                    "WIDTH] [-r [REDO_ANALYSIS]]")
                print("tf_analyser.py: error: argument -b/--biosource: invalid choice: ", bs)
                exit(2)

        for tf in args.tf:
            if tf not in tf_choices:
                print(
                    "usage: tf_analyser.py [-h] [-g GENOME] [-b BIOSOURCE [BIOSOURCE ...]] [-t TF [TF ...]] [-w "
                    "WIDTH] [-r [REDO_ANALYSIS]]")
                print("tf_analyser.py: error: argument -t/--tf: invalid choice: ", tf)
                exit(2)

        # test if biosource or tf equals 'all'
        # if yes, set the value to all possible values from deepbluer
        if 'all' in args.biosource:
            args.biosource = biosource_choices

        if 'all' in args.tf:
            args.tf = tf_choices

        # test if biosource or tf equals 'all'
        # if yes, set the value to all possible values from deepbluer
        if 'downloaded' in args.biosource:
            if lt_biosources != '-':
                args.biosource = lt_biosources
            else:
                print("There is currently no data available. You need to download the data first.")
                exit(2)

        if 'downloaded' in args.tf:
            if lt_tfs != '-':
                args.tf = lt_tfs
            else:
                print("There is currently no data available. You need to download the data first.")
                exit(2)

        # test if user parameters are already downloaded
        # save parameter that need to be downloaded in the dictionary download_dict
        download_dict = {}
        if linking_table_exist:
            for bs in args.biosource:
                if len(lt.loc[(lt['genome'].str.lower() == args.genome.lower()) & (
                        lt['biosource'].str.lower() == bs.lower())]) >= 1:
                    for tf in args.tf:
                        if len(lt.loc[(lt['genome'].str.lower() == args.genome.lower()) & (
                                lt['biosource'].str.lower() == bs.lower()) & (
                                              lt['epigenetic_mark'].str.lower() == tf.lower())]) < 1:
                            if bs not in download_dict:
                                download_dict[bs] = [tf]
                            else:
                                download_dict[bs].append(tf)
                else:
                    download_dict[bs] = args.tf
        else:
            for bs in args.biosource:
                download_dict[bs] = args.tf

        # download data from download_dict
        if download_dict:
            for key in download_dict:
                requested_data = generate_data.DataConfig(args.genome, [key], download_dict[key])
                requested_data.pull_data()

        # run the script score.py and store the calculated scores in the dictionary 'scores'
        scores, exist = scripts.score.findarea(args.width, args.genome, args.biosource, args.tf, args.redo_analysis)

        # test if 'scores' is an empty dictionary
        # if not, generate plots with the script analyse_main.py
        # if yes and exist is True, pass (the plots are already exist in result)
        # if yes and exist is False, notify that there is no data for the submitted combination of genome, biosource and
        # transcription factor and exit the program
        if scores:
            resultframe = scripts.analyse_main.Main().mainloop(data=scores, genome=args.genome, width=args.width)
            print(resultframe)

        elif exist:
            pass

        else:
            print('there is no data for your entered combination of genome, biosource and transcription factor')
            exit(3)


if __name__ == '__main__':
    import pandas as pd
    from sys import *
    import argparse
    import os
    import subprocess
    import re
    from argparse import RawTextHelpFormatter

    main()
