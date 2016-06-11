#!/usr/bin/env python
import sys
import os
import pickle

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
import jdecode
import nltk_model as model

def update_ngrams(lines, gramdict, grams):
    for line in lines:
        for i in range(0, len(line) - (grams - 1)):
            ngram = ' '.join([line[i + j] for j in range(0, grams)])
            if ngram in gramdict:
                gramdict[ngram] += 1
            else:
                gramdict[ngram] = 1

def describe_bins(gramdict, bins):
    bins = sorted(bins)
    counts = [0 for _ in range(0, len(bins) + 1)]

    for ngram in gramdict:
        for i in range(0, len(bins) + 1):
            if i < len(bins):
                if gramdict[ngram] <= bins[i]:
                    counts[i] += 1
                    break
            else:
                # didn't fit into any of the smaller bins, stick in on the end
                counts[-1] += 1
    
    for i in range(0, len(counts)):
        if counts[i] > 0:
            print ('  ' + (str(bins[i]) if i < len(bins) else str(bins[-1]) + '+') 
                   + ': ' + str(counts[i]))

def extract_language(cards, separate_lines = True):
    if separate_lines:
        lang = [line.vectorize() for card in cards for line in card.text_lines]
    else:
        lang = [card.text.vectorize() for card in cards]
    return map(lambda s: s.split(), lang)

def build_ngram_model(cards, n, separate_lines = True, verbose = False):
    if verbose:
        print('generating ' + str(n) + '-gram model')
    lang = extract_language(cards, separate_lines=separate_lines)
    if verbose:
        print('found ' + str(len(lang)) + ' sentences')
    lm = model.NgramModel(n, lang, pad_left=True, pad_right=True)
    if verbose:
        print(lm)
    return lm

def main(fname, oname, gmin = 2, gmax = 8, nltk = False, sep = False, verbose = False):
    # may need to set special arguments here
    cards = jdecode.mtg_open_file(fname, verbose=verbose)
    gmin = int(gmin)
    gmax = int(gmax)

    if nltk:
        n = gmin
        lm = build_ngram_model(cards, n, separate_lines=sep, verbose=verbose)
        if verbose:
            teststr = 'when @ enters the battlefield'
            print('litmus test: perplexity of ' + repr(teststr))
            print('  ' + str(lm.perplexity(teststr.split())))
        if verbose:
            print('pickling module to ' + oname)
        with open(oname, 'wb') as f:
            pickle.dump(lm, f)

    else:
        bins = [1, 2, 3, 10, 30, 100, 300, 1000]
        if gmin < 2 or gmax < gmin:
            print 'invalid gram sizes: ' + str(gmin) + '-' + str(gmax)
            exit(1)

        for grams in range(gmin, gmax+1):
            if verbose:
                print 'generating ' + str(grams) + '-grams...'
            gramdict = {}
            for card in cards:
                update_ngrams(card.text_lines_words, gramdict, grams)

            oname_full = oname + '.' + str(grams) + 'g'
            if verbose:
                print('  writing ' + str(len(gramdict)) + ' unique ' + str(grams) 
                      + '-grams to ' + oname_full)
                describe_bins(gramdict, bins)

            with open(oname_full, 'wt') as f:
                for ngram in sorted(gramdict,
                                    lambda x,y: cmp(gramdict[x], gramdict[y]),
                                    reverse = True):
                    f.write((ngram + ': ' + str(gramdict[ngram]) + '\n').encode('utf-8'))

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to process')
    parser.add_argument('outfile', #nargs='?', default=None,
                        help='base name of output file, outputs ending in .2g, .3g etc. will be produced')
    parser.add_argument('-min', '--min', action='store', default='2',
                        help='minimum gram size to compute')
    parser.add_argument('-max', '--max', action='store', default='8',
                        help='maximum gram size to compute')
    parser.add_argument('-nltk', '--nltk', action='store_true',
                        help='use nltk model.NgramModel, with n = min')
    parser.add_argument('-s', '--separate', action='store_true',
                        help='separate card text into lines when constructing nltk model')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    main(args.infile, args.outfile, gmin=args.min, gmax=args.max, nltk=args.nltk,
         sep=args.separate, verbose=args.verbose)
    exit(0)
