#!/usr/bin/env python
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
sys.path.append(libdir)
import utils
import jdecode
import cardlib

def main(fname, oname = None, verbose = True, gatherer = False, for_forum = False):
    cards = []
    valid = 0
    invalid = 0
    unparsed = 0

    if fname[-5:] == '.json':
        if verbose:
            print 'This looks like a json file: ' + fname
        json_srcs = jdecode.mtg_open_json(fname, verbose)
        for json_cardname in sorted(json_srcs):
            if len(json_srcs[json_cardname]) > 0:
                jcards = json_srcs[json_cardname]
                card = cardlib.Card(json_srcs[json_cardname][0])
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
        print (str(valid) + ' valid, ' + str(invalid) + ' invalid, ' 
               + str(unparsed) + ' failed to parse.')

    if oname:
        if verbose:
            print 'Writing output to: ' + oname
        with open(oname, 'w') as ofile:
            for card in cards:
                ofile.write((card.format(gatherer = gatherer, for_forum = for_forum) 
                            + '\n').encode('utf-8'))
    else:
        for card in cards:
            sys.stdout.write((card.format(gatherer = gatherer, for_forum = for_forum) 
                              + '\n').encode('utf-8'))
        sys.stdout.flush()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to encode')
    parser.add_argument('outfile', nargs='?', default=None,
                        help='output file, defaults to stdout')
    parser.add_argument('-g', '--gatherer', action='store_true',
                        help='emulate Gatherer visual spoiler')
    parser.add_argument('-f', '--forum', action='store_true',
                        help='use pretty mana encoding for mtgsalvation forum')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    
    args = parser.parse_args()
    main(args.infile, args.outfile, verbose = args.verbose, 
         gatherer = args.gatherer, for_forum = args.forum)
    exit(0)
