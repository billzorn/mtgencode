#!/usr/bin/env python
import sys
import os
import re
import json

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
import utils
import jdecode
import cardlib
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

def check_characters(fname, vname):
    cards = jdecode.mtg_open_file(fname, verbose=True, linetrans=True)

    tokens = {c for c in utils.cardsep}
    for card in cards:
        for c in card.encode():
            tokens.add(c)

    token_to_idx = {tok:i+1 for i, tok in enumerate(sorted(tokens))}
    idx_to_token = {i+1:tok for i, tok in enumerate(sorted(tokens))}

    print('Vocabulary: ({:d} symbols)'.format(len(token_to_idx)))
    for token in sorted(token_to_idx):
        print('{:8s} : {:4d}'.format(repr(token), token_to_idx[token]))

    # compliant with torch-rnn
    if vname:
        json_data = {'token_to_idx':token_to_idx, 'idx_to_token':idx_to_token}
        print('writing vocabulary to {:s}'.format(vname))
        with open(vname, 'w') as f:
            json.dump(json_data, f)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', nargs='?', default=os.path.join(libdir, '../data/output.txt'),
                        help='encoded card file or json corpus to process')
    parser.add_argument('-lines', action='store_true',
                        help='show behavior of line separation')
    parser.add_argument('-vocab', action='store_true',
                        help='show vocabulary counts from encoded card text')
    parser.add_argument('-chars', action='store_true',
                        help='generate and display vocabulary of characters used in encoding')
    parser.add_argument('--vocab_name', default=None,
                        help='json file to write vocabulary to')
    args = parser.parse_args()

    if args.lines:
        check_lines(args.infile)
    if args.vocab:
        check_vocab(args.infile)
    if args.chars:
        check_characters(args.infile, args.vocab_name)

    exit(0)
