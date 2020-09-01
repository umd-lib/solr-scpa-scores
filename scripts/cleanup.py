#!/usr/bin/env python3

import csv
import sys
import re

fieldnames = ['id', 'composer', 'title', 'imprint', 'instrumentation',
              'collation', 'additional_info', 'collection', 'call_number',
              'duration', 'solo_difficulty', 'difficulty', 'pages',
              'ensemble_description', 'ensemble_size', 'fair_use', 'special']

p_multipipe = re.compile(r'\|+')
p_multispace = re.compile(r' *\| *')
p_trailingpipe = re.compile(r'\|$')

if __name__ == '__main__':
    def warn(msg):
        ''' Print validation warning message. '''

        print(f'row#={rownum}, id={id}, {msg}')

    # Open input file for reading and output file for writing
    with open(sys.argv[1]) as ihandle, open(sys.argv[2], 'w') as ohandle:
        reader = csv.DictReader(ihandle, fieldnames=fieldnames)
        writer = csv.DictWriter(ohandle, fieldnames=fieldnames)
        writer.writeheader()

        is_valid = True
        all_ids = set()

        for rownum, row in enumerate(reader, start=1):

            for field in fieldnames:
                if field == 'id':
                    id = row['id']

                    try:
                        id = int(id)
                        if id < 1:
                            raise ValueError(f'not a positive integer: {id}')

                        # Zero pad id to 8 digits
                        id = f"{int(row['id']):08}"

                        if id in all_ids:
                            raise ValueError(f'not unique: {id}')

                        all_ids.add(id)
                        row['id'] = id

                    except ValueError as err:
                        id = "?"
                        warn(f'id column: {err}')
                        is_valid = False

                else:
                    new_value = row[field]

                    # Replace Control character K (represents multiple values)
                    # with PIPE
                    new_value = new_value.replace('\v', '|')

                    # Replace multiple PIPEs with single PIPE
                    # (To get rid of empty values in a multivalued field
                    new_value = p_multipipe.sub('|', new_value)

                    # # Trim extra spaces between values in a multivalued field
                    new_value = p_multispace.sub('|', new_value)

                    # Trim extra space between fields
                    new_value = new_value.strip()

                    # Remove trailing PIPE in a field
                    new_value = p_trailingpipe.sub('', new_value)

                    # Remove in-between spaces in instrumentation
                    if field == 'instrumentation':
                        new_value = ','.join(e.strip() for e in
                                             new_value.split(','))

                    row[field] = new_value

            writer.writerow(row)

    # Exit with error code if validation failed
    if is_valid:
        sys.exit(0)
    else:
        sys.exit(1)
