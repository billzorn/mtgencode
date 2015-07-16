#!/usr/bin/env python
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
import utils
import jdecode
from datalib import Datamine

def main(fname, verbose = True, outliers = False, dump_all = False):
    if fname[-5:] == '.json':
        if verbose:
            print 'This looks like a json file: ' + fname
        json_srcs = jdecode.mtg_open_json(fname, verbose)
        card_srcs = []
        for json_cardname in sorted(json_srcs):
            if len(json_srcs[json_cardname]) > 0:
                card_srcs += [json_srcs[json_cardname][0]]
    else:
        if verbose:
            print 'Opening encoded card file: ' + fname
        with open(fname, 'rt') as f:
            text = f.read()
        card_srcs = text.split(utils.cardsep)

    mine = Datamine(card_srcs)
    mine.summarize()
    if outliers or dump_all:
        mine.outliers(dump_invalid = dump_all)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', 
                        help='encoded card file or json corpus to process')
    parser.add_argument('-x', '--outliers', action='store_true',
                        help='show additional diagnostics and edge cases')
    parser.add_argument('-a', '--all', action='store_true',
                        help='show all information and dump invalid cards')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    
    args = parser.parse_args()
    main(args.infile, verbose = args.verbose, outliers = args.outliers, dump_all = args.all)
    exit(0)
