#!/usr/bin/env python
import sys
import os
import re

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
import utils
import jdecode
import transforms

def check_lines(fname):
    cards = jdecode.mtg_open_file(fname, verbose=True, linetrans=True)

    prelines = set()
    keylines = set()
    mainlines = set()
    costlines = set()
    postlines = set()

    known = ['enchant ', 'equip', 'countertype', 'multikicker', 'kicker',
             'suspend', 'echo', 'awaken', 'bestow', 'buyback',
             'cumulative', 'dash', 'entwine', 'evoke', 'fortify',
             'flashback', 'madness', 'morph', 'megamorph', 'miracle', 'ninjutsu',
             'overload', 'prowl', 'recover', 'reinforce', 'replicate', 'scavenge',
             'splice', 'surge', 'unearth', 'transfigure', 'transmute',
    ]
    known = []

    for card in cards:
        prel, keyl, mainl, costl, postl = transforms.separate_lines(card.text.encode(randomize=False))
        if card.bside:
            prel2, keyl2, mainl2, costl2, postl2 = transforms.separate_lines(card.bside.text.encode(randomize=False))
            prel += prel2
            keyl += keyl2
            mainl += mainl2
            costl += costl2
            postl += postl2

        for line in prel:
            if line.strip() == '':
                print(card.name, card.text.text)
            if any(line.startswith(s) for s in known):
                line = 'known'
            prelines.add(line)
        for line in postl:
            if line.strip() == '':
                print(card.name, card.text.text)
            if any(line.startswith(s) for s in known):
                line = 'known'
            postlines.add(line)
        for line in keyl:
            if line.strip() == '':
                print(card.name, card.text.text)
            if any(line.startswith(s) for s in known):
                line = 'known'
            keylines.add(line)
        for line in mainl:
            if line.strip() == '':
                print(card.name, card.text.text)
            # if any(line.startswith(s) for s in known):
            #     line = 'known'
            mainlines.add(line)
        for line in costl:
            if line.strip() == '':
                print(card.name, card.text.text)
            # if any(line.startswith(s) for s in known) or 'cycling' in line or 'monstrosity' in line:
            #     line = 'known'
            costlines.add(line)

    print('prel: {:d}, keyl: {:d}, mainl: {:d}, postl {:d}'
          .format(len(prelines), len(keylines), len(mainlines), len(postlines)))

    print('\nprelines')
    for line in sorted(prelines):
        print(line)

    print('\npostlines')
    for line in sorted(postlines):
        print(line)

    print('\ncostlines')
    for line in sorted(costlines):
        print(line)

    print('\nkeylines')
    for line in sorted(keylines):
        print(line)

    print('\nmainlines')
    for line in sorted(mainlines):
        #if any(s in line for s in ['champion', 'devour', 'tribute']):
        print(line)

def check_vocab(fname):
    cards = jdecode.mtg_open_file(fname, verbose=True, linetrans=True)

    vocab = {}
    for card in cards:
        words = card.text.vectorize().split()
        if card.bside:
            words += card.bside.text.vectorize().split()
        for word in words:
            if not word in vocab:
                vocab[word] = 1
            else:
                vocab[word] += 1

    for word in sorted(vocab, lambda x,y: cmp(vocab[x], vocab[y]), reverse = True):
        print('{:8d} : {:s}'.format(vocab[word], word))

    n = 3

    for card in cards:
        words = card.text.vectorize().split()
        if card.bside:
            words += card.bside.text.vectorize().split()
        for word in words:
            if vocab[word] <= n:
            #if 'name' in word:
                print('\n{:8d} : {:s}'.format(vocab[word], word))
                print(card.encode())
                break

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', nargs='?', default=os.path.join(libdir, '../data/output.txt'),
                        help='encoded card file or json corpus to process')
    parser.add_argument('-lines', action='store_true',
                        help='show behavior of line separation')
    parser.add_argument('-vocab', action='store_true',
                        help='show vocabulary counts from encoded card text')
    args = parser.parse_args()

    if args.lines:
        check_lines(args.infile)
    if args.vocab:
        check_vocab(args.infile)

    exit(0)
