#!/usr/bin/env python
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
sys.path.append(libdir)
import re
import random
import utils
import jdecode
import cardlib

def exclude_sets(cardset):
    return cardset == 'Unglued' or cardset == 'Unhinged' or cardset == 'Celebration'

def exclude_types(cardtype):
    return cardtype in ['conspiracy']

def exclude_layouts(layout):
    return layout in ['token', 'plane', 'scheme', 'phenomenon', 'vanguard']

def main(fname, oname = None, verbose = True, encoding = 'std', 
         nolinetrans = False, randomize = False, nolabel = False, stable = False):
    fmt_ordered = cardlib.fmt_ordered_default
    fmt_labeled = None if nolabel else cardlib.fmt_labeled_default
    fieldsep = utils.fieldsep
    line_transformations = not nolinetrans
    randomize_fields = False
    randomize_mana = randomize
    initial_sep = True
    final_sep = True

    # set the properties of the encoding

    if encoding in ['std']:
        pass
    elif encoding in ['named']:
        fmt_ordered = cardlib.fmt_ordered_named
    elif encoding in ['noname']:
        fmt_ordered = cardlib.fmt_ordered_noname
    elif encoding in ['rfields']:
        randomize_fields = True
        final_sep = False
    elif encoding in ['old']:
        fmt_ordered = cardlib.fmt_ordered_old
    elif encoding in ['norarity']:
        fmt_ordered = cardlib.fmt_ordered_norarity
    elif encoding in ['vec']:
        pass
    elif encoding in ['custom']:
        ## put custom format decisions here ##########################
        
        ## end of custom format ######################################
        pass
    else:
        raise ValueError('encode.py: unknown encoding: ' + encoding)

    if verbose:
        print 'Preparing to encode:'
        print '  Using encoding ' + repr(encoding)
        if stable:
            print '  NOT randomizing order of cards.'
        if randomize_mana:
            print '  Randomizing order of symobls in manacosts.'
        if not fmt_labeled:
            print '  NOT labeling fields for this run (may be harder to decode).'
        if not line_transformations:
            print '  NOT using line reordering transformations'

    cards = []
    valid = 0
    skipped = 0
    invalid = 0
    unparsed = 0

    if fname[-5:] == '.json':
        if verbose:
            print 'This looks like a json file: ' + fname
        json_srcs = jdecode.mtg_open_json(fname, verbose)
        # don't worry we randomize later
        for json_cardname in sorted(json_srcs):
            if len(json_srcs[json_cardname]) > 0:
                jcards = json_srcs[json_cardname]

                # look for a normal rarity version, in a set we can use
                idx = 0
                card = cardlib.Card(jcards[idx], linetrans = line_transformations)
                while (idx < len(jcards)
                       and (card.rarity == utils.rarity_special_marker 
                            or exclude_sets(jcards[idx][utils.json_field_set_name]))):
                    idx += 1
                    if idx < len(jcards):
                        card = cardlib.Card(jcards[idx], linetrans = line_transformations)
                # if there isn't one, settle with index 0
                if idx >= len(jcards):
                    idx = 0
                    card = cardlib.Card(jcards[idx], linetrans = line_transformations)
                # we could go back and look for a card satisfying one of the criteria,
                # but eh

                skip = False
                if (exclude_sets(jcards[idx][utils.json_field_set_name])
                    or exclude_layouts(jcards[idx]['layout'])):
                    skip = True                    
                for cardtype in card.types:
                    if exclude_types(cardtype):
                        skip = True
                if skip:
                    skipped += 1
                    continue
                
                if card.valid:
                    valid += 1
                    cards += [card]
                elif card.parsed:
                    invalid += 1
                else:
                    unparsed += 1

    # fall back to opening a normal encoded file
    else:
        if verbose:
            print 'Opening encoded card file: ' + fname
        with open(fname, 'rt') as f:
            text = f.read()
        for card_src in text.split(utils.cardsep):
            if card_src:
                card = cardlib.Card(card_src)
                if card.valid:
                    valid += 1
                    cards += [card]
                elif card.parsed:
                    invalid += 1
                else:
                    unparsed += 1

    if verbose:
        print (str(valid) + ' valid, ' + str(skipped) + ' skipped, ' 
               + str(invalid) + ' invalid, ' + str(unparsed) + ' failed to parse.')

    # This should give a random but consistent ordering, to make comparing changes
    # between the output of different versions easier.
    if not stable:
        random.seed(1371367)
        random.shuffle(cards)

    def writecards(writer):
        for card in cards:
            if encoding in ['vec']:
                writer.write(card.vectorize() + '\n\n')
            else:
                writer.write(card.encode(fmt_ordered = fmt_ordered,
                                         fmt_labeled = fmt_labeled,
                                         fieldsep = fieldsep,
                                         randomize_fields = randomize_fields,
                                         randomize_mana = randomize_mana,
                                         initial_sep = initial_sep,
                                         final_sep = final_sep) 
                             + utils.cardsep)

    if oname:
        if verbose:
            print 'Writing output to: ' + oname
        with open(oname, 'w') as ofile:
            writecards(ofile)
    else:
        writecards(sys.stdout)
        sys.stdout.flush()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', 
                        help='encoded card file or json corpus to encode')
    parser.add_argument('outfile', nargs='?', default=None,
                        help='output file, defaults to stdout')
    parser.add_argument('-e', '--encoding', default='std', choices=utils.formats,
                        #help='{' + ','.join(formats) + '}',
                        help='encoding format to use',
    )
    parser.add_argument('-r', '--randomize', action='store_true',
                        help='randomize the order of symbols in mana costs')
    parser.add_argument('--nolinetrans', action='store_true',
                        help="don't reorder lines of card text")
    parser.add_argument('--nolabel', action='store_true',
                        help="don't label fields")
    parser.add_argument('-s', '--stable', action='store_true',
                        help="don't randomize the order of the cards")
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    
    args = parser.parse_args()
    main(args.infile, args.outfile, verbose = args.verbose, encoding = args.encoding, 
         nolinetrans = args.nolinetrans, randomize = args.randomize, nolabel = args.nolabel, 
         stable = args.stable)
    exit(0)
