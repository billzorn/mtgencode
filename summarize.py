import sys

import lib.utils as utils
import lib.jdecode as jdecode
from lib.datalib import Datamine

def main(fname, verbose = True):
    if fname[-5:] == '.json':
        if verbose:
            print 'This looks like a json file: ' + fname
        json_srcs = jdecode.mtg_open_json(fname, verbose)
        card_srcs = []
        for json_cardname in json_srcs:
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
    mine.outliers(dump_invalid = False)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file>'
        exit(1)
