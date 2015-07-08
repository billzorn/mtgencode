import re
import codecs
import sys
import random

import utils

# Format a list of rows of data into nice columns.
# Note that it's the columns that are nice, not this code.
def padrows(l):
    # get length for each field
    lens = []
    for ll in l:
        for i, field in enumerate(ll):
            if i < len(lens):
                lens[i] = max(len(str(field)), lens[i])
            else:
                lens += [len(str(field))]
    # now pad out to that length
    padded = []
    for ll in l:
        padded += ['']
        for i, field in enumerate(ll):
            s = str(field)
            pad = ' ' * (lens[i] - len(s))
            padded[-1] += (s + pad + ' ')
    return padded
def printrows(l):
    for row in l:
        print row

def randomize_all_mana(text):
    manastrs = re.findall(utils.mana_regex, text)
    newtext = text
    for manastr in sorted(manastrs, lambda x,y: cmp(len(x), len(y)), reverse = True):
        newtext = newtext.replace(manastr, utils.reserved_marker)
    for manastr in manastrs:
        newtext = newtext.replace(utils.reserved_marker, 
                                  Manacost(manastr).reencode(randomize = True),
                                  1)
    return newtext

# so this stuff still needs to be cleaned up
punctuation_chars = r'[+\-*",.:;WUBRGPV/XTQ|\\&^\{\}@ \n=~%\[\]]'
creature_keywords = [
    # evergreen
    'deathtouch',
    'defender',
    'double strike',
    'first strike',
    'flash',
    'flying',
    'haste',
    'hexproof',
    'indestructible',
    'lifelink',
    'menace',
    'prowess',
    'reach',
    'trample',
    'vigilance',
    # no longer evergreen
    'banding',
    'fear',
    'shroud',
    'intimidate',
    # expert level keywords
    'absorb',
    'amplify',
    'annihilator',
    'battle cry',
    'bolster',
    'bloodthirst',
    'bushido',
    'changeling',
    'convoke',
    'devour',
    'evolve',
    'exalted',
    'extort',
    'fading',
    'flanking',
    'frenzy',
    'graft',
    'haunt',
    'horsemanship',
    'infect',
    'modular',
    #'morph',
    #'ninjutsu',
    'persist',
    'poisonous',
    'provoke',
    #'prowl',
    'rampage',
    'ripple',
    #'scavenge',
    'shadow',
    'soulbond',
    'soulshift',
    'split second',
    'sunburst',
    'undying',
    #'unearth',
    'unleash',
    'vanishing',
    'wither',
] # there are other keywords out there, these are just easy to detect

# data aggregating classes
class Manacost:
    '''mana cost representation with data'''
    
    # hardcoded to be dependent on the symbol structure... ah well
    def get_colors(self):
        colors = ''
        for sym in self.symbols:
            if self.symbols[sym] > 0:
                symcolors = re.sub(r'2|P|S|X', '', sym)
                for symcolor in symcolors:
                    if symcolor not in colors:
                        colors += symcolor
        # sort so the order is always consistent
        return ''.join(sorted(colors))

    def check_colors(self, symbolstring):
        for sym in symbolstring:
            if not sym in self.colors:
                return False
        return True

    def __init__(self, text):
        self.raw = text
        self.cmc = 0
        self.colorless = 0
        self.sequence = []
        self.symbols = {sym : 0 for sym in utils.mana_syms}
        self.allsymbols = {sym : 0 for sym in utils.mana_symall}

        if text == '':
            self._parsed = True
            self._valid = True
            self.none = True
            self.inner = ''

        elif not (len(self.raw) >= 2 and self.raw[0] == '{' and self.raw[-1] == '}'):
            self._parsed = False
            self._valid = False
            self.none = False

        else:
            self._parsed = True
            self._valid = True
            self.none = False
            self.inner = self.raw[1:-1]

            # structure mirrors the decoding in utils, but we pull out different data here
            idx = 0
            while idx < len(self.inner):
                # taking this branch is an infinite loop if unary_marker is empty
                if (len(utils.mana_unary_marker) > 0 and 
                    self.inner[idx:idx+len(utils.mana_unary_marker)] == utils.mana_unary_marker):
                    idx += len(utils.mana_unary_marker)
                    self.sequence += [utils.mana_unary_marker]
                elif self.inner[idx:idx+len(utils.mana_unary_counter)] == utils.mana_unary_counter:
                    idx += len(utils.mana_unary_counter)
                    self.sequence += [utils.mana_unary_counter]
                    self.colorless += 1
                    self.cmc += 1
                else:
                    old_idx = idx
                    for symlen in range(utils.mana_symlen_min, utils.mana_symlen_max + 1):
                        encoded_sym = self.inner[idx:idx+symlen]
                        if encoded_sym in utils.mana_symall_decode:
                            idx += symlen
                            # leave the sequence encoded for convenience
                            self.sequence += [encoded_sym]
                            sym = utils.mana_symall_decode[encoded_sym]
                            self.allsymbols[sym] += 1
                            if sym in utils.mana_symalt:
                                self.symbols[utils.mana_alt(sym)] += 1
                            else:
                                self.symbols[sym] += 1
                            if sym == utils.mana_X:
                                self.cmc += 0
                            elif utils.mana_2 in sym:
                                self.cmc += 2
                            else:
                                self.cmc += 1
                            break
                    # otherwise we'll go into an infinite loop if we see a symbol we don't know
                    if idx == old_idx:
                        idx += 1
                        self._valid = False

        self.colors = self.get_colors()

    def __str__(self):
        return utils.mana_untranslate(utils.mana_open_delimiter + ''.join(self.sequence)
                                      + utils.mana_close_delimiter)

    def format(self, for_forum):
        return utils.mana_untranslate(utils.mana_open_delimiter + ''.join(self.sequence, for_forum)
                                      + utils.mana_close_delimiter)

    def reencode(self, randomize = False):
        if self.none:
            return ''
        elif randomize:
            # so this won't work very well if mana_unary_marker isn't empty
            return (utils.mana_open_delimiter 
                    + ''.join(random.sample(self.sequence, len(self.sequence)))
                    + utils.mana_close_delimiter)
        else:
            return utils.mana_open_delimiter + ''.join(self.sequence) + utils.mana_close_delimiter

class Card:
    '''card representation with data'''

    def __init__(self, text):
        self.raw = text
        self._parsed = True
        self._valid = True

        if '\n' in self.raw:
            halves = self.raw.split('\n')
            if not len(halves) == 2:
                self._parsed = False
                self._valid = False
                self.fields = halves
                return
            else:
                self.raw = halves[0]
                self.bside = Card(halves[1])
                if not self.bside._valid:
                    self._valid = False
        else:
            self.bside = None

        fields = self.raw.split(utils.fieldsep)
        if not len(fields) >= 10:
            self._parsed = False
            self._valid = False
            self.fields = fields
        else:
            if not fields[1] == '':
                self.name = fields[1]
            else:
                self.name = ''
                self._valid = False

            if not fields[2] == '':
                self.supertypes = fields[2].split(' ')
            else:
                self.supertypes = []

            if not fields[3] == '':
                self.types = fields[3].split(' ')
            else:
                self.types = []
                self._valid = False

            if not fields[4] == '':
                self.loyalty = fields[4]
                try:
                    self.loyalty_value = int(self.loyalty)
                except ValueError:
                    self.loyalty_value = None
                    # strictly speaking, '* where * is something' is valid...
                    # self._valid = False
            else:
                self.loyalty = None
                self.loyalty_value = None

            if not fields[5] == '':
                self.subtypes = fields[5].split(' ')
                if 'creature' in self.types:
                    self.creaturetypes = self.subtypes
                else:
                    self.creaturetypes = []
            else:
                self.subtypes = []
                self.creaturetypes = []

            if not fields[6] == '':
                self.pt = fields[6]
                self.power = None
                self.power_value = None
                self.toughness = None
                self.toughness_value = None
                p_t = self.pt.split('/')
                if len(p_t) == 2:
                    self.power = p_t[0]
                    try:
                        self.power_value = int(self.power)
                    except ValueError:
                        self.power_value = None
                    self.toughness = p_t[1]
                    try:
                        self.toughness_value = int(self.toughness)
                    except ValueError:
                        self.toughness_value = None
                else:
                    self._valid = False
            else:
                self.pt = None
                self.power = None
                self.power_value = None
                self.toughness = None
                self.toughness_value = None

            # if there's no cost (lands) then cost.none will be True
            self.cost = Manacost(fields[7])
            
            if not fields[8] == '':
                self.text = fields[8]
                self.text_lines = self.text.split(utils.newline)
                self.text_words = re.sub(punctuation_chars, ' ', self.text).split()
                self.creature_words = []
                # SUPER HACK
                if 'creature' in self.types:
                    for line in self.text_lines:
                        orig_line = line
                        guess = []
                        for keyword in creature_keywords:
                            if keyword in line:
                                guess += [keyword]
                                line = line.replace(keyword, '')
                        # yeah, I said it was a hack
                        if re.sub(punctuation_chars, ' ', line).split() == [] or 'protect' in line or 'walk' in line or 'sliver creatures' in line or 'you control have' in line:
                            for word in guess:
                                if word not in self.creature_words:
                                    self.creature_words += [word]
                        # elif len(guess) > 0 and len(line) < 30:
                        #     print orig_line
            else:
                self.text = ''
                self.text_lines = []
                self.text_words = []
                self.creature_words = []

    def __str__(self):
        return ''.join([
            utils.fieldsep,
            self.name,
            utils.fieldsep,
            (' ' + utils.dash_marker + ' ').join([' '.join(self.supertypes + self.types),
                                                   ' '.join(self.subtypes)]),
            utils.fieldsep,
            str(self.cost.cmc) if self.cost.colors == '' 
            else str(self.cost.cmc) + ', ' + self.cost.colors,
            utils.fieldsep,
        ])
        
    def reencode(self, randomize = False):
        return ''.join([
            utils.fieldsep,
            self.name,
            utils.fieldsep,
            ' '.join(self.supertypes),
            utils.fieldsep,
            ' '.join(self.types),
            utils.fieldsep,
            self.loyalty if self.loyalty else '',
            utils.fieldsep,
            ' '.join(self.subtypes),
            utils.fieldsep,
            self.pt if self.pt else '',
            utils.fieldsep,
            self.cost.reencode(randomize) if not self.cost.none else '',
            utils.fieldsep,
            self.text if not randomize else randomize_all_mana(self.text),
            utils.fieldsep,
            utils.bsidesep + self.bside.reencode(randomize) if self.bside else '',
        ])

# global card pools
unparsed_cards = []
invalid_cards = []
cards = []
allcards = []

# global indices
by_name = {}
by_type = {}
by_type_inclusive = {}
by_supertype = {}
by_supertype_inclusive = {}
by_subtype = {}
by_subtype_inclusive = {}
by_color = {}
by_color_inclusive = {}
by_color_count = {}
by_cmc = {}
by_cost = {}
by_power = {}
by_toughness = {}
by_pt = {}
by_loyalty = {}
by_textlines = {}
by_textlen = {}

indices = {
    'by_name' : by_name,
    'by_type' : by_type,
    'by_type_inclusive' : by_type_inclusive,
    'by_supertype' : by_supertype,
    'by_supertype_inclusive' : by_supertype_inclusive,
    'by_subtype' : by_subtype,
    'by_subtype_inclusive' : by_subtype_inclusive,
    'by_color' : by_color,
    'by_color_inclusive' : by_color_inclusive,
    'by_color_count' : by_color_count,
    'by_cmc' : by_cmc,
    'by_cost' : by_cost,
    'by_power' : by_power,
    'by_toughness' : by_toughness,
    'by_pt' : by_pt,
    'by_loyalty' : by_loyalty,
    'by_textlines' : by_textlines,
    'by_textlen' : by_textlen,
}

def index_size(d):
    return sum(map(lambda k: len(d[k]), d))

def inc(d, k, obj):
    if k or k == 0:
        if k in d:
            d[k] += obj
        else:
            d[k] = obj

# build the global indices
def analyze(cardtexts):
    global unparsed_cards, invalid_cards, cards, allcards
    for cardtext in cardtexts:
        # the empty card is not interesting
        if not cardtext:
            continue
        card = Card(cardtext)
        if card._valid:
            cards += [card]
            allcards += [card]
        elif card._parsed:
            invalid_cards += [card]
            allcards += [card]
        else:
            unparsed_cards += [card]

        if card._parsed:
            inc(by_name, card.name, [card])

            inc(by_type, ' '.join(card.types), [card])
            for t in card.types:
                inc(by_type_inclusive, t, [card])
            inc(by_supertype, ' '.join(card.supertypes), [card])
            for t in card.supertypes:
                inc(by_supertype_inclusive, t, [card])
            inc(by_subtype, ' '.join(card.subtypes), [card])
            for t in card.subtypes:
                inc(by_subtype_inclusive, t, [card])

            if card.cost.colors:
                inc(by_color, card.cost.colors, [card])
                for c in card.cost.colors:
                    inc(by_color_inclusive, c, [card])
                inc(by_color_count, len(card.cost.colors), [card])
            else:
                # colorless, still want to include in these tables
                inc(by_color, 'A', [card])
                inc(by_color_inclusive, 'A', [card])
                inc(by_color_count, 0, [card])

            inc(by_cmc, card.cost.cmc, [card])
            inc(by_cost, card.cost.reencode() if card.cost.reencode() else 'none', [card])

            inc(by_power, card.power, [card])
            inc(by_toughness, card.toughness, [card])
            inc(by_pt, card.pt, [card])

            inc(by_loyalty, card.loyalty, [card])
            
            inc(by_textlines, len(card.text_lines), [card])
            inc(by_textlen, len(card.text), [card])

# summarize the indices
# Yes, this printing code is pretty terrible.
def summarize(hsize = 10, vsize = 10, cmcsize = 20):
    print '===================='
    print str(len(cards)) + ' valid cards, ' + str(len(invalid_cards)) + ' invalid cards.'
    print str(len(allcards)) + ' cards parsed, ' + str(len(unparsed_cards)) + ' failed to parse'
    print '--------------------'
    print str(len(by_name)) + ' unique card names'
    print '--------------------'
    print (str(len(by_color_inclusive)) + ' represented colors (including colorless as \'A\'), ' 
           + str(len(by_color)) + ' combinations')
    print 'Breakdown by color:'
    rows = [by_color_inclusive.keys()]
    rows += [[len(by_color_inclusive[k]) for k in rows[0]]]
    printrows(padrows(rows))
    print 'Breakdown by number of colors:'
    rows = [by_color_count.keys()]
    rows += [[len(by_color_count[k]) for k in rows[0]]]
    printrows(padrows(rows))
    print '--------------------'
    print str(len(by_type_inclusive)) + ' unique card types, ' + str(len(by_type)) + ' combinations'
    print 'Breakdown by type:'
    d = sorted(by_type_inclusive, 
               lambda x,y: cmp(len(by_type_inclusive[x]), len(by_type_inclusive[y])), 
               reverse = True)
    rows = [[k for k in d[:hsize]]]
    rows += [[len(by_type_inclusive[k]) for k in rows[0]]]
    printrows(padrows(rows))
    print '--------------------'
    print (str(len(by_subtype_inclusive)) + ' unique subtypes, ' 
           + str(len(by_subtype)) + ' combinations')
    print '-- Popular subtypes: --'
    d = sorted(by_subtype_inclusive, 
               lambda x,y: cmp(len(by_subtype_inclusive[x]), len(by_subtype_inclusive[y])), 
               reverse = True)
    rows = []
    for k in d[0:vsize]:
        rows += [[k, len(by_subtype_inclusive[k])]]
    printrows(padrows(rows))
    print '-- Top combinations: --'
    d = sorted(by_subtype, 
               lambda x,y: cmp(len(by_subtype[x]), len(by_subtype[y])), 
               reverse = True)
    rows = []
    for k in d[0:vsize]:
        rows += [[k, len(by_subtype[k])]]
    printrows(padrows(rows))
    print '--------------------'
    print (str(len(by_supertype_inclusive)) + ' unique supertypes, ' 
           + str(len(by_supertype)) + ' combinations')
    print 'Breakdown by supertype:'
    d = sorted(by_supertype_inclusive, 
               lambda x,y: cmp(len(by_supertype_inclusive[x]),len(by_supertype_inclusive[y])), 
               reverse = True)
    rows = [[k for k in d[:hsize]]]
    rows += [[len(by_supertype_inclusive[k]) for k in rows[0]]]
    printrows(padrows(rows))
    print '--------------------'
    print str(len(by_cmc)) + ' different CMCs, ' + str(len(by_cost)) + ' unique mana costs'
    print 'Breakdown by CMC:'
    d = sorted(by_cmc, reverse = False)
    rows = [[k for k in d[:cmcsize]]]
    rows += [[len(by_cmc[k]) for k in rows[0]]]
    printrows(padrows(rows))
    print '-- Popular mana costs: --'
    d = sorted(by_cost, 
               lambda x,y: cmp(len(by_cost[x]), len(by_cost[y])), 
               reverse = True)
    rows = []
    for k in d[0:vsize]:
        rows += [[utils.from_mana(k), len(by_cost[k])]]
    printrows(padrows(rows))
    print '--------------------'
    print str(len(by_pt)) + ' unique p/t combinations'
    print ('Largest power: ' + str(max(map(len, by_power)) - 1) + 
           ', largest toughness: ' + str(max(map(len, by_toughness)) - 1))
    print '-- Popular p/t values: --'
    d = sorted(by_pt, 
               lambda x,y: cmp(len(by_pt[x]), len(by_pt[y])), 
               reverse = True)
    rows = []
    for k in d[0:vsize]:
        rows += [[utils.from_unary(k), len(by_pt[k])]]
    printrows(padrows(rows))
    print '--------------------'
    print 'Loyalty values:'
    d = sorted(by_loyalty, 
               lambda x,y: cmp(len(by_loyalty[x]), len(by_loyalty[y])), 
               reverse = True)
    rows = []
    for k in d[0:vsize]:
        rows += [[utils.from_unary(k), len(by_loyalty[k])]]
    printrows(padrows(rows))
    print '--------------------'
    print('Card text ranges from ' + str(min(by_textlen)) + ' to ' 
          + str(max(by_textlen)) + ' characters in length')
    print('Card text ranges from ' + str(min(by_textlines)) + ' to '
          + str(max(by_textlines)) + ' lines')
    print '-- Line counts by frequency: --'
    d = sorted(by_textlines, 
               lambda x,y: cmp(len(by_textlines[x]), len(by_textlines[y])), 
               reverse = True)
    rows = []
    for k in d[0:vsize]:
        rows += [[k, len(by_textlines[k])]]
    printrows(padrows(rows))
    print '===================='


# describe outliers in the indices
def outliers(hsize = 10, vsize = 10, dump_invalid = False):
    print '********************'
    print 'Overview of indices:'
    rows = [['Index Name', 'Keys', 'Total Members']]
    for index in indices:
        rows += [[index, len(indices[index]), index_size(indices[index])]]
    printrows(padrows(rows))
    print '********************'
    if len(by_name) > 0:
        scardname =  sorted(by_name, 
                            lambda x,y: cmp(len(x), len(y)), 
                            reverse = False)[0]
        print 'Shortest Cardname: (' + str(len(scardname)) + ')'
        print '  ' + scardname
        lcardname =  sorted(by_name, 
                            lambda x,y: cmp(len(x), len(y)), 
                            reverse = True)[0]
        print 'Longest Cardname: (' + str(len(lcardname)) + ')'
        print '  ' + lcardname
        d = sorted(by_name, 
                   lambda x,y: cmp(len(by_name[x]), len(by_name[y])), 
                   reverse = True)
        rows = []
        for k in d[0:vsize]:
            if len(by_name[k]) > 1:
                rows += [[k, len(by_name[k])]]
        if rows == []:
            print('No duplicated cardnames')
        else:
            print '-- Most duplicated names: --'
            printrows(padrows(rows))
    else:
        print 'No cards indexed by name?'
    print '--------------------'
    if len(by_type) > 0:
        ltypes = sorted(by_type, 
                        lambda x,y: cmp(len(x), len(y)), 
                        reverse = True)[0]
        print 'Longest card type: (' + str(len(ltypes)) + ')'
        print '  ' + ltypes
    else:
        print 'No cards indexed by type?'
    if len(by_subtype) > 0:
        lsubtypes = sorted(by_subtype, 
                           lambda x,y: cmp(len(x), len(y)), 
                           reverse = True)[0]
        print 'Longest subtype: (' + str(len(lsubtypes)) + ')'
        print '  ' + lsubtypes
    else:
        print 'No cards indexed by subtype?'
    if len(by_supertype) > 0:
        lsupertypes = sorted(by_supertype, 
                        lambda x,y: cmp(len(x), len(y)), 
                             reverse = True)[0]
        print 'Longest supertype: (' + str(len(lsupertypes)) + ')'
        print '  ' + lsupertypes
    else:
        print 'No cards indexed by supertype?'
    print '--------------------'
    if len(by_cost) > 0:
        lcost = sorted(by_cost, 
                       lambda x,y: cmp(len(x), len(y)), 
                       reverse = True)[0]
        print 'Longest mana cost: (' + str(len(lcost)) + ')'
        print '  ' + utils.from_mana(lcost)
        print '\n' + by_cost[lcost][0].reencode() + '\n'
    else:
        print 'No cards indexed by cost?'
    if len(by_cmc) > 0:
        lcmc = sorted(by_cmc, reverse = True)[0]
        print 'Largest cmc: (' + str(lcmc) + ')'
        print '  ' + str(by_cmc[lcmc][0].cost)
        print '\n' + by_cmc[lcmc][0].reencode()
    else:
        print 'No cards indexed by cmc?'
    print '--------------------'
    if len(by_power) > 0:
        lpower = sorted(by_power, 
                        lambda x,y: cmp(len(x), len(y)), 
                        reverse = True)[0]
        print 'Largest creature power: ' + utils.from_unary(lpower)
        print '\n' + by_power[lpower][0].reencode() + '\n'
    else: 
        print 'No cards indexed by power?'
    if len(by_toughness) > 0:
        ltoughness = sorted(by_toughness, 
                        lambda x,y: cmp(len(x), len(y)), 
                        reverse = True)[0]
        print 'Largest creature toughness: ' + utils.from_unary(ltoughness)
        print '\n' + by_toughness[ltoughness][0].reencode()
    else: 
        print 'No cards indexed by toughness?'
    print '--------------------'
    if len(by_textlines) > 0:
        llines = sorted(by_textlines, reverse = True)[0]
        print 'Most lines of text in a card: ' + str(llines)
        print '\n' + by_textlines[llines][0].reencode() + '\n'
    else: 
        print 'No cards indexed by line count?'
    if len(by_textlen) > 0:
        ltext = sorted(by_textlen, reverse = True)[0]
        print 'Most chars in a card text: ' + str(ltext)
        print '\n' + by_textlen[ltext][0].reencode()
    else: 
        print 'No cards indexed by char count?'
    print '--------------------'
    print 'There were ' + str(len(invalid_cards)) + ' invalid cards.'
    if dump_invalid:
        for card in invalid_cards:
            print '\n' + card.raw
    elif len(invalid_cards) > 0:
        print 'Not summarizing.'
    print '--------------------'
    print 'There were ' + str(len(unparsed_cards)) + ' unparsed cards.'
    if dump_invalid:
        for card in unparsed_cards:
            print '\n' + card.raw
    elif len(unparsed_cards) > 0:
        print 'Not summarizing.'
    print '===================='

def main(fname, oname = None, verbose = False):
    if verbose:
        print 'Opening encoded card file: ' + fname

    with open(fname, 'rt') as f:
        text = f.read()

    cardtexts = text.split(utils.cardsep)
    analyze(cardtexts)
    summarize()
    outliers(dump_invalid = False)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file> [output filename]'
        exit(1)
