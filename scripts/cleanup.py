#!/usr/bin/env python3

import csv
import sys
import re
from unittest import TestLoader, TextTestRunner, TestCase

# Process a SCPA Scores Collection CSV file:
#
# - validate the input data and report problems
# - add the header
# - cleanup the input data
# - generate new fields for indexing

fieldnames = ['id', 'composer', 'title', 'imprint', 'instrumentation',
              'collation', 'additional_info', 'collection', 'call_number',
              'duration', 'solo_difficulty', 'difficulty', 'pages',
              'ensemble_description', 'ensemble_size', 'fair_use', 'special']

new_fieldnames = ['collection_dictionary', 'collection_sorted_dictionary',
                  'instrumentation_dictionary',
                  'instrumentation_dictionary_full',
                  'instrumentation_dictionary_full_with_alt']

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

# Instrument code to label map
inst_dict = {
    "any": "any instrument",
    "any-bb": "any b-flat instrument",
    "any-bc": "any bass clef instrument",
    "any-eb": "any e-flat instrument",
    "any-melody": "any melody instrument",
    "any-tc": "any treble clef instrument",
    "basso-continuo": "basso continuo",
    "ondes-martenot": "ondes martenot",
    "org": "organ",
    "pno": "piano",
    "pno-prep": "prepared piano",
    "pno-toy": "toy piano",
    "synth": "synthesizer",
    "cymbal-finger": "finger cymbal",
    "drum-bass": "bass drum",
    "drum-hand": "hand drum",
    "drum-snr": "snare drum",
    "drum-st": "drum set",
    "glock": "glockenspiel",
    "mrmba": "marimba",
    "perc": "percussion",
    "rhythm": "rhythm section",
    "tamb": "tambourine",
    "timp": "timpani",
    "xylo": "xylophone",
    "bsn": "bassoon",
    "cl": "clarinet",
    "cl-a": "a clarinet",
    "cl-alt": "alto clarinet",
    "cl-alt-f": "f alto clarinet",
    "cl-bb": "b-flat clarinet",
    "cl-bs": "bass clarinet",
    "cl-c": "c clarinet",
    "cl-choir": "clarinet choir",
    "cl-ctralt": "contralto clarinet",
    "cl-ctralt-bb": "b-flat contralto clarinet",
    "cl-ctralt-eb": "e-flat contralto clarinet",
    "cl-ctrbs": "contrabass clarinet",
    "cl-ctrbs-bb": "b-flat contrabass clarinet",
    "cl-ctrbs-eb": "e-flat contrabass clarinet",
    "cl-eb": "e-flat clarinet",
    "cl-eb-alt": "alto e-flat clarinet",
    "cl-sop": "soprano clarinet",
    "cl-sop-ab": "a-flat soprano clarinet",
    "cl-sop-bb": "b-flat soprano clarinet",
    "cl-sop-eb": "e-flat soprano clarinet",
    "ctrbs": "contrabassoon",
    "ctrbs-bb": "e-flat contrabassoon",
    "ctrbs-eb": "b-flat contrabassoon",
    "fl": "flute",
    "fl-a": "alto flute",
    "fl-bs": "bass flute",
    "hrn-eng": "english horn",
    "ob": "oboe",
    "picc": "piccolo",
    "rec": "recorder",
    "rec-alt": "alto recorder",
    "rec-bs": "bass recorder",
    "rec-sop": "soprano recorder",
    "rec-ten": "tenor recorder",
    "sax": "saxophone",
    "sax-alt": "alto saxophone",
    "sax-alt-eb": "alto e-flat saxophone",
    "sax-b": "bass saxophone",
    "sax-bar-eb": "baritone e-flat saxophone",
    "sax-bari": "baritone saxophone",
    "sax-bb": "b-flat saxophone",
    "sax-bb-sop": "b-flat soprano saxophone",
    "sax-bs": "bass saxophone",
    "sax-c": "c saxophone",
    "sax-eb": "e-flat saxophone",
    "sax-eb-alt": "e-flat alto saxophone",
    "sax-f-mezsop": "f mezzo-soprano saxophone",
    "sax-sop": "soprano saxophone",
    "sax-ten": "tenor saxophone",
    "woodwinds": "woodwind instruments",
    "woodwinds-choir": "woodwind choir",
    "woodwinds-orch": "wind orchestra",
    "bari": "baritone",
    "bari-bc": "bass clef baritone",
    "bari-tc": "treble clef baritone",
    "brass": "brass instruments",
    "cor": "cornet",
    "euph": "euphonium",
    "hrn": "horn",
    "hrn-a": "a horn",
    "hrn-basst": "basset horn",
    "hrn-bb": "b-flat horn",
    "hrn-c": "c horn",
    "hrn-d": "d horn",
    "hrn-e": "e horn",
    "hrn-eb": "e-flat horn",
    "tba": "tuba",
    "tba-bb": "b-flat tuba",
    "tba-bs": "bass tuba",
    "tba-c": "c tuba",
    "tba-eb": "e-flat tuba",
    "tba-f": "f tuba",
    "tba-tc": "treble clef tuba",
    "tbn": "trombone",
    "tbn-alt": "alto trombone",
    "tbn-bs": "bass trombone",
    "tbn-f": "trombone with f attachment",
    "tbn-ten": "tenor trombone",
    "tpt": "trumpet",
    "tpt-a": "a trumpet",
    "tpt-bb": "b-flat trumpet",
    "tpt-c": "c trumpet",
    "tpt-d": "d trumpet",
    "tpt-eb": "e-flat trumpet",
    "tpt-f": "f trumpet",
    "tpt-picc": "piccolo trumpet",
    "gtr": "guitar",
    "strings": "string instruments",
    "strings-quar": "string quartet",
    "vcl": "cello (violincello)",
    "vla": "viola",
    "vla-dg": "viola da gamba",
    "vln": "violin",
    "narr": "narrator",
    "satb": "choir",
    "voice-alt": "alto voice",
    "voice-bar": "baritone voice",
    "voice-bass": "bass voice",
    "voice-mez-sop": "mezzo soprano voice",
    "voice-sop": "soprano voice",
    "voice-ten": "tenor voice",
    "band-brass": "brass band",
    "band-concert": "concert band",
    "band-marching": "marching band",
    "band-symph": "symphonic band",
    "jazz": "jazz ensemble",
    "orch": "orchestra",
    "orch-chamber": "chamber orchestra",
    "orch-polka": "polka orchestra",
    "orch-string": "string orchestra",
    "accord": "accordion",
    "conch": "conch shell",
    "gtr-bs": "bass guitar",
    "penny-whistle": "penny whistle",
    "opt": "optional",
    "ens": "ensemble"
}

p_multipipe = re.compile(r'\|+')
p_multispace = re.compile(r' *\| *')
p_trailingpipe = re.compile(r'\|$')
p_inst = re.compile(r'([\w-]+?) *\( *([0-9]+|ens|opt) *\)')


def inst_sort_key(obj):
    '''
    Sort instruments by:
    0 - without alternatives
    1 - alternatives with counts other than 1
    2 - alternatives with all counts of 1
    '''

    if len(obj) == 1:
        return 0
    elif len(obj) > 1 and any(s[1] != 1 for s in obj):
        return 1
    else:
        return 2


def parse_inst(inst):
    '''
    Parse a single instrument code with optional count in parens, eg:
      code
      code(1)
      code(10)
      code(opt)
      code(ens)

    Return a tuple with (code, count)
    '''

    match = p_inst.match(inst)
    if match:
        code = match.group(1)
        try:
            count = match.group(2)
            if count == 'opt':
                count = 'optional'
            elif count == 'ens':
                count = 'ensemble'
            else:
                count = int(count)
        except:
            count = 1
    else:
        code, count = inst, 1

    return (code, count)


def parse_inst_list(value):
    '''
    Parse the list of instruments w/ alternatives in the instrumentation field.
    '''

    parsed = [alt.strip() for alt in value.lower().split(',')]
    parsed = [[parse_inst(i.strip()) for i in alt.split('|')]
              for alt in parsed if alt != ""]

    # Sort the instrument list
    return sorted(parsed, key=inst_sort_key)

def get_inst_dict(inst):
    ''' Get the full name of the inst code from inst_dict. '''

    if inst in inst_dict:
        return inst_dict[inst]
    else:
        return inst


def get_name_with_count(name, count):
    ''' Join the name with count for display. '''

    if isinstance(count, int):
        return f'{count} {name}'
    else:
        return f'{name} [{count}]'


def get_idf(name, count, name_with_count):
    ''' Get the value for instrumentation_dictionary_full. '''

    if isinstance(count, int):
        count = f'{count:03}'

    return f'{name}{count}::{name_with_count}'


def get_instrument_fields(new_value):
    '''
    Parse the instrumentation field and build new fields:

      instrumentation_dictionary - faceting
      instrumentation_dictionary_full - faceting (dependent)
      instrumentation_dictionary_full_with_alt - display
    '''

    id, idf, idfwa = [], [], []

    # Parse the instrument list, splitting on ',' and their
    # alternatives on '|'.
    inst_values = parse_inst_list(new_value)

    # Get unique instrument codes, in order
    sorted_insts = []

    # Iterate over the instrument list
    for alt in inst_values:

        display_name = []

        # Get list of unique instruments in the alternatives list
        insts = []
        for inst, _ in alt:
            if inst not in insts:
                insts.append(inst)
            if inst not in sorted_insts:
                sorted_insts.append(inst)

        # Iterate over the instruments
        for inst in insts:

            # Get the instrument full name
            name = get_inst_dict(inst)

            if name not in id:
                # Add the id facet (only once per instrument)
                id.append(name)

            # Get the alternative counts for this instrument
            inst_counts = [i[1] for i in alt if i[0] == inst]

            # Get the display names (idfwa) for this instrument
            for count in inst_counts:
                display_name.append(get_name_with_count(name, count))

        # Add the display names
        idfwa.append(' OR '.join(display_name))

    # Iterate over the instruments in their sorted order
    for sorted_inst in sorted_insts:

        counts = [0]
        all_counts = set()

        # Iterate over the instrument list
        for alt in inst_values:

            # Get list of unique instruments in the alternatives list
            insts = []
            for inst, _ in alt:
                if inst not in insts:
                    insts.append(inst)

            if sorted_inst in insts:

                # Get the alternative counts for this instrument
                inst_counts = [i[1] for i in alt if i[0] == sorted_inst]

                # Now determine the new cumulative counts for this instrument

                if len(insts) > 1:
                    # If there instruments other than this one, then 0 is a
                    # possible count for this instrument
                    inst_counts.append(0)

                old_counts = list(counts)
                new_counts = []
                for old_count in old_counts:
                    for count in inst_counts:

                        if isinstance(count, int) and isinstance(old_count, int):
                            new_count = old_count + count

                            if new_count in all_counts:
                                # Skip ones we've seen before
                                continue

                            new_counts.append(new_count)
                            all_counts.add(new_count)
                        else:
                            new_counts = [count]
                            all_counts.add(count)
                counts = new_counts

        # Get the instrument full name
        name = get_inst_dict(sorted_inst)

        for count in all_counts:
            if count != 0:
                name_with_idf_count = get_name_with_count(name, count)

                idf.append(get_idf(name, count, name_with_idf_count))

    return id, idf, idfwa


def cleanup():
    ''' Main loop for cleanup and validation. '''

    def warn(field, msg):
        ''' Print validation warning message. '''
        print(f'row#={rownum}, id={id}, {field} field {msg}')

    # Open input file for reading and output file for writing
    with open(sys.argv[1]) as ihandle, open(sys.argv[2], 'w') as ohandle:
        reader = csv.DictReader(ihandle, fieldnames=fieldnames)
        writer = csv.DictWriter(ohandle, fieldnames=fieldnames+new_fieldnames)
        writer.writeheader()

        is_valid = True
        all_ids = set()

        # Iterate over the input rows
        for rownum, row in enumerate(reader, start=1):

            # Iterate over the fields in each row
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

                    # Trim extra spaces between values in a multivalued field
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

                    if new_value != "":

                        field_id, field_idf, field_idfwa = \
                            get_instrument_fields(new_value)

                        row['instrumentation_dictionary'] = \
                            ','.join(field_id)

                        row['instrumentation_dictionary_full'] = \
                            ','.join(field_idf)

                        row['instrumentation_dictionary_full_with_alt'] = \
                            ','.join(field_idfwa)


                row[field] = new_value

            writer.writerow(row)

    # Exit with error code if validation failed
    # TODO: enable this once we want to enforce validation
    #
    # if is_valid:
    #     sys.exit(0)
    # else:
    #     sys.exit(1)

class Test(TestCase):

    def test_parse_inst(self):
        self.assertEqual(parse_inst('foo'), ('foo', 1))
        self.assertEqual(parse_inst('foo_bar'), ('foo_bar', 1))
        self.assertEqual(parse_inst('foo2'), ('foo2', 1))
        self.assertEqual(parse_inst('cl-bb (3)'), ('cl-bb', 3))

        self.assertEqual(parse_inst('foo (2)'), ('foo', 2))
        self.assertEqual(parse_inst('foo (10)'), ('foo', 10))
        self.assertEqual(parse_inst('foo ( opt )'), ('foo', 'optional'))
        self.assertEqual(parse_inst('foo(ens) '), ('foo', 'ensemble'))

        self.assertEqual(parse_inst('foo (bad)'), ('foo (bad)', 1))
        self.assertEqual(parse_inst('foo bad'), ('foo bad', 1))

    def test_parse_inst_list(self):
        self.assertEqual(parse_inst_list('cl (2)'),
                         [[('cl', 2)]])

        self.assertEqual(parse_inst_list('cl, bsn'),
                         [[('cl', 1)], [('bsn', 1)]])

        self.assertEqual(parse_inst_list('cl,, bsn,'),
                         [[('cl', 1)], [('bsn', 1)]])

        self.assertEqual(parse_inst_list('cl-bb (4)|cl-bb (2), cl-alt, cl-bs'),
                         [[('cl-alt', 1)], [('cl-bs', 1)],
                          [('cl-bb', 4), ('cl-bb', 2)]])

        self.assertEqual(parse_inst_list('pno,cl|vln,cl(2)|cl(3)'),
                         [[('pno', 1)], [('cl', 2), ('cl', 3)],
                          [('cl', 1), ('vln', 1)]])

        self.assertEqual(parse_inst_list('cl, woodwinds(ens), perc'),
                         [[('cl', 1)], [('woodwinds', 'ensemble')],
                          [('perc', 1)]])


    def test_get_inst_dict(self):
        self.assertEqual(get_inst_dict('foo'), 'foo')
        self.assertEqual(get_inst_dict('any'), 'any instrument')

    def test_get_name_with_count(self):
        self.assertEqual(get_name_with_count('oboe', 1), '1 oboe')

        self.assertEqual(get_name_with_count('clarinet', 2), '2 clarinet')

        self.assertEqual(get_name_with_count('flute', 'ensemble'),
                         'flute [ensemble]')

    def test_get_idf(self):
        self.assertEqual(get_idf('oboe', 1, '1 oboe'),
                         'oboe001::1 oboe')

        self.assertEqual(get_idf('clarinet', 2, '2 clarinet'),
                         'clarinet002::2 clarinet')

        self.assertEqual(get_idf('flute', 'ensemble', 'flute [ensemble]'),
                         'fluteensemble::flute [ensemble]')


    def test_get_instrument_fields(self):
        id, idf, idfwa = get_instrument_fields('ob, cl, bsn')

        self.assertEqual(id, ["oboe", "clarinet", "bassoon"])

        self.assertEqual(idf, ["oboe001::1 oboe",
                               "clarinet001::1 clarinet",
                               "bassoon001::1 bassoon"])

        self.assertEqual(idfwa, ["1 oboe", "1 clarinet", "1 bassoon"])

        # 00002292
        id, idf, idfwa = get_instrument_fields('cl, cl(2)')

        self.assertEqual(id, ['clarinet'])

        self.assertEqual(set(idf),
                         set(['clarinet001::1 clarinet',
                              'clarinet003::3 clarinet']))

        self.assertEqual(idfwa, ['1 clarinet', '2 clarinet'])

        # 00011023
        id, idf, idfwa = \
            get_instrument_fields('strings(2)|strings(3)|woodwinds(2)|woodwinds(3)')

        self.assertEqual(id, ['string instruments', 'woodwind instruments'])

        self.assertEqual(set(idf),
                         set(['string instruments002::2 string instruments',
                              'string instruments003::3 string instruments',
                              'woodwind instruments002::2 woodwind instruments',
                              'woodwind instruments003::3 woodwind instruments']))

        self.assertEqual(idfwa, ['2 string instruments OR 3 string instruments OR 2 woodwind instruments OR 3 woodwind instruments'])

        # 00001122
        id, idf, idfwa = get_instrument_fields('cl(3)|cl(2), hrn-bsst')

        self.assertEqual(id, ['hrn-bsst', 'clarinet'])

        self.assertEqual(set(idf),
                         set(['hrn-bsst001::1 hrn-bsst',
                              'clarinet003::3 clarinet',
                              'clarinet002::2 clarinet']))

        self.assertEqual(idfwa, ['1 hrn-bsst', '3 clarinet OR 2 clarinet'])

        # 00001202
        id, idf, idfwa = \
            get_instrument_fields('fl(3)|cl(3), ob(opt), cl|cl-alt, bsn|cl-bs, pno(opt)')

        self.assertEqual(id, ['oboe', 'piano', 'flute', 'clarinet',
                              'alto clarinet', 'bassoon', 'bass clarinet'])

        self.assertEqual(set(idf),
                         set(['oboeoptional::oboe [optional]',
                              'pianooptional::piano [optional]',
                              'flute003::3 flute',
                              'clarinet003::3 clarinet',
                              'clarinet001::1 clarinet',
                              'clarinet004::4 clarinet',
                              'alto clarinet001::1 alto clarinet',
                              'bassoon001::1 bassoon',
                              'bass clarinet001::1 bass clarinet']))

        self.assertEqual(idfwa, ['oboe [optional]',
                                 'piano [optional]',
                                 '3 flute OR 3 clarinet',
                                 '1 clarinet OR 1 alto clarinet',
                                 '1 bassoon OR 1 bass clarinet'])

        # 00004248
        id, idf, idfwa = get_instrument_fields('cl|cl(2)|cl(3)')

        self.assertEqual(id, ['clarinet'])

        self.assertEqual(set(idf),
                         set(['clarinet001::1 clarinet',
                              'clarinet002::2 clarinet',
                              'clarinet003::3 clarinet']))

        self.assertEqual(idfwa, ['1 clarinet OR 2 clarinet OR 3 clarinet'])


        # 00000056
        id, idf, idfwa = get_instrument_fields('fl(2), cl|fl, ob, cl')

        self.assertEqual(id, ['flute', 'oboe', 'clarinet'])

        self.assertEqual(set(idf),
                         set(['flute002::2 flute',
                              'flute003::3 flute',
                              'oboe001::1 oboe',
                              'clarinet001::1 clarinet',
                              'clarinet002::2 clarinet']))

        self.assertEqual(idfwa, ['2 flute',
                                 '1 oboe',
                                 '1 clarinet',
                                 '1 clarinet OR 1 flute'])

        # 00003573
        id, idf, idfwa = get_instrument_fields('cl, cl(2), cl(3)')

        self.assertEqual(id, ['clarinet'])

        self.assertEqual(set(idf),
                         set(['clarinet001::1 clarinet',
                              'clarinet003::3 clarinet',
                              'clarinet004::4 clarinet',
                              'clarinet006::6 clarinet']))

        self.assertEqual(idfwa, ['1 clarinet', '2 clarinet', '3 clarinet'])

        # 00002012
        id, idf, idfwa = \
            get_instrument_fields('ob|fl, fl(2)|cl(2), cl, bsn|cl, perc, cl(2)')

        self.assertEqual(id, ['clarinet',
                              'percussion',
                              'oboe',
                              'flute',
                              'bassoon'])

        self.assertEqual(set(idf),
                         set(['clarinet001::1 clarinet',
                              'clarinet003::3 clarinet',
                              'clarinet005::5 clarinet',
                              'clarinet002::2 clarinet',
                              'clarinet004::4 clarinet',
                              'clarinet006::6 clarinet',
                              'percussion001::1 percussion',
                              'oboe001::1 oboe',
                              'flute001::1 flute',
                              'flute002::2 flute',
                              'flute003::3 flute',
                              'bassoon001::1 bassoon']))

        self.assertEqual(idfwa, ['1 clarinet',
                                 '1 percussion',
                                 '2 clarinet',
                                 '1 oboe OR 1 flute',
                                 '2 flute OR 2 clarinet',
                                 '1 bassoon OR 1 clarinet'])

        # 00004647
        id, idf, idfwa = get_instrument_fields('cl-c|cl-eb, bongos(3)|pno')

        self.assertEqual(id, ['c clarinet', 'e-flat clarinet',
                              'bongos', 'piano'])

        self.assertEqual(set(idf),
                         set(['c clarinet001::1 c clarinet',
                              'e-flat clarinet001::1 e-flat clarinet',
                              'bongos003::3 bongos',
                              'piano001::1 piano']))

        self.assertEqual(idfwa, ['1 c clarinet OR 1 e-flat clarinet',
                                 '3 bongos OR 1 piano'])

        # Template for additional tests
        #
        # id, idf, idfwa = get_instrument_fields('')

        # self.assertEqual(id, )

        # self.assertEqual(set(idf),
        #                  set())

        # self.assertEqual(idfwa, )


if __name__ == '__main__':
    # Run the tests
    suite = TestLoader().loadTestsFromTestCase(Test)
    result = TextTestRunner().run(suite)
    if result.errors or result.failures:
        sys.exit(1)

    # Run the CSV validation and cleanup
    cleanup()