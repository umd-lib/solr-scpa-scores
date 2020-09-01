#!/usr/bin/env python3

import csv
import sys
import re

# Process a SCPA Scores Collection CSV file:
#
# - validate the input data and report problems
# - add the header
# - cleanup the input data
# - generate new columns for indexing

fieldnames = ['id', 'composer', 'title', 'imprint', 'instrumentation',
              'collation', 'additional_info', 'collection', 'call_number',
              'duration', 'solo_difficulty', 'difficulty', 'pages',
              'ensemble_description', 'ensemble_size', 'fair_use', 'special',
              'collection_dictionary', 'collection_sorted_dictionary']

collection_dict = {
    "ICA": "001::International Clarinet Association (ICA) Score Collection",
    "NACWPI": "002::National Association of College Wind and Percussion Instructors (NACWPI) Score Collection",
    "Stevens": "003::Milton Stevens Collection",
    "ABA": "004::American Bandmasters Association (ABA) Score Collection",
    "ABA - Banda Mexicana": "005::ABA - J.E. Roach Banda Mexicana Music Collection",
    "ABA - William Hill": "006::ABA - William Hill Collection",
    "ABA - King": "007::ABA - Karl King Scores",
    "ABA - Mayhew Lake": '008::ABA - Mayhew Lake "Symphony in Gold" Collection',
    "ABA - Reed": "009::ABA - Alfred Reed Collection",
    "ABA - Star Music Co": "010::ABA - Star Music Company Collection",
    "20th/21st Century Consort": "011::20th/21st Century Consort Collection",
    "Stephen Albert": "012::Stephen Albert Collection",
    "Harold Brown": "013::Harold Brown Collection",
    "CMP": "014::Contemporary Music Project (NAfME/MENC) Scores",
    "Lynn Steele": "015::Lynn Steele Collection",
    "George Tremblay": "016::George Tremblay Collection",
    "Philip Gordon": "017::Philip Gordon Papers",
    "VdGSA": "018::Viola da Gamba Society of America Archives"
}

p_multipipe = re.compile(r'\|+')
p_multispace = re.compile(r' *\| *')
p_trailingpipe = re.compile(r'\|$')

if __name__ == '__main__':
    def warn(field, msg):
        ''' Print validation warning message. '''

        print(f'row#={rownum}, id={id}, {field} field {msg}')

    # Open input file for reading and output file for writing
    with open(sys.argv[1]) as ihandle, open(sys.argv[2], 'w') as ohandle:
        reader = csv.DictReader(ihandle, fieldnames=fieldnames)
        writer = csv.DictWriter(ohandle, fieldnames=fieldnames)
        writer.writeheader()

        is_valid = True
        all_ids = set()

        for rownum, row in enumerate(reader, start=1):

            for field in fieldnames:
                new_value = row[field]

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
                        new_value = id

                    except ValueError as err:
                        id = "?"
                        warn(f'id', str(err))
                        is_valid = False

                else:

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

                if field == 'title':
                    if new_value == "":
                        new_value = "missing title"
                        warn('title', 'is empty')
                        is_valid = False

                if field == 'collection':
                    if new_value in collection_dict:
                        csd = collection_dict[new_value]
                        cd = csd.split('::')[1]
                    else:
                        csd, cd = '', ''
                        if new_value != "":
                            warn('collection', f'unknown value {new_value}')
                            is_valid = False

                    # add new fields
                    row['collection_dictionary'] = cd
                    row['collection_sorted_dictionary'] = csd

                if field == 'instrumentation':
                    # Remove in-between spaces in instrumentation
                    new_value = ','.join(e.strip() for e in
                                            new_value.split(','))

                row[field] = new_value

            writer.writerow(row)

    # Exit with error code if validation failed
    if is_valid:
        sys.exit(0)
    else:
        sys.exit(1)
