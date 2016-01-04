#!/bin/bash

# Caution!!!!
# entry.list short_name.idx must be UTF-8 Without BOM

# step 1. modify entry.list file manually
# [start, end]  first page no = 1

# step 2. download the new indices
rm -rf ./index/*
python genDownloadIndexScript.py

# step 3. parse the indices, download htmls and output the Year CSV File
rm -rf ./data/*
python ParseIndex.py 2015

# step 4. run stat to pre-stating
python Stat.py

# step 5. Merge stat.py and the Year.csv
python MergeCSV.py 2015

# step 5. convert merge2014.csv [UTF-8 BOM] to merge2014.xls and use error.stat to modify wrong records

# step 6. convert merge2014.xls to calc2014.csv then calc the result csv
python Calc.py 2015

# step 7. convert the result csv file to xls results and report
