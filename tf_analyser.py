def main():
    import score
    # import Jans Teil

    # test if part one was executed
    # if no: execute part one

    lt = pd.read_csv("linking_table.csv", sep=",", usecols=["genome", "epigenetic_mark", "biosample_term_name"])
    genomes = set(lt.values[:, 0])
    tfs = set(lt.values[:, 1][lt.values[:, 1] != "DNaseI"])
    biosources = set(lt.values[:, 2])

    # input arguments
    genome = "hg19"
    tf = "all"
    biosource = "all"
    w = 50
    try:
        opts, args = getopt.getopt(argv[1:], "hg:b:t:w:", ["genome=", "biosource=", "tf=", "w="])
    except getopt.GetoptError:
        print('test.py -g <genome> -b <biosources> -t <transcription factors> -w <w>')
        exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -g <genome> -b <biosources> -t <transcription factors> -w <w>')
            exit()
        elif opt in ("-g", "--genome"):
            genome = arg
            if genome in genomes:
                pass
            else:
                print("the submitted genome '", genome,
                      "' does not exist within the data, please use one of the following: ", genomes)
                exit(2)
        elif opt in ("-b", "--biosource"):
            biosource = arg.split(",")
            if len(biosource) == 1 and biosource[0] == 'all':
                biosource = 'all'
                pass
            else:
                for bs in biosource:
                    if bs in biosources:
                        pass
                    else:
                        print("the submitted biosource '", bs,
                              "' does not exist within the data, please choose from the following: ", biosources)
                        exit(2)
        elif opt in ("-t", "--tf"):
            tf = arg.split(",")
            if len(tf) == 1 and tf[0] == 'all':
                tf = 'all'
                pass
            else:
                for t in tf:
                    if t in tfs:
                        pass
                    else:
                        print("the submitted transcription factor '", t,
                              "' does not exist within the data, please choose from the following: ", tfs)
                        exit(2)
        elif opt in ("-w", "--w"):
            try:
                w = int(arg)
            except ValueError:
                print('w must be an integer')
                exit(2)

    if biosource == 'all':
        biosource = biosources

    if tf == 'all':
        tf = tfs

    print('genome is "', genome)
    print('biosource is "', biosource)
    print('tf is   ', tf)
    print('w is   ', w)

    try:
        scores = score.findarea(w, genome, biosource, tf)
    except ValueError:
        scores = {}

    if scores:
        pass
    else:
        print("there is no output for your entered combination of genome, biosource and transcription factor")
        exit(3)
    # result=Jans Pipeline(scores)


if __name__ == '__main__':
    import pandas as pd
    import getopt
    from sys import *

    main()
