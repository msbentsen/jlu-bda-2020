#!/bin/bash
tools_path="$1/tools/"
mkdir --parents "$tools_path"
min_tools=("bedGraphToBigWig" "bigWigToBedGraph" "bigWigMerge")

validate() {
	"$tools_path$1"  >/dev/null 2>&1
	if [ "$?" == "127" ]; then
        return 1
	fi
    echo "$1 is installed"
    return 0
}

install_tool() {
   wget --quiet --tries 2 "https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/$1"
   chmod u+x "./$1"
   mv "./$1" "$tools_path"
}

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
