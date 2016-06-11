#!/usr/bin/env python
import sys
import os
import re
from collections import OrderedDict

# scipy is kinda necessary
import scipy
import scipy.stats
import numpy as np
import math

def mean_nonan(l):
    filtered = [x for x in l if not math.isnan(x)]
    return  np.mean(filtered)

def gmean_nonzero(l):
    filtered = [x for x in l if x != 0 and not math.isnan(x)]
    return  scipy.stats.gmean(filtered)

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data')
import jdecode

import mtg_validate
import ngrams

def annotate_values(values):
    for k in values:
        (total, good, bad) = values[k]
        values[k] = OrderedDict([('total', total), ('good', good), ('bad', bad)])
    return values

def print_statistics(stats, ident = 0):
    for k in stats:
        if isinstance(stats[k], OrderedDict):
            print(' ' * ident + str(k) + ':')
            print_statistics(stats[k], ident=ident+2)
        elif isinstance(stats[k], dict):
            print(' ' * ident + str(k) + ': <dict with ' + str(len(stats[k])) + ' entries>')
        elif isinstance(stats[k], list):
            print(' ' * ident + str(k) + ': <list with ' + str(len(stats[k])) + ' entries>')
        else:
            print(' ' * ident + str(k) + ': ' + str(stats[k]))

def get_statistics(fname, lm = None, sep = False, verbose=False):
    stats = OrderedDict()
    cards = jdecode.mtg_open_file(fname, verbose=verbose)
    stats['cards'] = cards

    # unpack the name of the checkpoint - terrible and hacky
    try:
        final_name = os.path.basename(fname)
        halves = final_name.split('_epoch')
        cp_name = halves[0]
        cp_info = halves[1][:-4]
        info_halves = cp_info.split('_')
        cp_epoch = float(info_halves[0])
        fragments = info_halves[1].split('.')
        cp_vloss = float('.'.join(fragments[:2]))
        cp_temp = float('.'.join(fragments[-2:]))
        cp_ident = '.'.join(fragments[2:-2])
        stats['cp'] = OrderedDict([('name', cp_name),
                                   ('epoch', cp_epoch),
                                   ('vloss', cp_vloss),
                                   ('temp', cp_temp),
                                   ('ident', cp_ident)])
    except Exception as e:
        pass

    # validate
    ((total_all, total_good, total_bad, total_uncovered), 
         values) = mtg_validate.process_props(cards)
    
    stats['props'] = annotate_values(values)
    stats['props']['overall'] = OrderedDict([('total', total_all), 
                                             ('good', total_good), 
                                             ('bad', total_bad), 
                                             ('uncovered', total_uncovered)])

    # distances
    distfname = fname + '.dist'
    if os.path.isfile(distfname):
        name_dupes = 0
        card_dupes = 0
        with open(distfname, 'rt') as f:
            distlines = f.read().split('\n')
        dists = OrderedDict([('name', []), ('cbow', [])])
        for line in distlines:
            fields = line.split('|')
            if len(fields) < 4:
                continue
            idx = int(fields[0])
            name = str(fields[1])
            ndist = float(fields[2])
            cdist = float(fields[3])
            dists['name'] += [ndist]
            dists['cbow'] += [cdist]
            if ndist == 1.0:
                name_dupes += 1
            if cdist == 1.0:
                card_dupes += 1

        dists['name_mean'] = mean_nonan(dists['name'])
        dists['cbow_mean'] = mean_nonan(dists['cbow'])
        dists['name_geomean'] = gmean_nonzero(dists['name'])
        dists['cbow_geomean'] = gmean_nonzero(dists['cbow'])
        stats['dists'] = dists
        
    # n-grams
    if not lm is None:
        ngram = OrderedDict([('perp', []), ('perp_per', []), 
                             ('perp_max', []), ('perp_per_max', [])])
        for card in cards:
            if len(card.text.text) == 0:
                perp = 0.0
                perp_per = 0.0
            elif sep:
                vtexts = [line.vectorize().split() for line in card.text_lines 
                          if len(line.vectorize().split()) > 0]
                perps = [lm.perplexity(vtext) for vtext in vtexts]
                perps_per = [perps[i] / float(len(vtexts[i])) for i in range(0, len(vtexts))]
                perp = gmean_nonzero(perps)
                perp_per = gmean_nonzero(perps_per)
                perp_max = max(perps)
                perp_per_max = max(perps_per)
            else:
                vtext = card.text.vectorize().split()
                perp = lm.perplexity(vtext)
                perp_per = perp / float(len(vtext))
                perp_max = perp
                perp_per_max = perps_per

            ngram['perp'] += [perp]
            ngram['perp_per'] += [perp_per]
            ngram['perp_max'] += [perp_max]
            ngram['perp_per_max'] += [perp_per_max]

        ngram['perp_mean'] = mean_nonan(ngram['perp'])
        ngram['perp_per_mean'] = mean_nonan(ngram['perp_per'])
        ngram['perp_geomean'] = gmean_nonzero(ngram['perp'])
        ngram['perp_per_geomean'] = gmean_nonzero(ngram['perp_per'])
        stats['ngram'] = ngram

    return stats
    

def main(infile, verbose = False):
    lm = ngrams.build_ngram_model(jdecode.mtg_open_file(str(os.path.join(datadir, 'output.txt'))),
                            3, separate_lines=True, verbose=True)
    stats = get_statistics(infile, lm=lm, sep=True, verbose=verbose)
    print_statistics(stats)

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to process')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    main(args.infile, verbose=args.verbose)
    exit(0)
