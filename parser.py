# TODO: add dictionary for ATAC-data
# TODO: adapt folder names to provided data

def parse():
    """
    This function creates dictionaries for the bed and bigwig files of the provided data. The dictionaries are stored in
    pickle files. For the bigwig files of ChIP-seq and ATAC-seq a separate pickle file is created for each biosource.
    For the bed files, a pickle file is created that contains the entire data.
    """
    ATAC = {}
    bed = {}
    biosources = os.listdir("Data")
    for biosource in biosources:
        bs_bed_dict = {}
        chip = {}
        tfs = os.listdir("Data/" + biosource + "/ChIP-seq")
        for tf in tfs:
            bed_dict = {}
            files = os.listdir("Data/" + biosource + "/ChIP-seq/" + tf)
            for f in files:
                if f.split(".")[1] == "bed":
                    bed_dict.update(read_bed("Data/" + biosource + "/ChIP-seq/" + tf + "/" + f))
                elif f.split(".")[1] == "bigWig":
                    bigwig_file = f
            chip[tf] = read_bigwig("Data/" + biosource + "/ChIP-seq/" + tf + "/" + bigwig_file, bed_dict)
            bs_bed_dict[tf] = bed_dict
        bed[biosource] = bs_bed_dict
        with open('parsedData/ChIP-seq/' + biosource + '.pickle', 'wb') as handle:
            pickle.dump(chip, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('parsedData/bed.pickle', 'wb') as handle:
        pickle.dump(bed, handle, protocol=pickle.HIGHEST_PROTOCOL)


def read_bed(file):
    """
    This function reads in a bed-file and returns the contained information in a dictionary.
    :param file: The path of the bed-file
    :return: chromosome is a dictionary with the chromosome as key and [start, stop, score, peak] as value
    """
    chromosome = {}
    for line in open(file):
        s = line.split("\t")
        start = int(s[1])
        stop = int(s[2])
        score = float(s[4])
        peak = int(s[9])
        if s[0] in chromosome:
            chromosome[s[0]].append([start, stop, score, peak])
        else:
            chromosome[s[0]] = [[start, stop, score, peak]]
    return chromosome


def read_bigwig(file, d):
    """
    This function reads a bigWig-file and returns the contained information in a dictionary.
    :param file: the path of the bigWig-file
    :param d: a dictionary created by the 'read_bed' function to specify the ranges to be read in
    :return: scores is a dictionary that contains the chromosome as key an a tuple containing tuples with the
             start position, stop position and the score between those positions
    """
    bw = pyBigWig.open(file)
    scores = {}
    for key in d:
        for pos in d[key]:
            s = bw.intervals(key, pos[0], pos[1])
            if key in scores:
                scores[key] = scores[key] + s
            else:
                scores[key] = s
    return scores


if __name__ == '__main__':
    import pyBigWig
    import pickle
    import os

    parse()
