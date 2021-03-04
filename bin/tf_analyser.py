"""
@author: Jasmin
"""
import pandas as pd
import argparse
import os
from argparse import RawTextHelpFormatter
import xmlrpc.client as xc


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

    # call deepbluer to get all available genomes, biosources and tfs from deepbluer
    url = "http://deepblue.mpi-inf.mpg.de/xmlrpc"
    server = xc.Server(url, encoding='UTF-8', allow_none=True)
    user_key = "anonymous_key"

    genome_choices = [genome[1] for genome in server.list_genomes(user_key)[1]]
    genome_choices.sort()

    biosource_choices = [biosource[1] for biosource in server.list_biosources(None, user_key)[1]]
    biosource_choices.append('all')
    biosource_choices.append('downloaded')
    biosource_choices.sort()

    tf_choices = [tf[1] for tf in server.list_epigenetic_marks(None, user_key)[1]]
    tf_choices.append('all')
    tf_choices.append('downloaded')
    tf_choices = [x for x in tf_choices if x not in ["DnaseI", "DNA Accessibility"]]
    tf_choices.sort()

    chromosomes = {}
    chr_choices = []
    for genome in genome_choices:
        chr = [x[0] for x in server.chromosomes(genome, user_key)[1]]
        chr_choices += chr
        chromosomes[genome] = chr

    # if linking_table exists:
    # read in columns of the linking table that contain the names of the downloaded genomes,
    # biosources and transcription factors  and safe every column in a set to remove duplicates
    # set variable linking_table_exist to True
    try:
        lt = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/linking_table.csv'), sep=';',
                         usecols=['genome', 'epigenetic_mark', 'biosource_name'])
        lt_genomes = set(lt.values[:, 0])
        lt_tfs = [x.upper() for x in set(lt.values[:, 1][lt.values[:, 1] != ('dnasei' or 'dna accessibility')])]
        lt_biosources = set(x for x in lt.values[:, 2] if x in biosource_choices)
        linking_table_exist = True

    # if linking_table does not exist:
    # set list of downloaded genomes, biosources and tfs to "-"
    except FileNotFoundError:
        lt_genomes = None
        lt_tfs = None
        lt_biosources = None

    # links to deepbluer for possible genomes, biosources and tfs
    # given to the user if script is called with -h / --help
    genomelink = 'https://deepblue.mpi-inf.mpg.de/dashboard.php#ajax/deepblue_view_genomes.php'
    biosourcelink = 'https://deepblue.mpi-inf.mpg.de/dashboard.php#ajax/deepblue_view_biosources.php'
    tflink = 'https://deepblue.mpi-inf.mpg.de/dashboard.php#ajax/deepblue_view_epigenetic_marks.php'

    # parse arguments submitted by the user
    parser = argparse.ArgumentParser(description='Analysis of transcription factors',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-g', '--genome', default='hg19', type=str, choices=genome_choices,
                        help='Allowed values are genome names from\n' + genomelink + '\n You already downloaded the '
                                                                                     'following genomes:\n' + ', '.join(
                            ["None"] if lt_genomes is None else lt_genomes),
                        metavar='GENOME')
    parser.add_argument('-b', '--biosource', default=['all'], type=str, nargs='+', choices=biosource_choices,
                        help='Allowed values are \'all\', \'downloaded\' or biosources from\n' + biosourcelink + '\n '
                                                                                                                 'You already downloaded the following biosources:\n' + ', '.join(
                            ["None"] if lt_biosources is None else lt_biosources),
                        metavar='BIOSOURCE')
    parser.add_argument('-t', '--tf', default=['all'], type=str, nargs='+', choices=tf_choices,
                        help='Allowed values are \'all\', \'downloaded\' or epigenetic marks from\n' + tflink + '\n '
                                                                                                                'You already downloaded the following TFs:\n' + ', '.join(
                            ["None"] if lt_tfs is None else lt_tfs),
                        metavar='TF')
    parser.add_argument('-c', '--chromosome', default=['all'], type=str, nargs='+', choices=chr_choices,
                        help='Allowed values are \'all\' or the following chromosomes depending on the genome: \n',
                        metavar='CHROMOSOME')
    parser.add_argument('-w', '--width', default=50, type=int,
                        help='parameter to define the range that will be analyzed (peak+-w)')
    parser.add_argument('-r', '--redo_analysis', action='store_true',
                        help='existing results will be executed again and overwritten if argument is submitted')
    parser.add_argument('-v', '--visualize', action='store_true',
                        help='visualization will be called for existing results')
    parser.add_argument('-cs', '--component_size', type=int, nargs='?', help='component size')
    parser.add_argument('-o', '--output_path', default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                        type=str, nargs='?', help='output path')

    args = parser.parse_args()

    # if -v / --visualize was stated, call visualisation for existing results
    if args.visualize:
        print("Aufruf Visualisierung")

    # compute analysis
    else:
        # test if biosource or tf equals 'all'
        # if yes, set the value to all possible values from deepbluer
        if 'all' in args.biosource:
            args.biosource = biosource_choices
            args.biosource.remove('all')
            args.biosource.remove('downloaded')

        if 'all' in args.tf:
            args.tf = [x for x in tf_choices if x not in ["all", "downloaded"]]

        # test if biosource or tf equals 'all'
        # if yes, set the value to all possible values from deepbluer
        if 'downloaded' in args.biosource:
            if linking_table_exist:
                args.biosource = lt_biosources
            else:
                raise ValueError("There is currently no data available. You need to download the data first.")

        if 'downloaded' in args.tf:
            if linking_table_exist:
                args.tf = lt_tfs
            else:
                raise ValueError("There is currently no data available. You need to download the data first.")

        # test if user parameters are already downloaded
        # save parameter that need to be downloaded in the dictionary download_dict

        # download data from download_dict
        requested_data = generate_data.DataConfig(args.genome, args.biosource, args.tf, args.output_path,
                                                  'linkage_table.csv', os.path.abspath
                                                  (os.path.join(os.path.dirname(__file__), '../data/chromsizes/')))
        requested_data.pull_data()

        # run the script score.py and store the calculated scores in the dictionary 'scores'
        scores, exist = scripts.score.findarea(args.width, args.genome, args.biosource, args.tf, args.redo_analysis)

        # test if 'scores' is an empty dictionary
        # if not, generate plots with the script analyse_main.py
        # if yes and exist is True, pass (the plots are already exist in result)
        # if yes and exist is False, notify that there is no data for the submitted combination of genome, biosource and
        # transcription factor and exit the program
        if scores:
            resultframe = scripts.analyse_main.Main(genome=args.genome, width=args.width).mainloop(data=scores)
            print(resultframe)

        elif exist:
            pass

        else:
            raise Exception(
                'there is no data for your entered combination of genome, biosource and transcription factor')


if __name__ == '__main__':
    main()
