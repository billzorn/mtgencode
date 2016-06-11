#!/usr/bin/env python
import sys
import os
import random
import zipfile
import shutil

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data')
import utils
import jdecode
import ngrams
import analysis
import mtg_validate

from cbow import CBOW

separate_lines=True

def select_card(cards, stats, i):
    card = cards[i]
    nearest = stats['dists']['cbow'][i]
    perp = stats['ngram']['perp'][i]
    perp_per = stats['ngram']['perp_per'][i]
    perp_max = stats['ngram']['perp_max'][i]

    if nearest > 0.9 or perp_per > 2.0 or perp_max > 10.0:
        return None
        
    ((_, total_good, _, _), _) = mtg_validate.process_props([card])
    if not total_good == 1:
        return False

    # print '===='
    # print nearest
    # print perp
    # print perp_per
    # print perp_max
    # print '----'
    # print card.format()

    return True

def compare_to_real(card, realcard):
    ctypes = ' '.join(sorted(card.types))
    rtypes = ' '.join(sorted(realcard.types))
    return ctypes == rtypes and realcard.cost.check_colors(card.cost.get_colors())

def writecard(card, name, writer):
    gatherer = False
    for_forum = True
    vdump = True
    fmt = card.format(gatherer = gatherer, for_forum = for_forum, vdump = vdump)
    oldname = card.name
    # alter name used in image
    card.name = name
    writer.write(card.to_mse().encode('utf-8'))
    card.name = oldname
    fstring = ''
    if card.json:
        fstring += 'JSON:\n' + card.json + '\n'
    if card.raw: 
        fstring += 'raw:\n' + card.raw + '\n'
    fstring += '\n'
    fstring +=  fmt + '\n'
    fstring = fstring.replace('<', '(').replace('>', ')')
    writer.write(('\n' + fstring[:-1]).replace('\n', '\n\t\t').encode('utf-8'))
    writer.write('\n'.encode('utf-8'))

def main(fname, oname, n=20, verbose=False):
    cbow = CBOW()
    realcards = jdecode.mtg_open_file(str(os.path.join(datadir, 'output.txt')), verbose=verbose)
    real_by_name = {c.name: c for c in realcards}
    lm = ngrams.build_ngram_model(realcards, 3, separate_lines=separate_lines, verbose=verbose)
    cards = jdecode.mtg_open_file(fname, verbose=verbose)
    stats = analysis.get_statistics(fname, lm=lm, sep=separate_lines, verbose=verbose)

    selected = []
    for i in range(0, len(cards)):
        if select_card(cards, stats, i):
            selected += [(i, cards[i])]

    limit = 3000

    random.shuffle(selected)
    #selected = selected[:limit]

    if verbose:
        print('computing nearest cards for ' + str(len(selected)) + ' candindates...')
    cbow_nearest = cbow.nearest_par(map(lambda (i, c): c, selected))
    for i in range(0, len(selected)):
        (j, card) = selected[i]
        selected[i] = (j, card, cbow_nearest[i])
    if verbose:
        print('...done')

    final = []
    for (i, card, nearest) in selected:
        for dist, rname in nearest:
            realcard = real_by_name[rname]
            if compare_to_real(card, realcard):
                final += [(i, card, realcard, dist)]
                break

    for (i, card, realcard, dist) in final:
        print '-- real --'
        print realcard.format()
        print '-- fake --'
        print card.format()
        print '-- stats --'
        perp_per = stats['ngram']['perp_per'][i]
        perp_max = stats['ngram']['perp_max'][i]
        print dist
        print perp_per
        print perp_max
        print '----'

    if not oname is None:
        with open(oname, 'wt') as ofile:
            ofile.write(utils.mse_prepend)
            for (i, card, realcard, dist) in final:
                name = realcard.name
                writecard(realcard, name, ofile)
                writecard(card, name, ofile)
            ofile.write('version control:\n\ttype: none\napprentice code: ')
            # Copy whatever output file is produced, name the copy 'set' (yes, no extension).
            if os.path.isfile('set'):
                print 'ERROR: tried to overwrite existing file "set" - aborting.'
                return
            shutil.copyfile(oname, 'set')
            # Use the freaky mse extension instead of zip.
            with zipfile.ZipFile(oname+'.mse-set', mode='w') as zf:
                try:
                    # Zip up the set file into oname.mse-set.
                    zf.write('set') 
                finally:
                    if verbose:
                        print 'Made an MSE set file called ' + oname + '.mse-set.'
                    # The set file is useless outside the .mse-set, delete it.
                    os.remove('set')

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to process')
    parser.add_argument('outfile', nargs='?', default=None,
                        help='output file, defaults to none')
    parser.add_argument('-n', '--n', action='store',
                        help='number of cards to consider for each pairing')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    main(args.infile, args.outfile, n=args.n, verbose=args.verbose)
    exit(0)
