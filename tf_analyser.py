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
    parameter -w / --w= : parameter to define the range that will be analyzed (peak+-w)
    """

    # import score, author: Noah
    import score

    # TODO: import Jan's part

    # TODO: test if part one was executed

    # read in columns of the linking table that contain the names of the genomes, biosources and transcription factors
    # safe every column in a set to remove duplicates
    lt = pd.read_csv("linking_table.csv", sep=",", usecols=["genome", "epigenetic_mark", "biosample_term_name"])
    lt_genomes = set(lt.values[:, 0])
    lt_tfs = set(lt.values[:, 1][lt.values[:, 1] != "DNaseI"])
    lt_biosources = set(lt.values[:, 2])

    # default arguments for the input parameters
    genome = "hg19"
    tf = "all"
    biosource = "all"
    w = 50

    # test, if valid parameters were submitted
    # throw GetOptError if not, print help and exit program
    try:
        opts, args = getopt.getopt(argv[1:], "hg:b:t:w:", ["genome=", "biosource=", "tf=", "w="])
    except getopt.GetoptError:
        print('test.py -g <genome> -b <biosources> -t <transcription factors> -w <w>')
        exit(2)

    # parse submitted parameters
    for opt, arg in opts:

        # if -h is submitted, print explanation of the syntax for parameter submission and exit the program
        if opt == '-h':
            print('test.py -g <genome> -b <biosources> -t <transcription factors> -w <w>')
            exit()

        # if -g is submitted, set default genome to submitted
        # test if the submitted genome occurs in the linking_table
        # if not, print a message for the user containing usable genomes and exit the program
        elif opt in ("-g", "--genome"):
            genome = arg
            if genome in lt_genomes:
                pass
            else:
                print("the submitted genome '", genome,
                      "' does not exist within the data, please use one of the following: ", lt_genomes)
                exit(2)

        # if -b is submitted, set default biosources to submitted
        # test if submitted biosources are either 'all' or occur in the linking_table
        # if not, print a message containing usable biosources from the linking_table
        elif opt in ("-b", "--biosource"):
            biosource = arg.split(",")
            if len(biosource) == 1 and biosource[0] == 'all':
                biosource = 'all'
                pass
            else:
                for bs in biosource:
                    if bs in lt_biosources:
                        pass
                    else:
                        print("the submitted biosource '", bs,
                              "' does not exist within the data, please choose from the following: ", lt_biosources)
                        exit(2)

        # if -t is submitted, set default tf to submitted
        # test if submitted tf is 'all' or occurs in the linking_table
        # if not, print a message containing usable tfs from the linking_table and exit the program
        elif opt in ("-t", "--tf"):
            tf = arg.split(",")
            if len(tf) == 1 and tf[0] == 'all':
                tf = 'all'
                pass
            else:
                for t in tf:
                    if t in lt_tfs:
                        pass
                    else:
                        print("the submitted transcription factor '", t,
                              "' does not exist within the data, please choose from the following: ", lt_tfs)
                        exit(2)

        # if w is submitted, set the default w to the submitted
        # try to parse submitted value to int and throw ValueError if not possible
        elif opt in ("-w", "--w"):
            try:
                w = int(arg)
            except ValueError:
                print('w must be an integer')
                exit(2)

    # test if biosource or tf equals 'all'
    # if yes, set the value to all possible values from the linking_table
    if biosource == 'all':
        biosource = lt_biosources

    if tf == 'all':
        tf = lt_tfs

    # run the script score.py and store the calculated scores in the dictionary 'scores'
    scores = score.findarea(w, genome, biosource, tf)

    # test if 'scores' is an empty dictionary
    # if yes, notify that there is no data for the submitted combination of genome, biosource and
    # transcription factor and exit the program
    if scores:
        pass
    else:
        print("there is no data for your entered combination of genome, biosource and transcription factor")
        exit(3)

    # TODO: Jan's Part


if __name__ == '__main__':
    import pandas as pd
    import getopt
    from sys import *

    main()
