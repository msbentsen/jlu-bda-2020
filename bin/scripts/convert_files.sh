#!/bin/env bash

#===============================================================================
#
#  FILE:  convert.sh
#
#  USAGE:  convert.sh [filetype to convert to] [path to files]
#					  [genome.chrom.size folder path] [name of csv]
#
#  DESCRIPTION:  Validate and convert  files in src_path according to the
#				parameters. At the same time ensure proper file-naming.
#
#  NOTES:  ---
#  AUTHOR:  Jonathan Schäfer
#===============================================================================
filetype=$1
source_path=$2
chrom_path=$3
csv_name=$4

new_link=$source_path/$csv_name.new
touch "$new_link"
export new_filename=""

# Strip .txt ending of downloaded files
rename '.txt' '' "$source_path/*"
#==== Function =================================================================
#  Name: validate_file
#  Description: Validates that the file extension of a file fits the content of
#  a file by comparing the filename to the format provided in the .csv
#  $1 = filename of the file to check
#  $2 = format of the filecontent
#===============================================================================
validate_filetype () {
	local file_extension=${1##*.}
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
		new_filename="${new_filename%.*}.$filetype"
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
convert_file() {
	local file_extension=${1##*.}
	local file_name=${1%.*}
	if [ "$2" == "bigwig" ] | [ "$2" == "bw" ]; then
		if  [ "$file_extension" == "bed" ]; then
			cut --fields 1-3,7 "$1" > "$file_name.bedgraph"
			file_extension="bedgraph"
		fi
		if [ "$file_extension" == "bedgraph" ]; then
			bedGraphToBigWig "$file_name.$file_extension" \
				"$4/$3.chrom.sizes" "$file_name.bw"
		else
				echo "unexpected file" # TODO: proper error handling
		fi
	fi
}


#===============================================================================
# Goes through all lines of the .csv and validates the file before attempting
# to convert it to the proper filetype
#===============================================================================
while IFS=";" read -r experiment_id	genome	biosource	technique	\
	epigenetic_mark	filename	data_type	format remaining
do
	if [ ! -e "$source_path/$filename" ]; then
		continue
	fi

	source_file="$source_path/$filename"

	if validate_filetype "$filename" "$format"; then
		mv "$source_file" "$source_path/$new_filename"
	 	source_file="$source_path/$new_filename"
	fi
	convert_file "$source_file" "$filetype" "$genome" "$chrom_path"

	echo "$experiment_id,$genome,$biosource,$technique	\
	,$epigenetic_mark,$filename,$data_type,$format, $remaining"\
	>> "$new_link"
done < <(tail --lines +2 "$source_path/$csv_name")

#replace out of date linking table with up to date one
mv "$new_link" "$source_path/$csv_name"
