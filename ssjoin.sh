#!/bin/bash

METADATACSV=$1
LINKCSV=$2

echo "asset,SharestreamURL" > temp.csv
sed 1d $LINKCSV | csvcut -c1,4 >> temp.csv
csvjoin -c "FileName,asset" --left $METADATACSV temp.csv | csvcut -c "FileName,asset,SharestreamURL" | csvlook
