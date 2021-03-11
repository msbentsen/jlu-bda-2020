#!/bin/env bash

#===============================================================================
#
#  FILE:  sort.sh
#
#  USAGE:  sort.sh [data directory path] [destination directory path] [csv_path]
#
#  DESCRIPTION:  Sort files in data into a folderstructure in the destination
#				according to the parameters in the csv table, At the same time
#				adds the new filepath and cleans up the .csv. Files that do not
# 				exist anymore are deleted out of the .csv, this should only
#				affect the merging of forward/reverse reads, since those files
#				are only needed in the merged form.
#
#  NOTES:  ---
#  AUTHOR:  Jonathan Schäfer
#===============================================================================

source_path=$1
dest_path=$2
csv_path=$3
csv_name=$4
new_link=$dest_path/$csv_name

headers=$(head -n1 "$csv_path")
echo "$headers" > "$new_link"


#===============================================================================
# Goes through all lines of the .csv and sorts the files according to the
# sequencing technique, skipping non existing files to clean up the .csv .
#===============================================================================

atac="" # used to ensure dnase-seq also land in the proper atac-seq folder
while IFS=";" read -r experiment_id	genome	biosource	technique	\
	epigenetic_mark	chromosome filename	data_type	remaining
do
	if [ ! -e "$source_path/$filename" ]; then
		continue
	fi

	# lowercase comparison to ensure
	check=$(echo "$technique" | awk '{print tolower($0)}')
	if [ "$check" == "atac-seq" ]; then
		new_path="$dest_path/$biosource/$technique"
		atac=$technique
	elif [ "$check" == "chip-seq" ]; then
		new_path="$dest_path/$biosource/$technique/$epigenetic_mark"
	elif [ "$check" == "dnase-seq" ]; then
		new_path="$dest_path/$biosource/$atac"
	else
		new_path="$dest_path/$genome/$biosource/$technique/$epigenetic_mark"
	fi

	mkdir -p "$new_path"
	sourcefile="$source_path/$filename"
	newfile="$new_path/$filename"
	mv "$sourcefile" "$newfile"
	echo "$experiment_id;$genome;$biosource;$technique;$epigenetic_mark;\
$chromosome;$filename;$data_type;$newfile;$remaining" >> "$new_link"
done < <(tail -n +2 "$csv_path")


# TODO: temp linkage für logn in /temp
# data/l1.csv /erster parameter run
# data/l2.csv /zweiter parameter run
# data/temp/norm.csv /nura aktuelle angaben
# data/download/l1.csv
# data/download/l2.csv
