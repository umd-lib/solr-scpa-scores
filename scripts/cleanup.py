#!/usr/bin/env python3

import csv
import sys

with open(sys.argv[1]) as ihandle, open(sys.argv[2], 'w') as ohandle:
    reader = csv.DictReader(ihandle)
    writer = csv.DictWriter(ohandle, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        row['id'] = f"{int(row['id']):08}"
        writer.writerow(row)
