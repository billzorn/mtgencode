#!/usr/bin/env python
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
import utils
import jdecode
from namediff import Namediff
from cbow import CBOW

def main(fname, oname, verbose = True, parallel = True):
    # may need to set special arguments here
    cards = jdecode.mtg_open_file(fname, verbose=verbose)

    # this could reasonably be some separate function
    # might make sense to merge cbow and namediff and have this be the main interface
    namediff = Namediff()
    cbow = CBOW()

    if verbose:
        print 'Computing nearest names...'
    if parallel:
        nearest_names = namediff.nearest_par(map(lambda c: c.name, cards), n=1)
    else:
        nearest_names = [namediff.nearest(c.name, n=1) for c in cards]

    if verbose:
        print 'Computing nearest cards...'
    if parallel:
        nearest_cards = cbow.nearest_par(cards, n=1)
    else:
        nearest_cards = [cbow.nearest(c, n=1) for c in cards]

    for i in range(0, len(cards)):
        cards[i].nearest_names = nearest_names[i]
        cards[i].nearest_cards = nearest_cards[i]

    # # unfortunately this takes ~30 hours on 8 cores for a 10MB dump
    # if verbose:
    #     print 'Computing nearest encodings by text edit distance...'
    # if parallel:
    #     nearest_cards_text = namediff.nearest_card_par(cards, n=1)
    # else:
    #     nearest_cards_text = [namediff.nearest_card(c, n=1) for c in cards]

    if verbose:
        print '...Done.'

    # write to a file to store the data, this is a terribly long computation
    # we could also just store this same info in the cards themselves as more fields...
    sep = '|'
    with open(oname, 'w') as ofile:
        for i in range(0, len(cards)):
            card = cards[i]
            ostr = str(i) + sep + card.name + sep
            ndist, _ = card.nearest_names[0]
            ostr += str(ndist) + sep
            cdist, _ = card.nearest_cards[0]
            ostr += str(cdist) + '\n'
            # tdist, _ = nearest_cards_text[i][0]
            # ostr += str(tdist) + '\n'
            ofile.write(ostr.encode('utf-8'))

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to process')
    parser.add_argument('outfile', #nargs='?', default=None,
                        help='name of output file, will be overwritten')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    parser.add_argument('-p', '--parallel', action='store_true', 
                        help='run in parallel on all cores')

    args = parser.parse_args()
    main(args.infile, args.outfile, verbose=args.verbose, parallel=args.parallel)
    exit(0)
