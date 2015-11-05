#!/usr/bin/env python
import sys
import os
import zipfile
import shutil

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
sys.path.append(libdir)
import utils
import jdecode
import cardlib
from cbow import CBOW
from namediff import Namediff

def exclude_sets(cardset):
    return cardset == 'Unglued' or cardset == 'Unhinged' or cardset == 'Celebration'

def main(fname, oname = None, verbose = True, 
         gatherer = False, for_forum = False, for_mse = False,
         creativity = False, norarity = False, vdump = False, for_html = False):
    cards = []
    valid = 0
    invalid = 0
    unparsed = 0

    if norarity:
        decode_fields = [
            cardlib.field_name,
            cardlib.field_supertypes,
            cardlib.field_types,
            cardlib.field_loyalty,
            cardlib.field_subtypes,
            #cardlib.field_rarity,
            cardlib.field_pt,
            cardlib.field_cost,
            cardlib.field_text,
        ]
    else:
        decode_fields = cardlib.fmt_ordered_default

    if fname[-5:] == '.json':
        if verbose:
            print 'This looks like a json file: ' + fname
        json_srcs = jdecode.mtg_open_json(fname, verbose)
        for json_cardname in sorted(json_srcs):
            if len(json_srcs[json_cardname]) > 0:
                jcards = json_srcs[json_cardname]

                # look for a normal rarity version, in a set we can use
                idx = 0
                card = cardlib.Card(jcards[idx], fmt_ordered = decode_fields)
                while (idx < len(jcards)
                       and (card.rarity == utils.rarity_special_marker 
                            or exclude_sets(jcards[idx][utils.json_field_set_name]))):
                    idx += 1
                    if idx < len(jcards):
                        card = cardlib.Card(jcards[idx], fmt_ordered = decode_fields)
                # if there isn't one, settle with index 0
                if idx >= len(jcards):
                    idx = 0
                    card = cardlib.Card(jcards[idx], fmt_ordered = decode_fields)
                # we could go back and look for a card satisfying one of the criteria,
                # but eh

                if card.valid:
                    valid += 1
                elif card.parsed:
                    invalid += 1
                else:
                    unparsed += 1
                cards += [card]

    # fall back to opening a normal encoded file
    else:
        if verbose:
            print 'Opening encoded card file: ' + fname
        with open(fname, 'rt') as f:
            text = f.read()
        for card_src in text.split(utils.cardsep):
            if card_src:
                card = cardlib.Card(card_src, fmt_ordered = decode_fields)
                if card.valid:
                    valid += 1
                elif card.parsed:
                    invalid += 1
                else:
                    unparsed += 1
                cards += [card]

    if verbose:
        print (str(valid) + ' valid, ' + str(invalid) + ' invalid, ' 
               + str(unparsed) + ' failed to parse.')

    good_count = 0
    bad_count = 0
    for card in cards:
        if not card.parsed and not card.text.text:
            bad_count += 1
        else:
            good_count += 1
        if good_count + bad_count > 15: 
            break
    # random heuristic
    if bad_count > 10:
        print 'Saw a bunch of unparsed cards with no text:'
        print 'If this is a legacy format, try rerunning with --norarity'

    if creativity:
        cbow = CBOW()
        namediff = Namediff()

    def writecards(writer):
        if for_mse:
            # have to prepend a massive chunk of formatting info
            writer.write(utils.mse_prepend)
            
        if for_html:
            # have to preapend html info
            writer.write(utils.html_preapend)
            
        for card in cards:
            if for_mse:
                writer.write(card.to_mse().encode('utf-8'))
                fstring = ''
                if card.json:
                    fstring += 'JSON:\n' + card.json + '\n'
                if card.raw: 
                    fstring += 'raw:\n' + card.raw + '\n'
                fstring += '\n'
                fstring += card.format(gatherer = gatherer, for_forum = for_forum,
                                       vdump = vdump, for_html = for_html)
                fstring = fstring.replace('<', '(').replace('>', ')')
                writer.write(('\n' + fstring[:-1]).replace('\n', '\n\t\t'))
            else:
                writer.write(card.format(gatherer = gatherer, for_forum = for_forum,
                                         vdump = vdump, for_html = for_html).encode('utf-8'))

            if creativity:
                cstring = '~~ closest cards ~~\n'
                nearest = cbow.nearest(card)
                for dist, cardname in nearest:
                    cardname = namediff.names[cardname]
                    if for_forum:
                        cardname = '[card]' + cardname + '[/card]'
                    cstring += cardname + ': ' + str(dist) + '\n'
                cstring += '~~ closest names ~~\n'
                nearest = namediff.nearest(card.name)
                for dist, cardname in nearest:
                    cardname = namediff.names[cardname]
                    if for_forum:
                        cardname = '[card]' + cardname + '[/card]'
                    cstring += cardname + ': ' + str(dist) + '\n'
                if for_mse:
                    cstring = cstring.replace('<', '(').replace('>', ')')
                    cstring = ('\n\n' + cstring[:-1]).replace('\n', '\n\t\t')
                writer.write(cstring.encode('utf-8'))

            writer.write('\n'.encode('utf-8'))

        if for_mse:
            # more formatting info
            writer.write('version control:\n\ttype: none\napprentice code: ')
            
        if for_html:
            # closing the html file
            writer.write(utils.html_postapend)

    if oname:
        if verbose:
            print 'Writing output to: ' + oname
        with open(oname, 'w') as ofile:
            writecards(ofile)
        if for_mse:
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
#        if for_html:
                ## not sure what to put here
    else:
        writecards(sys.stdout)
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
    parser.add_argument('-c', '--creativity', action='store_true',
                        help='use CBOW fuzzy matching to check creativity of cards')
    parser.add_argument('-d', '--dump', action='store_true',
                        help='dump out lots of information about invalid cards')
    parser.add_argument('--norarity', action='store_true',
                        help='the card format has no rarity field; use for legacy input')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    parser.add_argument('-mse', '--mse', action='store_true',
                        help='use Magic Set Editor 2 encoding; will output as .mse-set file')
    parser.add_argument('-html', '--html', action='store_true', help='create a .html file with pretty forum formatting')
    
    args = parser.parse_args()
    main(args.infile, args.outfile, verbose = args.verbose, 
         gatherer = args.gatherer, for_forum = args.forum, for_mse = args.mse,
         creativity = args.creativity, norarity = args.norarity, vdump = args.dump, for_html = args.for_html)
    exit(0)
