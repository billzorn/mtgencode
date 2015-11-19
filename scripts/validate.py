#!/usr/bin/env python
import sys
import os
import re
from collections import OrderedDict

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
import utils
import jdecode

def list_only(l, items):
    for e in l:
        if not e in items:
            return False
    return True

def check_types(card):
    if 'instant' in card.types:
        return list_only(card.types, ['tribal', 'instant'])
    if 'sorcery' in card.types:
        return list_only(card.types, ['tribal', 'sorcery'])
    if 'creature' in card.types:
        return list_only(card.types, ['tribal', 'creature', 'artifact', 'land', 'enchantment'])
    if 'planeswalker' in card.types:
        return list_only(card.types, ['tribal', 'planeswalker', 'artifact', 'land', 'enchantment'])
    else:
        return list_only(card.types, ['tribal', 'artifact', 'land', 'enchantment'])

def check_pt(card):
    if 'creature' in card.types or card.pt:
        return (('creature' in card.types and len(re.findall(re.escape('/'), card.pt)) == 1)
                and not card.loyalty)
    if 'planeswalker' in card.types or card.loyalty:
        return (('planeswalker' in card.types and card.loyalty)
                and not card.pt)
    return None

# doesn't handle granted activated abilities in ""
def check_X(card):
    correct = None
    incost = 'X' in card.cost.encode()
    extra_cost_lines = 0
    cost_lines = 0
    use_lines = 0
    for mt in card.text_lines:
        sides = mt.text.split(':')
        if len(sides) == 2:
            actcosts = len(re.findall(re.escape(utils.reserved_mana_marker), sides[0]))
            lcosts = mt.costs[:actcosts]
            rcosts = mt.costs[actcosts:]
            if 'X' in sides[0] or (utils.reserved_mana_marker in sides[0] and
                                   'X' in ''.join(map(lambda c: c.encode(), lcosts))):

                if incost:
                    return False # bad, duplicated Xs in costs

                if 'X' in sides[1] or (utils.reserved_mana_marker in sides[1] and
                                       'X' in ''.join(map(lambda c: c.encode(), rcosts))):
                    correct = True # good, defined X is either specified or used
                    if 'monstrosity' in sides[1]:
                        extra_cost_lines += 1
                    continue
                elif 'remove X % counters' in sides[0] and 'each counter removed' in sides[1]:
                    correct = True # Blademane Baku
                    continue
                elif 'note' in sides[1]:
                    correct = True # Ice Cauldron
                    continue
                else:
                    return False # bad, defined X is unused

        # we've checked all cases where an X ocurrs in an activiation cost
        linetext = mt.encode()
        intext = len(re.findall(r'X', linetext))
        defs = (len(re.findall(r'X is', linetext))
                + len(re.findall(re.escape('pay {X'), linetext))
                + len(re.findall(re.escape('pay X'), linetext))
                + len(re.findall(re.escape('reveal X'), linetext))
                + len(re.findall(re.escape('may tap X'), linetext)))

        if incost:
            if intext:
                correct = True # defined and used or specified in some way
        elif intext > 0:
            if intext > 1 and defs > 0:
                correct = True # look for multiples
            elif 'suspend' in linetext or 'bloodthirst' in linetext:
                correct = True # special case keywords
            elif 'reinforce' in linetext and intext > 2:
                correct = True # this should work
            elif 'contain {X' in linetext or 'with {X' in linetext:
                correct = True
                
            elif ('additional cost' in linetext
                  or 'morph' in linetext
                  or 'kicker' in linetext):
                cost_lines += 1
            else:
                use_lines += 1

    if incost and not correct:
        if 'sunburst' in card.text.text or 'spent to cast' in card.text.text:
            return True # Engineered Explosives, Skyrider Elf
        return False # otherwise we should have seen X somewhere if it was in the cost

    elif cost_lines > 0 or use_lines > 0:
        if (cost_lines + extra_cost_lines) == 1 and use_lines > 0:
            return True # dreams, etc.
        else:
            return False

    return correct

def check_counters(card):
    uses = len(re.findall(re.escape(utils.counter_marker), card.text.text))
    if uses > 0:
        return uses > 1 and 'countertype ' + utils.counter_marker in card.text.text
    else:
        return None

props = OrderedDict([
    ('types', check_types),
    ('pt', check_pt),
    ('X', check_X),
    ('counters', check_counters),
])
values = OrderedDict([(k, (0,0,0)) for k in props])

def main(fname, oname = None, verbose = True):
    # may need to set special arguments here
    cards = jdecode.mtg_open_file(fname, verbose=verbose)

    for card in cards:
        for prop in props:
            (total, good, bad) = values[prop]
            this_prop = props[prop](card)
            if not this_prop is None:
                total += 1
                if this_prop:
                    good += 1
                else:
                    bad += 1
                values[prop] = (total, good, bad)

    for prop in props:
        (total, good, bad) = values[prop]
        print prop + ':'
        print '  total: ' + str(total)
        print '  good : ' + str(good)
        print '  bad  : ' + str(bad)

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to process')
    parser.add_argument('outfile', nargs='?', default=None,
                        help='name of output file, will be overwritten')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    main(args.infile, args.outfile, verbose=args.verbose)
    exit(0)
