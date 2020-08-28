#!/bin/bash

file_name=$1
dos2unix -f --newfile $file_name $file_name.unix
rm scpa-scores.csv

if [ "$2" =  "add-header" ]; then
  header=id,composer,title,imprint,instrumentation,collation,additional_info,collection,call_number,duration,solo_difficulty,difficulty,pages,ensemble_description,ensemble_size,fair_use,special
  echo $header > scpa-scores.csv
fi;

cat $file_name".unix" >> scpa-scores.csv

# Replace Control character K (represents multiple values) with PIPE
sed -i.bak s//\|/g scpa-scores.csv

# Replace multiple PIPEs with single PIPE
# (To get rid of empty values in a multivalued field
sed -i.bak -E 's/\|+/\|/g' scpa-scores.csv

# Trim extra spaces between values in a multivalued field
sed -i.bak -E 's/\ *\|\ */\|/g' scpa-scores.csv

# Trim extra space between fields
sed -i.bak -E 's/\ *,/,/g' scpa-scores.csv

# Trim beginning space inside quotes
sed -i.bak -E 's/^\"\ */\"/g' scpa-scores.csv
sed -i.bak -E 's/,\"\ */,\"/g' scpa-scores.csv

# Trim trailing space inside quotes
sed -i.bak -E 's/\ *\",/\",/g' scpa-scores.csv
sed -i.bak -E 's/\ *\"$/\"/g' scpa-scores.csv

# Remove trailing PIPE in a field
sed -i.bak -E 's/\|\"$/\"/g' scpa-scores.csv
sed -i.bak -E 's/\|\",/\",/g' scpa-scores.csv

# Copy instrumentaion field to a separate file
csvcut -c instrumentation scpa-scores.csv > instr

# Remove beginning, trailing, in-between spaces
sed -i.bak -E 's/,\ */,/g' instr
sed -i.bak -E 's/\ *\"/\"/g' instr
sed -i.bak 's/^\ *//g' instr
sed -i.bak 's/\ *$//g' instr

# Copy all fields except instrumentation to a new file
csvcut -C instrumentation scpa-scores.csv > others

# Join instrumentation and other fields
# Using "--no-inference" flag, so zero-padded id field doesn't lose padded zeros.
csvjoin --no-inference others instr > clean.csv

