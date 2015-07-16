import re

import utils
from cardlib import Card

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

# index management helpers
def index_size(d):
    return sum(map(lambda k: len(d[k]), d))

def inc(d, k, obj):
    if k or k == 0:
        if k in d:
            d[k] += obj
        else:
            d[k] = obj

# thanks gleemax
def plimit(s, mlen = 1000):
    if len(s) > mlen:
        return s[:1000] + '[...]'
    else:
        return s

class Datamine:
    # build the global indices
    def __init__(self, card_srcs):
        # global card pools
        self.unparsed_cards = []
        self.invalid_cards = []
        self.cards = []
        self.allcards = []
        
        # global indices
        self.by_name = {}
        self.by_type = {}
        self.by_type_inclusive = {}
        self.by_supertype = {}
        self.by_supertype_inclusive = {}
        self.by_subtype = {}
        self.by_subtype_inclusive = {}
        self.by_color = {}
        self.by_color_inclusive = {}
        self.by_color_count = {}
        self.by_cmc = {}
        self.by_cost = {}
        self.by_power = {}
        self.by_toughness = {}
        self.by_pt = {}
        self.by_loyalty = {}
        self.by_textlines = {}
        self.by_textlen = {}

        self.indices = {
            'by_name' : self.by_name,
            'by_type' : self.by_type,
            'by_type_inclusive' : self.by_type_inclusive,
            'by_supertype' : self.by_supertype,
            'by_supertype_inclusive' : self.by_supertype_inclusive,
            'by_subtype' : self.by_subtype,
            'by_subtype_inclusive' : self.by_subtype_inclusive,
            'by_color' : self.by_color,
            'by_color_inclusive' : self.by_color_inclusive,
            'by_color_count' : self.by_color_count,
            'by_cmc' : self.by_cmc,
            'by_cost' : self.by_cost,
            'by_power' : self.by_power,
            'by_toughness' : self.by_toughness,
            'by_pt' : self.by_pt,
            'by_loyalty' : self.by_loyalty,
            'by_textlines' : self.by_textlines,
            'by_textlen' : self.by_textlen,
        }

        for card_src in card_srcs:
            # the empty card is not interesting
            if not card_src:
                continue
            card = Card(card_src)
            if card.valid:
                self.cards += [card]
                self.allcards += [card]
            elif card.parsed:
                self.invalid_cards += [card]
                self.allcards += [card]
            else:
                self.unparsed_cards += [card]

            if card.parsed:
                inc(self.by_name, card.name, [card])

                inc(self.by_type, ' '.join(card.types), [card])
                for t in card.types:
                    inc(self.by_type_inclusive, t, [card])
                inc(self.by_supertype, ' '.join(card.supertypes), [card])
                for t in card.supertypes:
                    inc(self.by_supertype_inclusive, t, [card])
                inc(self.by_subtype, ' '.join(card.subtypes), [card])
                for t in card.subtypes:
                    inc(self.by_subtype_inclusive, t, [card])

                if card.cost.colors:
                    inc(self.by_color, card.cost.colors, [card])
                    for c in card.cost.colors:
                        inc(self.by_color_inclusive, c, [card])
                    inc(self.by_color_count, len(card.cost.colors), [card])
                else:
                    # colorless, still want to include in these tables
                    inc(self.by_color, 'A', [card])
                    inc(self.by_color_inclusive, 'A', [card])
                    inc(self.by_color_count, 0, [card])

                inc(self.by_cmc, card.cost.cmc, [card])
                inc(self.by_cost, card.cost.encode() if card.cost.encode() else 'none', [card])

                inc(self.by_power, card.pt_p, [card])
                inc(self.by_toughness, card.pt_t, [card])
                inc(self.by_pt, card.pt, [card])

                inc(self.by_loyalty, card.loyalty, [card])

                inc(self.by_textlines, len(card.text_lines), [card])
                inc(self.by_textlen, len(card.text.encode()), [card])

    # summarize the indices
    # Yes, this printing code is pretty terrible.
    def summarize(self, hsize = 10, vsize = 10, cmcsize = 20):
        print '===================='
        print str(len(self.cards)) + ' valid cards, ' + str(len(self.invalid_cards)) + ' invalid cards.'
        print str(len(self.allcards)) + ' cards parsed, ' + str(len(self.unparsed_cards)) + ' failed to parse'
        print '--------------------'
        print str(len(self.by_name)) + ' unique card names'
        print '--------------------'
        print (str(len(self.by_color_inclusive)) + ' represented colors (including colorless as \'A\'), ' 
               + str(len(self.by_color)) + ' combinations')
        print 'Breakdown by color:'
        rows = [self.by_color_inclusive.keys()]
        rows += [[len(self.by_color_inclusive[k]) for k in rows[0]]]
        printrows(padrows(rows))
        print 'Breakdown by number of colors:'
        rows = [self.by_color_count.keys()]
        rows += [[len(self.by_color_count[k]) for k in rows[0]]]
        printrows(padrows(rows))
        print '--------------------'
        print str(len(self.by_type_inclusive)) + ' unique card types, ' + str(len(self.by_type)) + ' combinations'
        print 'Breakdown by type:'
        d = sorted(self.by_type_inclusive, 
                   lambda x,y: cmp(len(self.by_type_inclusive[x]), len(self.by_type_inclusive[y])), 
                   reverse = True)
        rows = [[k for k in d[:hsize]]]
        rows += [[len(self.by_type_inclusive[k]) for k in rows[0]]]
        printrows(padrows(rows))
        print '--------------------'
        print (str(len(self.by_subtype_inclusive)) + ' unique subtypes, ' 
               + str(len(self.by_subtype)) + ' combinations')
        print '-- Popular subtypes: --'
        d = sorted(self.by_subtype_inclusive, 
                   lambda x,y: cmp(len(self.by_subtype_inclusive[x]), len(self.by_subtype_inclusive[y])), 
                   reverse = True)
        rows = []
        for k in d[0:vsize]:
            rows += [[k, len(self.by_subtype_inclusive[k])]]
        printrows(padrows(rows))
        print '-- Top combinations: --'
        d = sorted(self.by_subtype, 
                   lambda x,y: cmp(len(self.by_subtype[x]), len(self.by_subtype[y])), 
                   reverse = True)
        rows = []
        for k in d[0:vsize]:
            rows += [[k, len(self.by_subtype[k])]]
        printrows(padrows(rows))
        print '--------------------'
        print (str(len(self.by_supertype_inclusive)) + ' unique supertypes, ' 
               + str(len(self.by_supertype)) + ' combinations')
        print 'Breakdown by supertype:'
        d = sorted(self.by_supertype_inclusive, 
                   lambda x,y: cmp(len(self.by_supertype_inclusive[x]),len(self.by_supertype_inclusive[y])), 
                   reverse = True)
        rows = [[k for k in d[:hsize]]]
        rows += [[len(self.by_supertype_inclusive[k]) for k in rows[0]]]
        printrows(padrows(rows))
        print '--------------------'
        print str(len(self.by_cmc)) + ' different CMCs, ' + str(len(self.by_cost)) + ' unique mana costs'
        print 'Breakdown by CMC:'
        d = sorted(self.by_cmc, reverse = False)
        rows = [[k for k in d[:cmcsize]]]
        rows += [[len(self.by_cmc[k]) for k in rows[0]]]
        printrows(padrows(rows))
        print '-- Popular mana costs: --'
        d = sorted(self.by_cost, 
                   lambda x,y: cmp(len(self.by_cost[x]), len(self.by_cost[y])), 
                   reverse = True)
        rows = []
        for k in d[0:vsize]:
            rows += [[utils.from_mana(k), len(self.by_cost[k])]]
        printrows(padrows(rows))
        print '--------------------'
        print str(len(self.by_pt)) + ' unique p/t combinations'
        if len(self.by_power) > 0 and len(self.by_toughness) > 0:
            print ('Largest power: ' + str(max(map(len, self.by_power)) - 1) + 
                   ', largest toughness: ' + str(max(map(len, self.by_toughness)) - 1))
        print '-- Popular p/t values: --'
        d = sorted(self.by_pt, 
                   lambda x,y: cmp(len(self.by_pt[x]), len(self.by_pt[y])), 
                   reverse = True)
        rows = []
        for k in d[0:vsize]:
            rows += [[utils.from_unary(k), len(self.by_pt[k])]]
        printrows(padrows(rows))
        print '--------------------'
        print 'Loyalty values:'
        d = sorted(self.by_loyalty, 
                   lambda x,y: cmp(len(self.by_loyalty[x]), len(self.by_loyalty[y])), 
                   reverse = True)
        rows = []
        for k in d[0:vsize]:
            rows += [[utils.from_unary(k), len(self.by_loyalty[k])]]
        printrows(padrows(rows))
        print '--------------------'
        if len(self.by_textlen) > 0 and len(self.by_textlines) > 0:
            print('Card text ranges from ' + str(min(self.by_textlen)) + ' to ' 
                  + str(max(self.by_textlen)) + ' characters in length')
            print('Card text ranges from ' + str(min(self.by_textlines)) + ' to '
                  + str(max(self.by_textlines)) + ' lines')
        print '-- Line counts by frequency: --'
        d = sorted(self.by_textlines, 
                   lambda x,y: cmp(len(self.by_textlines[x]), len(self.by_textlines[y])), 
                   reverse = True)
        rows = []
        for k in d[0:vsize]:
            rows += [[k, len(self.by_textlines[k])]]
        printrows(padrows(rows))
        print '===================='


    # describe outliers in the indices
    def outliers(self, hsize = 10, vsize = 10, dump_invalid = False):
        print '********************'
        print 'Overview of indices:'
        rows = [['Index Name', 'Keys', 'Total Members']]
        for index in self.indices:
            rows += [[index, len(self.indices[index]), index_size(self.indices[index])]]
        printrows(padrows(rows))
        print '********************'
        if len(self.by_name) > 0:
            scardname =  sorted(self.by_name, 
                                lambda x,y: cmp(len(x), len(y)), 
                                reverse = False)[0]
            print 'Shortest Cardname: (' + str(len(scardname)) + ')'
            print '  ' + scardname
            lcardname =  sorted(self.by_name, 
                                lambda x,y: cmp(len(x), len(y)), 
                                reverse = True)[0]
            print 'Longest Cardname: (' + str(len(lcardname)) + ')'
            print '  ' + lcardname
            d = sorted(self.by_name, 
                       lambda x,y: cmp(len(self.by_name[x]), len(self.by_name[y])), 
                       reverse = True)
            rows = []
            for k in d[0:vsize]:
                if len(self.by_name[k]) > 1:
                    rows += [[k, len(self.by_name[k])]]
            if rows == []:
                print('No duplicated cardnames')
            else:
                print '-- Most duplicated names: --'
                printrows(padrows(rows))
        else:
            print 'No cards indexed by name?'
        print '--------------------'
        if len(self.by_type) > 0:
            ltypes = sorted(self.by_type, 
                            lambda x,y: cmp(len(x), len(y)), 
                            reverse = True)[0]
            print 'Longest card type: (' + str(len(ltypes)) + ')'
            print '  ' + ltypes
        else:
            print 'No cards indexed by type?'
        if len(self.by_subtype) > 0:
            lsubtypes = sorted(self.by_subtype, 
                               lambda x,y: cmp(len(x), len(y)), 
                               reverse = True)[0]
            print 'Longest subtype: (' + str(len(lsubtypes)) + ')'
            print '  ' + lsubtypes
        else:
            print 'No cards indexed by subtype?'
        if len(self.by_supertype) > 0:
            lsupertypes = sorted(self.by_supertype, 
                            lambda x,y: cmp(len(x), len(y)), 
                                 reverse = True)[0]
            print 'Longest supertype: (' + str(len(lsupertypes)) + ')'
            print '  ' + lsupertypes
        else:
            print 'No cards indexed by supertype?'
        print '--------------------'
        if len(self.by_cost) > 0:
            lcost = sorted(self.by_cost, 
                           lambda x,y: cmp(len(x), len(y)), 
                           reverse = True)[0]
            print 'Longest mana cost: (' + str(len(lcost)) + ')'
            print '  ' + utils.from_mana(lcost)
            print '\n' + plimit(self.by_cost[lcost][0].encode()) + '\n'
        else:
            print 'No cards indexed by cost?'
        if len(self.by_cmc) > 0:
            lcmc = sorted(self.by_cmc, reverse = True)[0]
            print 'Largest cmc: (' + str(lcmc) + ')'
            print '  ' + str(self.by_cmc[lcmc][0].cost)
            print '\n' + plimit(self.by_cmc[lcmc][0].encode())
        else:
            print 'No cards indexed by cmc?'
        print '--------------------'
        if len(self.by_power) > 0:
            lpower = sorted(self.by_power, 
                            lambda x,y: cmp(len(x), len(y)), 
                            reverse = True)[0]
            print 'Largest creature power: ' + utils.from_unary(lpower)
            print '\n' + plimit(self.by_power[lpower][0].encode()) + '\n'
        else: 
            print 'No cards indexed by power?'
        if len(self.by_toughness) > 0:
            ltoughness = sorted(self.by_toughness, 
                            lambda x,y: cmp(len(x), len(y)), 
                            reverse = True)[0]
            print 'Largest creature toughness: ' + utils.from_unary(ltoughness)
            print '\n' + plimit(self.by_toughness[ltoughness][0].encode())
        else: 
            print 'No cards indexed by toughness?'
        print '--------------------'
        if len(self.by_textlines) > 0:
            llines = sorted(self.by_textlines, reverse = True)[0]
            print 'Most lines of text in a card: ' + str(llines)
            print '\n' + plimit(self.by_textlines[llines][0].encode()) + '\n'
        else: 
            print 'No cards indexed by line count?'
        if len(self.by_textlen) > 0:
            ltext = sorted(self.by_textlen, reverse = True)[0]
            print 'Most chars in a card text: ' + str(ltext)
            print '\n' + plimit(self.by_textlen[ltext][0].encode())
        else: 
            print 'No cards indexed by char count?'
        print '--------------------'
        print 'There were ' + str(len(self.invalid_cards)) + ' invalid cards.'
        if dump_invalid:
            for card in self.invalid_cards:
                print '\n' + repr(card.fields)
        elif len(self.invalid_cards) > 0:
            print 'Not summarizing.'
        print '--------------------'
        print 'There were ' + str(len(self.unparsed_cards)) + ' unparsed cards.'
        if dump_invalid:
            for card in self.unparsed_cards:
                print '\n' + repr(card.fields)
        elif len(self.unparsed_cards) > 0:
            print 'Not summarizing.'
        print '===================='
