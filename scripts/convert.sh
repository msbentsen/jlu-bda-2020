#!/bin/bash

filetype=$1
source_path=$2
csv_path=$3
chromsizes=$4

new_link=$source_path/linking.csv


validate_file () {
	true
}


convert_files() {
	true
}

while IFS="," read -r genome source seq_type tf data_type file_type file_path remaining
do
	if test -e "source_path/$file_path"; then
		continue
	fi
	if [ "$file_type" != "$filetype" ]; then
		source_file="$source_path$file_path"
		validate_filetype "$source_file" "$seq_type"
		convert_file "$source_file" "$filetype" "$chromsizes/$genome"
	fi
	echo "$genome,$source,$seq_type,$tf,$data_type,$file_type,$FILE,$remaining" >> "$new_link"
done < <(tail -n +2 "$csv_path")
