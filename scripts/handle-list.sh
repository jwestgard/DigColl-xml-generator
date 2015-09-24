#!/usr/bin/env bash

while read pid
do
    echo "Fetching handle for $pid ..."
    handle=$(curl -sS "http://fedora.lib.umd.edu/handle/?action=lookup&pid=$pid" | \
    awk '/<handlehttp>/ {b=13; e=(length($0)-25); print substr($0,b,e)}')
    echo "$pid, $handle" >> result.csv
done 
