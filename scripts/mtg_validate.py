#!/usr/bin/env python
import sys
import os
import re
from collections import OrderedDict

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../lib')
sys.path.append(libdir)
import utils
import jdecode

datadir = os.path.realpath(os.path.join(libdir, '../data'))
gramdir = os.path.join(datadir, 'ngrams')
compute_ngrams = False
gramdicts = {}
if os.path.isdir(gramdir):
    import keydiff
    compute_ngrams = True
    for fname in os.listdir(gramdir):
        suffixes = re.findall(r'\.[0-9]*g$', fname)
        if suffixes:
            grams = int(suffixes[0][1:-1])
            d = {}
            with open(os.path.join(gramdir, fname), 'rt') as f:
                keydiff.parse_keyfile(f, d, int)
            gramdicts[grams] = d

def rare_grams(card, thresh = 2, grams = 2):
    if not grams in gramdicts:
        return None
    rares = 0
    gramdict = gramdicts[grams]
    for line in card.text_lines_words:
        for i in range(0, len(line) - (grams - 1)):
            ngram = ' '.join([line[i + j] for j in range(0, grams)])
            if ngram in gramdict:
                if gramdict[ngram] < thresh:
                    rares += 1
            else:
                rares += 1
    return rares

def list_only(l, items):
    for e in l:
        if not e in items:
            return False
    return True

def pct(x, total):
    pctstr = 100.0 * float(x) / float(total)
    return '(' + str(pctstr)[:5] + '%)'

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
    if ('creature' in card.types or 'vehicle' in card.subtypes) or card.pt:
        return ((('creature' in card.types or 'vehicle' in card.subtypes) and len(re.findall(re.escape('/'), card.pt)) == 1)
                and not card.loyalty)
    if 'planeswalker' in card.types or card.loyalty:
        return (('planeswalker' in card.types and card.loyalty)
                and not card.pt)
    return None

def check_lands(card):
    if 'land' in card.types:
        return card.cost.format() == '_NOCOST_'
    else:
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

def check_kicker(card):
    # also lazy and simple
    if 'kicker' in card.text.text or 'kicked' in card.text.text:
        # could also check for costs, at least make 'it's $ kicker,' not count as a kicker ability
        newtext = card.text.text.replace(utils.reserved_mana_marker + ' kicker', '')
        return 'kicker' in newtext and 'kicked' in newtext
    else:
        return None

def check_counters(card):
    uses = len(re.findall(re.escape(utils.counter_marker), card.text.text))
    if uses > 0:
        return uses > 1 and 'countertype ' + utils.counter_marker in card.text.text
    else:
        return None

def check_choices(card):
    bullets = len(re.findall(re.escape(utils.bullet_marker), card.text.text))
    obracks = len(re.findall(re.escape(utils.choice_open_delimiter), card.text.text))
    cbracks = len(re.findall(re.escape(utils.choice_close_delimiter), card.text.text))
    if bullets + obracks + cbracks > 0:
        if not (obracks == cbracks and bullets > 0):
            return False
        # could compile ahead of time
        choice_regex = (re.escape(utils.choice_open_delimiter) + re.escape(utils.unary_marker)
                        + r'.*' + re.escape(utils.bullet_marker) + r'.*' 
                        + re.escape(utils.choice_close_delimiter))
        nochoices = re.sub(choice_regex, '', card.text.text)
        nobullets = len(re.findall(re.escape(utils.bullet_marker), nochoices))
        noobracks = len(re.findall(re.escape(utils.choice_open_delimiter), nochoices))
        nocbracks = len(re.findall(re.escape(utils.choice_close_delimiter), nochoices))
        return nobullets + noobracks + nocbracks == 0
    else:
        return None

def check_auras(card):
    # a bit loose
    if 'enchantment' in card.types or 'aura' in card.subtypes or 'enchant' in card.text.text:
        return 'enchantment' in card.types or 'aura' in card.subtypes or 'enchant' in card.text.text
    else:
        return None

def check_equipment(card):
    # probably even looser, chould check for actual equip abilities and noncreatureness
    if 'equipment' in card.subtypes:
        return 'equip' in card.text.text
    else:
        return None

def check_vehicles(card):
    if 'vehicle' in card.subtypes:
	return 'crew' in card.text.text
    else:
	return None

def check_planeswalkers(card):
    if 'planeswalker' in card.types:
        good_lines = 0
        bad_lines = 0
        initial_re = r'^[+-]?' + re.escape(utils.unary_marker) + re.escape(utils.unary_counter) + '*:'
        initial_re_X = r'^[-+]' + re.escape(utils.x_marker) + '+:'
        for line in card.text_lines:
            if len(re.findall(initial_re, line.text)) == 1:
                good_lines += 1
            elif len(re.findall(initial_re_X, line.text)) == 1:
                good_lines += 1
            elif 'can be your commander' in line.text:
                pass
            elif 'countertype' in line.text or 'transform' in line.text:
                pass
            else:
                bad_lines += 1
        return good_lines > 1 and bad_lines == 0
    else:
        return None

def check_levelup(card):
    if 'level' in card.text.text:
        uplines = 0
        llines = 0
        for line in card.text_lines:
            if 'countertype ' + utils.counter_marker + ' level' in line.text:
                uplines += 1
                llines += 1
            elif 'with level up' in line.text:
                llines += 1
            elif 'level up' in line.text:
                uplines += 1
            elif 'level' in line.text:
                llines += 1
        return uplines == 1 and llines > 0
    else:
        return None

def check_activated(card):
    activated = 0
    for line in card.text_lines:
        if '.' in line.text:
            subtext = re.sub(r'"[^"]*"', '', line.text)
            if 'forecast' in subtext:
                pass
            elif 'return ' + utils.this_marker + ' from your graveyard' in subtext:
                pass
            elif 'on the stack' in subtext:
                pass
            elif ':' in subtext:
                activated += 1
    if activated > 0:
        return list_only(card.types, ['creature', 'land', 'artifact', 'enchantment', 'planeswalker', 'tribal'])
    else:
        return None

def check_triggered(card):
    triggered = 0
    triggered_2 = 0
    for line in card.text_lines:
        if 'when ' + utils.this_marker + ' enters the battlefield' in line.text:
            triggered += 1
        if 'when ' + utils.this_marker + ' leaves the battlefield' in line.text:
            triggered += 1
        if 'when ' + utils.this_marker + ' dies' in line.text:
            triggered += 1
        elif 'at the beginning' == line.text[:16] or 'when' == line.text[:4]:
            if 'from your graveyard' in line.text:
                triggered_2 += 1
            elif 'in your graveyard' in line.text:
                triggered_2 += 1
            elif 'if ' + utils.this_marker + ' is suspended' in line.text:
                triggered_2 += 1
            elif 'if that card is exiled' in line.text or 'if ' + utils.this_marker + ' is exiled' in line.text:
                triggered_2 += 1
            elif 'when the creature ' + utils.this_marker + ' haunts' in line.text:
                triggered_2 += 1
            elif 'when you cycle ' + utils.this_marker in line.text or 'when you cast ' + utils.this_marker in line.text:
                triggered_2 += 1
            elif 'this turn' in line.text or 'this combat' in line.text or 'your next upkeep' in line.text:
                triggered_2 += 1
            elif 'from your library' in line.text:
                triggered_2 += 1
            elif 'you discard ' + utils.this_marker in line.text or 'you to discard ' + utils.this_marker in line.text:
                triggered_2 += 1
            else:
                triggered += 1
            
    if triggered > 0:
        return list_only(card.types, ['creature', 'land', 'artifact', 'enchantment', 'planeswalker', 'tribal'])
    elif triggered_2:
        return True
    else:
        return None

def check_chosen(card):
    if 'chosen' in card.text.text:
        return ('choose' in card.text.text
                or 'chosen at random' in card.text.text
                or 'name' in card.text.text
                or 'is chosen' in card.text.text
                or 'search' in card.text.text)
    else:
        return None

def check_shuffle(card):
    retval = None
    # sadly, this does not detect spurious shuffling
    for line in card.text_lines:
        if 'search' in line.text and 'library' in line.text:
            thisval = ('shuffle' in line.text
                       or 'searches' in line.text
                       or 'searched' in line.text
                       or 'searching' in line.text
                       or 'rest' in line.text
                       or 'instead' in line.text)
            if retval is None:
                retval = thisval
            else:
                retval = retval and thisval
    return retval

def check_quotes(card):
    retval = None
    for line in card.text_lines:
        quotes = len(re.findall(re.escape('"'), line.text))
        # HACK: the '" pattern in the training set is actually incorrect
        quotes += len(re.findall(re.escape('\'"'), line.text))
        if quotes > 0:
            thisval = quotes % 2 == 0
            if retval is None:
                retval = thisval
            else:
                retval = retval and thisval
    return retval

props = OrderedDict([
    ('types', check_types),
    ('pt', check_pt),
    ('lands', check_lands),
    ('X', check_X),
    ('kicker', check_kicker),
    ('counters', check_counters),
    ('choices', check_choices),
    ('quotes', check_quotes),
    ('auras', check_auras),
    ('equipment', check_equipment),
    ('vehicles', check_vehicles),
    ('planeswalkers', check_planeswalkers),
    ('levelup', check_levelup),
    ('chosen', check_chosen),
    ('shuffle', check_shuffle),
    ('activated', check_activated),
    ('triggered', check_triggered),
])

def process_props(cards, dump = False, uncovered = False):
    total_all = 0
    total_good = 0
    total_bad = 0
    total_uncovered = 0
    values = OrderedDict([(k, (0,0,0)) for k in props])

    for card in cards:
        total_all += 1
        overall = True
        any_prop = False
        for prop in props:
            (total, good, bad) = values[prop]
            this_prop = props[prop](card)
            if not this_prop is None:
                total += 1
                if not prop == 'types':
                    any_prop = True
                if this_prop:
                    good += 1
                else:
                    bad += 1
                    overall = False
                    if card.name not in ['demonic pact', 'lavaclaw reaches',
                                         "ertai's trickery", 'rumbling aftershocks', # i hate these
                    ] and dump:
                        print('---- ' + prop + ' ----')
                        print(card.encode())
                        print(card.format())
                values[prop] = (total, good, bad)
        if overall:
            total_good += 1
        else:
            total_bad += 1
        if not any_prop:
            total_uncovered += 1
            if uncovered:
                print('---- uncovered ----')
                print(card.encode())
                print(card.format())

    return ((total_all, total_good, total_bad, total_uncovered),
            values)

def main(fname, oname = None, verbose = False, dump = False):
    # may need to set special arguments here
    cards = jdecode.mtg_open_file(fname, verbose=verbose)
    
    do_grams = False

    if do_grams:
        rg = {}
        for card in cards:
            g = rare_grams(card, thresh=2, grams=2)
            if len(card.text_words) > 0:
                g = int(1.0 + (float(g) * 100.0 / float(len(card.text_words))))
            if g in rg:
                rg[g] += 1
            else:
                rg[g] = 1
            if g >= 60:
                print g
                print card.format()

        tot = 0
        vmax = sum(rg.values())
        pct90 = None
        pct95 = None
        pct99 = None
        for i in sorted(rg):
            print str(i) + ' rare ngrams: ' + str(rg[i])
            tot += rg[i]
            if pct90 is None and tot >= vmax * 0.90:
                pct90 = i
            if pct95 is None and tot >= vmax * 0.95:
                pct95 = i
            if pct99 is None and tot >= vmax * 0.99:
                pct99 = i

        print '90% - ' + str(pct90)
        print '95% - ' + str(pct95)
        print '99% - ' + str(pct99)

    else:
        ((total_all, total_good, total_bad, total_uncovered), 
         values) = process_props(cards, dump=dump)

        # summary
        print('-- overall --')
        print('  total     : ' + str(total_all))
        print('  good      : ' + str(total_good) + ' ' + pct(total_good, total_all))
        print('  bad       : ' + str(total_bad) + ' ' + pct(total_bad, total_all))
        print('  uncocoverd: ' + str(total_uncovered) + ' ' + pct(total_uncovered, total_all))
        print('----')

        # breakdown
        for prop in props:
            (total, good, bad) = values[prop]
            print(prop + ':')
            print('  total: ' + str(total) + ' ' + pct(total, total_all))
            print('  good : ' + str(good) + ' ' + pct(good, total_all))
            print('  bad  : ' + str(bad) + ' ' + pct(bad, total_all))


if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infile', #nargs='?'. default=None,
                        help='encoded card file or json corpus to process')
    parser.add_argument('outfile', nargs='?', default=None,
                        help='name of output file, will be overwritten')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')
    parser.add_argument('-d', '--dump', action='store_true', 
                        help='print invalid cards')

    args = parser.parse_args()
    main(args.infile, args.outfile, verbose=args.verbose, dump=args.dump)
    exit(0)
 
