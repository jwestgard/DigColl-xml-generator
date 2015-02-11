#!/bin/bash

METADATACSV=$1
LINKCSV=$2

# Set up header row for a temp file to hold the Sharestream data
echo "asset,SharestreamURLs" > sstemp.csv

# Copy needed columns from Sharestream download to the temp file
sed 1d $LINKCSV | csvcut -c1,4 >> sstemp.csv

# Remove SharestreamURLs column from metadata CSV
csvcut -C "SharestreamURLs" < $METADATACSV > metatemp.csv

# Join the two files
csvjoin -c "FileName,asset" --left metatemp.csv sstemp.csv > joined.csv

# Clean up
rm sstemp.csv metatemp.csv
