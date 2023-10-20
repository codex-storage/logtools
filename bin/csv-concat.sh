#!/usr/bin/env bash
# Concatenates CSV files that have identical headers by removing the header from all but the first file. This is
# meant to be used after a call to `cat`; e.g., cat csv1.csv csv2.csv | lscsv-concat.sh
set -e

header=$(head -n 1)
echo "$header"
grep "$header" -Fv