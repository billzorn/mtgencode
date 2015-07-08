import utils
import datamine
import random

def main(fname, oname = None, verbose = True):
    if verbose:
        print 'Opening encoded card file: ' + fname

    with open(fname, 'rt') as f:
        text = f.read()

    cardtexts = text.split(utils.cardsep)
    
    # overkill
    datamine.analyze(cardtexts)

    multicards = []
    reps = 5

    for card in datamine.cards:
        for i in range(reps):
            multicards += [card.reencode(randomize = True)]
            
    random.shuffle(multicards)

    if oname:
        if verbose:
            print 'Writing output to: ' + oname
            with open(oname, 'w') as ofile:
                for textcard in multicards:
                    ofile.write(textcard + utils.cardsep)
    else:
        for textcard in multicards:
            print textcard + '\n'

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file> [output filename]'
        exit(1)
