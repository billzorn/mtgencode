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

def main(fname, oname = None, verbose = True, encoding = 'std',
         gatherer = False, for_forum = False, for_mse = False,
         creativity = False, vdump = False, for_html = False):

    fmt_ordered = cardlib.fmt_ordered_default

    if encoding in ['std']:
        pass
    elif encoding in ['named']:
        fmt_ordered = cardlib.fmt_ordered_named
    elif encoding in ['noname']:
        fmt_ordered = cardlib.fmt_ordered_noname
    elif encoding in ['rfields']:
        pass
    elif encoding in ['old']:
        fmt_ordered = cardlib.fmt_ordered_old
    elif encoding in ['norarity']:
        fmt_ordered = cardlib.fmt_ordered_norarity
    elif encoding in ['vec']:
        pass
    elif encoding in ['custom']:
        ## put custom format decisions here ##########################
        
        ## end of custom format ######################################
        pass
    else:
        raise ValueError('encode.py: unknown encoding: ' + encoding)

    cards = jdecode.mtg_open_file(fname, verbose=verbose, fmt_ordered=fmt_ordered)

    if creativity:
        cbow = CBOW()
        namediff = Namediff()

    def writecards(writer):
        if for_mse:
            # have to prepend a massive chunk of formatting info
            writer.write(utils.mse_prepend)

        if for_html:
            # have to preapend html info
            writer.write(utils.html_prepend)

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
                                       vdump = vdump)
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
            writer.write(utils.html_append)

    if oname:
        if for_html:
            print oname
            # if ('.html' != oname[-])
            #     oname += '.html'
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
    parser.add_argument('-e', '--encoding', default='std', choices=utils.formats,
                        #help='{' + ','.join(formats) + '}',
                        help='encoding format to use',
    )
    parser.add_argument('-g', '--gatherer', action='store_true',
                        help='emulate Gatherer visual spoiler')
    parser.add_argument('-f', '--forum', action='store_true',
                        help='use pretty mana encoding for mtgsalvation forum')
    parser.add_argument('-c', '--creativity', action='store_true',
                        help='use CBOW fuzzy matching to check creativity of cards')
    parser.add_argument('-d', '--dump', action='store_true',
                        help='dump out lots of information about invalid cards')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    parser.add_argument('-mse', '--mse', action='store_true', 
                        help='use Magic Set Editor 2 encoding; will output as .mse-set file')
    parser.add_argument('-html', '--html', action='store_true', help='create a .html file with pretty forum formatting')
    args = parser.parse_args()
    main(args.infile, args.outfile, verbose = args.verbose, encoding = args.encoding,
         gatherer = args.gatherer, for_forum = args.forum, for_mse = args.mse,
         creativity = args.creativity, vdump = args.dump, for_html = args.html)
    exit(0)
