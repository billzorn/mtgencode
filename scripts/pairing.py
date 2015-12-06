#!/usr/bin/env python
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data')
import jdecode
import ngrams
import analysis

separate_lines=True

def main(fname, n=20, verbose=False):
    realcards = jdecode.mtg_open_file(str(os.path.join(datadir, 'output.txt')), verbose=verbose)
    lm = ngrams.build_ngram_model(realcards, 3, separate_lines=separate_lines, verbose=verbose)
    cards = jdecode.mtg_open_file(fname, verbose=verbose)
    stats = analysis.get_statistics(fname, lm=lm, sep=separate_lines, verbose=verbose)

    print 'derp'

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to process')
    parser.add_argument('-n', '--n', action='store',
                        help='number of cards to consider for each pairing')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    main(args.infile, n=args.n, verbose=args.verbose)
    exit(0)
