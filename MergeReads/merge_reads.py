#import os

#os.system("")

def read_linkage_table():
    import csv


    lt_path = "Daten/linkage_table.csv"
    lt_rows = []
    file_dict = {}
    files = []
    genomes = []
    biosources = []


    with open(lt_path) as linkage_table:
        lt_reader = csv.DictReader(linkage_table, delimiter= ',')

        for row in lt_reader:
            lt_rows.append(row)


    for row in lt_rows:
        if row["Sequencing_Type"] == "ATAC-seq":
            files.append((row["Filename"], row["File_Path"]))
            genomes.append(row["Reference_Genome"])
            biosources.append(row["Biosource"])


    for i in range(1,len(genomes)):
        ref_genome = genomes[0]
        ref_biosource = biosources[0]
        tmp_files = []
        tmp_dict_bs = {}

        if ref_genome == genomes[i]:
            if ref_biosource == biosources[i]:
                tmp_files.append(files[i])
            elif ref_biosource != biosources[i] or i == len(biosources)-1:
                tmp_dict_bs[ref_biosource] = tmp_files
                ref_biosource = biosources[i]
                tmp_files.clear()
        elif ref_genome != genomes[i] or i == len(genomes)-1:
            file_dict[ref_genome] = tmp_dict_bs
            ref_genome = genomes[i]
            tmp_dict_bs.clear()
