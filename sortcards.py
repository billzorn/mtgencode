#!/usr/bin/env python
import re
import codecs
import sys
from collections import OrderedDict

# returns back a dictionary mapping the names of classes of cards
# to lists of cards in those classes
def sortcards(cards):
    classes = OrderedDict([
        ('Special classes:', None),
        ('multicards', []),
        ('Inclusive classes:', None),
        ('X cards', []),
        ('kicker cards', []),
        ('counter cards', []),
        ('uncast cards', []),
        ('choice cards', []),
        ('equipment', []),
        ('levelers', []),
        ('legendary', []),
        ('Exclusive classes:', None),
        ('planeswalkers', []),
        ('lands', []),
        ('instants', []),
        ('sorceries', []),
        ('enchantments', []),
        ('noncreature artifacts', []),
        ('creatures', []),
        ('other', []),
        ('By color:', None),
        ('white', []),
        ('blue', []),
        ('black', []),
        ('red', []),
        ('green', []),
        ('colorless nonland', []),
        ('colorless land', []),
        ('unknown color', []),
        ('By number of colors:', None),
        ('zero colors', []),                
        ('one color', []),
        ('two colors', []),
        ('three colors', []),
        ('four colors', []),
        ('five colors', []),
        ('more colors?', []),
    ])

    for card in cards:
        # special classes
        if '|\n|' in card:
            # better formatting pls???
            classes['multicards'] += [card.replace('|\n|', '|\n~~~~~~~~~~~~~~~~\n|')]
            continue
        
        # inclusive classes
        if 'X' in card:
            classes['X cards'] += [card]
        if 'kick' in card:
            classes['kicker cards'] += [card]
        if '%' in card or '#' in card:
            classes['counter cards'] += [card]
        if 'uncast' in card:
            classes['uncast cards'] += [card]
        if '[' in card or ']' in card or '=' in card:
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

        # color classes need to find the mana cost
        fields = card.split('|')
        if len(fields) != 11:
            classes['unknown color'] += [card]
        else:
            cost = fields[8]
            color_count = 0
            if 'W' in cost or 'U' in cost or 'B' in cost or 'R' in cost or 'G' in cost:
                if 'W' in cost:
                    classes['white'] += [card]
                    color_count += 1
                if 'U' in cost:
                    classes['blue'] += [card]
                    color_count += 1
                if 'B' in cost:
                    classes['black'] += [card]
                    color_count += 1
                if 'R' in cost:
                    classes['red'] += [card]
                    color_count += 1
                if 'G' in cost:
                    classes['green'] += [card]
                    color_count += 1
                # should be unreachable
                if color_count == 0:
                    classes['unknown color'] += [card]
            else:
                if '|land|' in card:
                    classes['colorless land'] += [card]
                else:
                    classes['colorless nonland'] += [card]
            
            if color_count == 0:
                classes['zero colors'] += [card]
            elif color_count == 1:
                classes['one color'] += [card]
            elif color_count == 2:
                classes['two colors'] += [card]
            elif color_count == 3:
                classes['three colors'] += [card]
            elif color_count == 4:
                classes['four colors'] += [card]
            elif color_count == 5:
                classes['five colors'] += [card]
            else:
                classes['more colors?'] += [card]
        
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
        if classes[cardclass] == None:
            print cardclass
        else:
            print '  ' + cardclass + ': ' + str(len(classes[cardclass]))

    if oname == None:
        outputter = sys.stdout
    else:
        outputter = ofile

    for cardclass in classes:
        if classes[cardclass] == None:
            outputter.write(cardclass + '\n')
        else:
            classlen = len(classes[cardclass])
            if classlen > 0:
                outputter.write('[spoiler=' + cardclass + ': ' + str(classlen) + ' cards]\n')
                for card in classes[cardclass]:
                    outputter.write(card + '\n\n')
                outputter.write('[/spoiler]\n')

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

