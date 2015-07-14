import re
import random
import sys

import lib.utils as utils
from lib.cardlib import Card
import lib.jdecode as jdecode

valid_encoded_char = r'[abcdefghijklmnopqrstuvwxyz\'+\-*",.:;WUBRGPV/XTQ|\\&^\{\}@ \n=~%\[\]]'

def exclude_sets(cardset):
    return cardset == 'Unglued' or cardset == 'Unhinged' or cardset == 'Celebration'

def exclude_types(cardtype):
    return cardtype in ['conspiracy']

def exclude_layouts(layout):
    return layout in ['token', 'plane', 'scheme', 'phenomenon', 'vanguard']

def compile_duplicated(jcards):
    # Boring solution: only write out the first one...
    card = Card(jcards[0])
    if (exclude_sets(jcards[0][utils.json_field_set_name])
        or exclude_layouts(jcards[0]['layout'])):
        return None
    for cardtype in card.types:
        if exclude_types(cardtype):
            return None
    return card

def main(fname, oname = None, verbose = True):
    if verbose:
        print 'Opening json file: ' + fname

    jcards = jdecode.mtg_open_json(fname, verbose)
    cards = []

    valid = 0
    skipped = 0
    invalid = 0
    unparsed = 0

    for jcard_name in jcards:
        card = compile_duplicated(jcards[jcard_name])
        if card:
            if card.valid:
                valid += 1
                cards += [card]
            elif card.parsed:
                invalid += 1
            else:
                unparsed += 1
        else:
            skipped += 1

    if verbose:
        print (str(valid) + ' valid, ' + str(skipped) + ' skipped, ' 
               + str(invalid) + ' invalid, ' + str(unparsed) + ' failed to parse.')

    # This should give a random but consistent ordering, to make comparing changes
    # between the output of different versions easier.
    random.seed(1371367)
    random.shuffle(cards)

    if oname:
        if verbose:
            print 'Writing output to: ' + oname
        with open(oname, 'w') as ofile:
            for card in cards:
                ofile.write(card.encode() + utils.cardsep)
    else:
        for card in cards:
            sys.stdout.write(card.encode() + utils.cardsep)
        sts.stdout.flush()

    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<JSON file> [output filename]'
        exit(1)
