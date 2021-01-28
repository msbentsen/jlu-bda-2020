#!/bin/bin/env bash

#===============================================================================
#
#  FILE:  convert.sh
#
#  USAGE:  convert.sh [filetype to convert to]
#					[path to files] [csv_path]
#
#  DESCRIPTION:  Validate and convert  files in src_path according to the
#				parameters. At the same time ensure proper file-naming.
#
#  NOTES:  ---
#  AUTHOR:  Jonathan Schäfer
#===============================================================================
filetype=$1
source_path=$2
csv_path=$3

new_link=$source_path/linking.csv
export new_filename=""


#==== Function =================================================================
#  Name: validate_file
#  Description: Validates that the file extension of a file fits the content of
#  a file by comparing the filename to the format provided in the .csv
#  $1 = filename of the file to check
#  $2 = format of the filecontent
#===============================================================================
validate_file () {
	local file_extension=${$1##*.}
	local filetype
	case "$2" in
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
		new_filename=$(basename "$1")
		new_filename="${$new_filename%.*}.$filetype"
		return 1
	fi
	return 0
}

#==== Function =================================================================
#  Name: convert_file
#  Description: Converts a file into the requested format (atm only bigwig).
#  converts .bed to .bedgraph and then calls the appropriate ucsc tool
#  $1 = file to convert
#  §2 = filetype to convert to
#  $3 = genome of the filecontent, needed for chrom.sizes
#=============================================================	==================
convert_files() {
	local file_extension=${$1##*.}
	local file_name=${$1%.*}
	if [ "$2" == "bigwig" ] | [ "$2" == "bw" ]; then
		if  [ "$file_extension" == "bed" ]; then
			cut --fields 1-3,7 "$source_path/$1" > "$source_path/$file_name.bedgraph"
			file_extension="bedgraph"
		fi
		if [ "$file_extension" == "bedgraph" ]; then
			./tools/bedGraphToBigWig "$file_name.$file_extension" \
				"$source_path/$3.chrom.sizes" "$file_name.bw"
		else
				echo "unexpected file" # TODO: proper error handling
		fi
	fi
}


#===============================================================================
# Goes through all lines of the .csv and validates the file before attempting
# to convert it to the proper filetype
#===============================================================================
while IFS="," read -r experiment_id	genome	biosource	technique	\
	epigenetic_mark	filename	data_type	format	remaining
do
	if [ ! -e "$source_path/$filename" ]; then
		continue
	fi

	source_file="$source_path/$filename"
	if [[ "$(validate_filetype "$filename" "$format")" != "0" ]]; then
	 filename=$new_filename
	fi
	convert_file "$source_file" "$filetype" "$genome"

	echo "$experiment_id,$genome,$biosource,$technique	\
	,$epigenetic_mark,$filename,$data_type,$format,$remaining"\
	>> "$new_link"
done < <(tail --lines +2 "$csv_path")

mv "$new_link" "$source_path/linking_table.csv"
