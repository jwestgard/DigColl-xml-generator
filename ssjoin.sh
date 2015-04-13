#!/bin/bash

METADATACSV=$1
LINKCSV=$2

# Join the two files
csvjoin -c "FileName,asset" --left \
  <(csvcut -C "SharestreamURLs" < $METADATACSV) \
  <(echo "asset,SharestreamURLs"; sed 1d $LINKCSV | \
  csvcut -c "Asset Title, Streamable Deeplink URL")
