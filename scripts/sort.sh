#!/bin/bash

source_path=$1
dest_path=$2
csv_path=$3

new_link=$dest_path/linking.csv
head -n1 "$csv_path" > "$new_link"

while IFS="," read -r genome source seq_type tf data_type file_type file_path remaining
do
	if test -e "source_path/$file_path"; then
		continue
	fi

	if [ "$seq_type" == "atac_seq" ]; then
		new_path=$dest_path/$source/$seq_type/
	elif [ "$seq_type" == "chip_seq" ]; then
		new_path=$dest_path/$source/$seq_type/$tf/
	elif [ "$seq_type" == "dns_seq" ]; then
		new_path=$dest_path/$source/$seq_type/$tf/
	else
		echo "error, invalid sequencing technique"
		exit 1
	fi
	filename=$(basename file_path)
	mkdir -p "$new_path"
	sourcefile="$source_path$file_path"
	newfile="$new_path$filename"
	mv "$sourcefile" "$newfile"
	echo "$genome,$source,$seq_type,$tf,$data_type,$file_type,$FILE,$remaining" >> "$new_link"
done < <(tail -n +2 "$csv_path")
