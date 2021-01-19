# TODO: adapt folder names to provided data
"""
@author Jasmin
"""

def parse():
	"""
	This function creates dictionaries for the bed and bigwig files of the provided data. The dictionaries are stored in
	pickle files. For the bigwig files of ChIP-seq and ATAC-seq a separate pickle file is created for each biosource.
	For the bed files, a pickle file is created that contains the entire data.
	"""

	bed = {}
	biosources = os.listdir("Data")
	for biosource in biosources:
		if not os.path.exists('parsedData/ChIP-seq/' + biosource):
			os.mkdir('parsedData/ChIP-seq/' + biosource)
		if not os.path.exists('parsedData/ATAC-seq/' + biosource):
			os.mkdir('parsedData/ATAC-seq/' + biosource)
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
			chip[tf] = ("Data/" + biosource + "/ChIP-seq/" + tf + "/" + bigwig_file)
			with open('parsedData/ChIP-seq/' + biosource + '.pickle', 'wb') as handle:
				pickle.dump(chip, handle, protocol=pickle.HIGHEST_PROTOCOL)
			bs_bed_dict[tf] = bed_dict
		bed[biosource] = bs_bed_dict

		for f in os.listdir("Data/" + biosource + "/ATAC-seq"):
			if f.split(".")[1] == "bigWig":
				atac=("Data/" + biosource + "/ATAC-seq/" + f)
				with open('parsedData/ATAC-seq/' + biosource + '.pickle', 'wb') as handle:
					pickle.dump(atac, handle, protocol=pickle.HIGHEST_PROTOCOL)

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


if __name__ == '__main__':
	import pyBigWig
	import pickle
	import os

	parse()
