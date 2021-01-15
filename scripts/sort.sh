#!/bin/bash
#===============================================================================
#
#  FILE:  sort.sh
#
#  USAGE:  sort.sh [data directory path] [destination directory path] [csv_path]
#
#  DESCRIPTION:  Sort files in data into a folderstructure in the destination
#				according to the parameters in the csv table
#
#  NOTES:  ---
#  AUTHOR:  Jonathan Schäfer
#===============================================================================

source_path=$1
dest_path=$2
csv_path=$3

new_link=$dest_path/linking.csv
head -n1 "$csv_path" > "$new_link"


#===============================================================================
# Goes through all lines of the .csv and sorts the files according to the
# sequencing technique.
#===============================================================================

while IFS="," read -r genome source seq_type tf data_type file_type \
file_path remaining
do
	if [ ! -e "$source_path/$file_path" ]; then
		continue
	fi

	if [ "$seq_type" == "ATAC-Seq" ]; then
		new_path=$dest_path/$source/$seq_type/
	elif [ "$seq_type" == "ChIP-seq" ]; then
		new_path=$dest_path/$source/$seq_type/$tf/
	elif [ "$seq_type" == "DNase-seq" ]; then
		new_path=$dest_path/$source/$seq_type/$tf/
	else
		echo "error, invalid sequencing technique for file $file_path"
		exit 1
	fi

	filename=$(basename file_path)
	mkdir -p "$new_path"
	sourcefile="$source_path$file_path"
	newfile="$new_path$filename"
	mv "$sourcefile" "$newfile"
	echo "$genome,$source,$seq_type,$tf,$data_type,$file_type,$FILE,$remaining" >> "$new_link"
done < <(tail -n +2 "$csv_path")
