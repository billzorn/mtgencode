#!/usr/bin/env python
import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)

def main(fname):
    with open(fname, 'rt') as f:
        text = f.read()
    
    cardstats = text.split('\n')
    nonempty = 0
    name_avg = 0
    name_dupes = 0
    card_avg = 0
    card_dupes = 0

    for c in cardstats:
        fields = c.split('|')
        if len(fields) < 4:
            continue
        nonempty += 1
        idx = int(fields[0])
        name = str(fields[1])
        ndist = float(fields[2])
        cdist = float(fields[3])

        name_avg += ndist
        if ndist == 1.0:
            name_dupes += 1
        card_avg += cdist
        if cdist == 1.0:
            card_dupes += 1

    name_avg = name_avg / float(nonempty)
    card_avg = card_avg / float(nonempty)
    
    print str(nonempty) + ' cards'
    print '-- names --'
    print 'avg distance:   ' + str(name_avg)
    print 'num duplicates: ' + str(name_dupes)
    print '-- cards --'
    print 'avg distance:   ' + str(card_avg)
    print 'num duplicates: ' + str(card_dupes)
    print '----'

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='data file to process')

    args = parser.parse_args()
    main(args.infile)
    exit(0)
