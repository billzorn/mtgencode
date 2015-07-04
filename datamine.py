import re
import codecs
import sys

# grab the characters we need out of encode
# really we should probably make a settings file with that stuff in it
import encode


# global helpers
def prettymana(s, for_forum):
    # this agorithm is pretty generic, intended fro use on Manacost.symbols keys
    if len(s) == 1:
        if for_forum:
            return '[mana]' + s + '[/mana]'
        else:
            return '{' + s + '}'
    elif len(s) == 2:
        if for_forum:
            return '[mana]{' + s[0] + '/' + s[1] + '}[/mana]'
        else:
            return '{' + s[0] + '/' + s[1] + '}'

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
    # rare ones that work the same way and interfere
    'rampage',
    'infect',
    'bushido',
    'exalted',
    'shadow',
] # there are other keywords out there, these are just easy to detect

# data aggregating classes
class Manacost:
    '''mana cost representation with data'''
    
    def get_colors(self):
        colors = ''
        for sym in self.symbols:
            if self.symbols[sym] > 0:
                symcolors = re.sub(r'2|P|S|X', '', sym)
                for symcolor in symcolors:
                    if symcolor not in colors:
                        colors += symcolor
        return colors

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
        self.symbols = {            
            'W' : 0, # single color
            'U' : 0,
            'B' : 0,
            'R' : 0,
            'G' : 0,
            'P' : 0, # colorless phyrexian
            'S' : 0, # snow
            'X' : 0, # number of x symbols
            'WP' : 0, # single color phyrexian
            'UP' : 0,
            'BP' : 0,
            'RP' : 0,
            'GP' : 0,
            '2W' : 0, # single color hybrid
            '2U' : 0,
            '2B' : 0,
            '2R' : 0,
            '2G' : 0,
            'WU' : 0, # dual color hybrid
            'WB' : 0,
            'RW' : 0,
            'GW' : 0,
            'UB' : 0,
            'UR' : 0,
            'GU' : 0,
            'BR' : 0,
            'BG' : 0,
            'RG' : 0,
        }

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

            trans_decode = {
                'WW' : 'W',
                'UU' : 'U',
                'BB' : 'B',
                'RR' : 'R',
                'GG' : 'G',
                'PP' : 'P',
                'SS' : 'S',
                'XX' : 'X',
                'WP' : 'WP',
                'UP' : 'UP',
                'BP' : 'BP',
                'RP' : 'RP',
                'GP' : 'GP',
                'VW' : '2W',
                'VU' : '2U',
                'VB' : '2B',
                'VR' : '2R',
                'VG' : '2G',
                'WU' : 'WU',
                'WB' : 'WB',
                'RW' : 'RW',
                'GW' : 'GW',
                'UB' : 'UB',
                'UR' : 'UR',
                'GU' : 'GU',
                'BR' : 'BR',
                'BG' : 'BG',
                'RG' : 'RG',
            }

            # read the symbols in a loop
            inner_current = self.inner
            while len(inner_current) > 0:
                # look for counters to get the colorless cost
                if inner_current[:1] == encode.unary_counter:
                    self.colorless += 1
                    self.cmc += 1
                    inner_current = inner_current[1:]
                # or look for symbols to read
                elif inner_current[:2] in trans_decode:
                    sym = trans_decode[inner_current[:2]]
                    self.sequence += [sym]
                    self.symbols[sym] += 1
                    if sym == 'X':
                        self.cmc += 0
                    elif sym[:1] == '2':
                        self.cmc += 2
                    else:
                        self.cmc += 1
                    inner_current = inner_current[2:]
                # if we don't recognize the symbol, bail out
                else:
                    self._valid = False
                    break

        self.colors = self.get_colors()

    def __str__(self):
        if self.colorless == 0 and self.sequence == []:
            return '{0}'
        else:
            if self.colorless > 0:
                colorless_part = '{' + str(self.colorless) + '}'
            else:
                colorless_part = ''
            return colorless_part + ''.join(map(lambda s: prettymana(s, False), self.sequence))

    def format(self, for_forum):
        if self.colorless == 0 and self.sequence == []:
            if for_forum:
                return '[mana]0[/mana]'
            else:
                return '{0}'
        else:
            if self.colorless > 0:
                if for_forum:
                    colorless_part = '[mana]{' + str(self.colorless) + '}[/mana]'
                else:
                    colorless_part = '{' + str(self.colorless) + '}'
            else:
                colorless_part = ''
            return colorless_part + ''.join(map(lambda s: prettymana(s, for_forum), self.sequence))

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

        fields = self.raw.split(encode.fieldsep)
        if not len(fields) == 10:
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
                    self.power = None
                    self.power_value = None
                    self.toughess = None
                    self.toughness_value = None
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
                self.text_lines = self.text.split(encode.newline)
                self.text_words = re.sub(punctuation_chars, ' ', self.text).split()
                self.creature_words = []
                # SUPER HACK
                if 'creature' in self.types:
                    for line in self.text_lines:
                        guess = []
                        for keyword in creature_keywords:
                            if keyword in line:
                                guess += [keyword]
                                line = line.replace(keyword, '')
                        if re.sub(punctuation_chars, ' ', line).split() == [] or 'protect' in line:
                            for word in guess:
                                if word not in self.creature_words:
                                    self.creature_words += [word]
            else:
                self.text = None
                self.text_lines = []
                self.text_words = []
                self.creature_words = []

    def __str__(self):
        return ''.join([
            encode.fieldsep,
            self.name,
            encode.fieldsep,
            (' ' + encode.dash_marker + ' ').join([' '.join(self.supertypes + self.types),
                                                   ' '.join(self.subtypes)]),
            encode.fieldsep,
            str(self.cost.cmc) if self.cost.colors == '' 
            else str(self.cost.cmc) + ', ' + self.cost.colors,
            encode.fieldsep,
        ])


def main(fname, oname = None, verbose = False):
    if verbose:
        print 'Opening encoded card file: ' + fname

    f = open(fname, 'r')
    text = f.read()
    f.close()

    # we get rid of the first and last because they are probably partial
    cardtexts = text.split('\n\n')[1:-1]
    cards = []

    creatures = 0
    cwords = 0
    allwords = {}

    mcolor = 'G'

    i = 0
    for cardtext in cardtexts:
        i += 1
        card = Card(cardtext)
        if not (card._parsed and card._valid):
            print card.raw
            continue
        cards += [card]

        if 'creature' in card.types:
            creatures += 1
        if card.creature_words:
            cwords += 1

        if card.cost.check_colors(mcolor):
            print ' '.join(card.text_words)

        for word in card.text_words:
            if word in allwords:
                allwords[word] += 1
            else:
                allwords[word] = 1
            

    # print str(creatures) + ' creatures, ' + str(cwords) + ' with keywords'
    # print str(len(allwords)) + ' unique words in card text'
    # i = 0
    # for word in sorted(allwords, key=allwords.get, reverse=True):
    #     i += 1
    #     if i > 0:
    #         break
    #     print word + ': ' + str(allwords[word])
    

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file> [output filename]'
        exit(1)

