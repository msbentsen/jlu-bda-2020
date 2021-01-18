#!/bin/bash

filetype=$1
source_path=$2
csv_path=$3
chromsizes=$4

new_link=$source_path/linking.csv
export new_filename=""

validate_file () {
	local file_extension=${$1##*.}
	local filetype
	case "$3" in
	"CHROMOSOME,START,END,VALUE")
		filetype="bedgraph"
		;;
	"CHROMOSOME,START,END,NAME,SCORE,STRAND,SIGNAL_VALUE,P_VALUE,Q_VALUE,PEAK" \
	| "CHROMOSOME,START,END,NAME,SCORE,STRAND,SIGNAL_VALUE,P_VALUE,Q_VALUE" \
	| "CHROMOSOME,START,END,NAME,SCORE"\
	| "CHROMOSOME,START,END,NAME")
		filetype="bed"
		;;
	*)
		echo "unrecognized file format"
		filetype=""
		;;
	esac
	if [ "$filetype" != "$file_extension" ]; then
		new_filename="$(basename "$1").$filetype"
		return 1
	fi
	return 0
}


convert_files() {
	true
}

while IFS="," read -r experiment_id	genome	biosource	technique	\
	epigenetic_mark	filename	data_type	extension	format	remaining
do
	if [ ! -e "source_path/$filename" ]; then
		continue
	fi

	if [ "$extension" != "$filetype" ]; then
		source_file="$source_path$filename"
		if [[ "$(validate_filetype "$filename" "$extension" "$format")" != "0" ]]; then
			filename=${new_filename%.*}
			extension=${new_filename##*.}
		fi
		convert_file "$source_file" "$filetype" "$chromsizes/$genome"
	fi
	echo "$experiment_id,$genome,$biosource,$technique	\
	,$epigenetic_mark,$filename,$data_type,$extension,$format,$remaining"\
	>> "$new_link"
done < <(tail -n +2 "$csv_path")

mv "$new_link" "$source_path/linking_table.csv"
