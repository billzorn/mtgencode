# representation for mana costs and text with embedded mana costs
# data aggregating classes
import re
import random

import utils

class Manacost:
    '''mana cost representation with data'''
    
    # hardcoded to be dependent on the symbol structure... ah well
    def get_colors(self):
        colors = ''
        for sym in self.symbols:
            if self.symbols[sym] > 0:
                symcolors = re.sub(r'2|P|S|X|C', '', sym)
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

    def __init__(self, src, fmt = ''):
        # source fields, exactly one will be set
        self.raw = None
        self.json = None
        # flags
        self.parsed = True
        self.valid = True
        self.none = False
        # default values for all fields
        self.inner = None
        self.cmc = 0
        self.colorless = 0
        self.sequence = []
        self.symbols = {sym : 0 for sym in utils.mana_syms}
        self.allsymbols = {sym : 0 for sym in utils.mana_symall}
        self.colors = ''

        if fmt == 'json':
            self.json = src
            text = utils.mana_translate(self.json.upper())
        else:
            self.raw = src
            text = self.raw

        if text == '':
            self.inner = ''
            self.none = True

        elif not (len(text) >= 2 and text[0] == '{' and text[-1] == '}'):
            self.parsed = False
            self.valid = False

        else:
            self.inner = text[1:-1]

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
                        self.valid = False

        self.colors = self.get_colors()

    def __str__(self):
        if self.none:
            return '_NOCOST_'
        return utils.mana_untranslate(utils.mana_open_delimiter + ''.join(self.sequence)
                                      + utils.mana_close_delimiter)

    def format(self, for_forum = False, for_html = False):
        if self.none:
            return '_NOCOST_'
        
        else:
            return utils.mana_untranslate(utils.mana_open_delimiter + ''.join(self.sequence)
                                          + utils.mana_close_delimiter, for_forum, for_html)

    def encode(self, randomize = False):
        if self.none:
            return ''
        elif randomize:
            # so this won't work very well if mana_unary_marker isn't empty
            return (utils.mana_open_delimiter 
                    + ''.join(random.sample(self.sequence, len(self.sequence)))
                    + utils.mana_close_delimiter)
        else:
            return utils.mana_open_delimiter + ''.join(self.sequence) + utils.mana_close_delimiter

    def vectorize(self, delimit = False):
        if self.none:
            return ''
        elif delimit:
            ld = '('
            rd = ')'
        else:
            ld = ''
            rd = ''
        return ' '.join(map(lambda s: ld + s + rd, sorted(self.sequence)))
        

class Manatext:
    '''text representation with embedded mana costs'''
    
    def __init__(self, src, fmt = ''):
        # source fields
        self.raw = None
        self.json = None
        # flags
        self.valid = True
        # default values for all fields
        self.text = src
        self.costs = []
        
        if fmt == 'json':
            self.json = src
            manastrs = re.findall(utils.mana_json_regex, src)
        else:
            self.raw = src
            manastrs = re.findall(utils.mana_regex, src)
            
        for manastr in manastrs:
            cost = Manacost(manastr, fmt)
            if not cost.valid:
                self.valid = False
            self.costs += [cost]
            self.text = self.text.replace(manastr, utils.reserved_mana_marker, 1)

        if (utils.mana_open_delimiter in self.text 
            or utils.mana_close_delimiter in self.text
            or utils.mana_json_open_delimiter in self.text 
            or utils.mana_json_close_delimiter in self.text):
            self.valid = False

    def __str__(self):
        text = self.text
        for cost in self.costs:
            text = text.replace(utils.reserved_mana_marker, str(cost), 1)
        return text

    def format(self, for_forum = False, for_html = False):
        text = self.text
        for cost in self.costs:
            text = text.replace(utils.reserved_mana_marker, cost.format(for_forum=for_forum, for_html=for_html), 1)
        if for_html:
            text = text.replace('\n', '<br>\n')
        return text

    def encode(self, randomize = False):
        text = self.text
        for cost in self.costs:
            text = text.replace(utils.reserved_mana_marker, cost.encode(randomize = randomize), 1)
        return text

    def vectorize(self):
        text = self.text
        special_chars = [utils.reserved_mana_marker,
                         utils.dash_marker,
                         utils.bullet_marker,
                         utils.this_marker,
                         utils.counter_marker,
                         utils.choice_open_delimiter,
                         utils.choice_close_delimiter,
                         utils.newline,
                         #utils.x_marker,
                         utils.tap_marker,
                         utils.untap_marker,
                         utils.newline,
                         ';', ':', '"', ',', '.']
        for char in special_chars:
            text = text.replace(char, ' ' + char + ' ')
        text = text.replace('/', '/ /')
        for cost in self.costs:
            text = text.replace(utils.reserved_mana_marker, cost.vectorize(), 1)
        return ' '.join(text.split())
