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
    """

    # import score, author: Noah
    import scripts.score

    # import analyse_main, author: Jan
    import scripts.analyse_main

    # TODO: test if part one was executed

    # read in columns of the linking table that contain the names of the genomes, biosources and transcription factors
    # safe every column in a sets to remove duplicates
    # extra set for biosources and tfs including 'all' used to declare possible choices for the user
    lt = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/linking_table.csv'), sep=',',
                     usecols=['genome', 'epigenetic_mark', 'biosample_term_name'])
    lt_genomes = set(lt.values[:, 0])
    lt_tfs = set(lt.values[:, 1][lt.values[:, 1] != 'DNaseI'])
    lt_tfs_choices = set(lt.values[:, 1][lt.values[:, 1] != 'DNaseI'])
    lt_tfs_choices.add('all')
    lt_biosources = set(lt.values[:, 2])
    lt_biosources_choices = set(lt.values[:, 2])
    lt_biosources_choices.add('all')

    # parse arguments submitted by the user
    parser = argparse.ArgumentParser(description='Analysis of transcription factors')
    parser.add_argument('-g', '--genome', default='hg19', type=str, choices=lt_genomes,
                        help='Allowed values are: \'' + ', '.join(lt_genomes) + '\'', metavar='GENOME')
    parser.add_argument('-b', '--biosource', default='all', type=str, choices=lt_biosources_choices, nargs='+',
                        help='Allowed values are: \'all\' or \'' + ', '.join(lt_biosources) + '\'', metavar='BIOSOURCE')
    parser.add_argument('-t', '--tf', default='all', type=str, choices=lt_tfs_choices, nargs='+',
                        help='Allowed values are: \'all\' or \'' + ', '.join(lt_tfs) + '\'',
                        metavar='TF')
    parser.add_argument('-w', '--width', default=50, type=int,
                        help='parameter to define the range that will be analyzed (peak+-w)')

    args = parser.parse_args()

    # test if biosource or tf equals 'all'
    # if yes, set the value to all possible values from the linking_table
    if 'all' in args.biosource:
        args.biosource = lt_biosources

    if 'all' in args.tf:
        args.tf = lt_tfs

    # run the script score.py and store the calculated scores in the dictionary 'scores'

    scores = scripts.score.findarea(args.width, args.genome, args.biosource, args.tf)

    # test if 'scores' is an empty dictionary
    # if yes, notify that there is no data for the submitted combination of genome, biosource and
    # transcription factor and exit the program
    if scores:
        pass
    else:
        print('there is no data for your entered combination of genome, biosource and transcription factor')
        exit(3)

    # generate plots with the script analyse_main.py
    resultframe = scripts.analyse_main.Main().mainloop(data=scores)
    print(resultframe)


if __name__ == '__main__':
    import pandas as pd
    from sys import *
    import argparse
    import os

    main()
