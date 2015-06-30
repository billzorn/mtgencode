import re
import codecs
import sys

# returns back a dictionary mapping the names of classes of cards
# to lists of cards in those classes
def sortcards(cards):
    classes = {
        'multicards' : [],

        'X cards' : [],
        'counter cards' : [],
        'choice cards' : [],
        'equipment' : [],
        'levelers' : [],
        'legendary' : [],
        
        'planeswalkers' : [],
        'lands' : [],
        'instants' : [],
        'sorceries' : [],
        'enchantments' : [],
        'noncreature artifacts' : [],
        'creatures' : [],
        'other' : [],
    }

    for card in cards:
        # special classes
        if '|\n|' in card:
            classes['multicards'] += [card]
            continue
        
        # inclusive classes
        if 'X' in card:
            classes['X cards'] += [card]
        if '#' in card:
            classes['counter cards'] += [card]
        if 'choose one ~' in card or 'choose two ~' in card or '=' in card:
            classes['choice cards'] += [card]
        if '|equipment|' in card or 'equip {' in card:
            classes['equipment'] += [card]
        if 'level up' in card or 'level &' in card:
            classes['levelers'] += [card]
        if '|legendary|' in card:
            classes['legendary'] += [card]

        # exclusive classes
        if '|planeswalker|' in card:
            classes['planeswalkers'] += [card]
        elif '|land|' in card:
            classes['lands'] += [card]
        elif '|instant|' in card:
            classes['instants'] += [card]
        elif '|sorcery|' in card:
            classes['sorceries'] += [card]
        elif '|enchantment|' in card:
            classes['enchantments'] += [card]
        elif '|artifact|' in card:
            classes['noncreature artifacts'] += [card]
        elif '|creature|' in card or 'artifact creature' in card:
            classes['creatures'] += [card]
        else:
            classes['other'] += [card]
        
    return classes

def main(fname, oname = None, verbose = True):
    if verbose:
        print 'Opening encoded card file: ' + fname

    f = open(fname, 'r')
    text = f.read()
    f.close()

    # we get rid of the first and last because they are probably partial
    cards = text.split('\n\n')[1:-1]
    classes = sortcards(cards)

    if not oname == None:
        if verbose:
            print 'Writing output to: ' + oname
        ofile = codecs.open(oname, 'w', 'utf-8')

    for cardclass in classes:
        print cardclass + ': ' + str(len(classes[cardclass]))

    if oname == None:
        outputter = sys.stdout
    else:
        outputter = ofile

    for cardclass in classes:
        outputter.write('[spoiler=' + cardclass + ']\n')
        for card in classes[cardclass]:
            outputter.write(card + '\n\n')
        outputter.write('[/spoiler]')

    if not oname == None:
        ofile.close()

    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file> [output filename]'
        exit(1)

