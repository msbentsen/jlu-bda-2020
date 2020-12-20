#!/bin/bash
#===============================================================================
#
#  FILE:  tools.sh
#
#  USAGE:  tools.sh [data directory path] [list of tools]
#
#  DESCRIPTION:  Check for the availability of ucsc tools. Additional arguments
#  my be given to check for additional tools. If a tool is not found the script
#  attempts to install it.
#
#  NOTES:  ---
#  AUTHOR:  Jonathan Schäfer
#===============================================================================

tools_path="$1/tools/"
mkdir --parents "$tools_path"
min_tools=("bedGraphToBigWig" "bigWigToBedGraph" "bigWigMerge")

#==== Function =================================================================
#  Name: validate
#  Description: attempt to exectute a tool to see if it is callable
#  Parameter 1: name of the tool to validate
#===============================================================================
validate() {
	"$tools_path$1"  >/dev/null 2>&1
	if [ "$?" == "127" ]; then
        return 1
	fi
    echo "$1 is installed"
    return 0
}

#==== Function =================================================================
#  Name: install_tool
#  Description: attempt to install a tool into the tool directory
#  Parameter 1: name of the tool to validate
#===============================================================================
install_tool() {
   wget --quiet --tries 2 "https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/$1"
   chmod u+x "./$1"
   mv "./$1" "$tools_path"
}

#==== Function =================================================================
#  Name: check
#  Description: checks wheter a tool is available and attempts to install if not
#  Parameter 1: name of the tool to validate
#===============================================================================
check () {
    validate "$1"
    local result=$?
    if [ $result -ne 0 ]; then
        echo "$1 is not installed, trying to install"
        install_tool "$1"
        validate "$1"
        result=$?
        if [ $result -ne 0 ]; then
            echo "$1 was not able to be installed"
        fi
    fi
}

#===============================================================================
#  goes through an array of minimally required tools to check/install and then
#  continues to go through every argument to check if necessary
#===============================================================================
for tool in "${min_tools[@]}"
do
    check "$tool"
done

if [ "$#" -gt 2 ]; then
    for arg in "${@:2}"
    do
       check "$arg"
    done
fi
