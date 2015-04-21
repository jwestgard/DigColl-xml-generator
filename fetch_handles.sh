#!/usr/bin/env bash

INFILE=$1
OUTFILE=$2

touch result.csv
echo "filename,pid,handle" >> result.csv

while read filename pid
do
    echo "Fetching handle for $pid ..."
    handle=$(curl -sS "http://fedora.lib.umd.edu/handle/?action=lookup&pid=$pid" | \
    awk '/<handlehttp>/ {b=13; e=(length($0)-25); print substr($0,b,e)}')
    echo "$filename, $pid, $handle" >> result.csv
done < <(awk -F "," '$2=="\"UMDM\"" {gsub(/"/,""); print $1,$3}' $INFILE)

csvjoin -c 'Identifier,filename' --left $OUTFILE result.csv > handled.csv
