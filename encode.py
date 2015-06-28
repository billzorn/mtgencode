import jdecode
import re
import codecs

#badwords = []

valid_encoded_char = r'[abcdefghijklmnopqrstuvwxyz\'+\-*",.:;WUBRGPV/XTQ|\\&^\{\}@ \n=~#]'

dash_marker = '~'
bullet_marker = '='
reserved_indicator = '\r'

def to_ascii(s):
    s = s.replace(u'\u2014', dash_marker) # unicode long dash
    s = s.replace(u'\u2022', bullet_marker) # unicode bullet
    s = s.replace(u'\u2019', '"') # single quote
    s = s.replace(u'\u2018', '"') # single quote
    s = s.replace(u'\u2212', '-') # minus sign
    s = s.replace(u'\xe6', 'ae') # ae symbol
    s = s.replace(u'\xfb', 'u') # u with caret
    s = s.replace(u'\xfa', 'u') # u with accent
    s = s.replace(u'\xe9', 'e') # e with accent
    s = s.replace(u'\xe1', 'a') # a with accent
    s = s.replace(u'\xe0', 'a') # a with accent going the other way
    s = s.replace(u'\xe2', 'a') # a with caret
    s = s.replace(u'\xf6', 'o') # o with umlaut
    s = s.replace(u'\xed', 'i') # i with accent
    return s

# This whole things assumes the json format of mtgjson.com.

# Here's a brief list of relevant fields:
# name - string
# names - list (used for split, flip, and double-faced)
# manaCost - string
# cmc - number
# colors - list
# type - string (the whole big long damn thing)
# supertypes - list
# types - list
# subtypes - list
# text - string
# power - string
# toughness - string
# loyalty - number

# And some less useful ones, in case they're wanted for something:
# layout - string
# rarity - string
# flavor - string
# artis - string
# number - string
# multiverseid - number
# variations - list
# imageName - string
# watermark - string
# border - string
# timeshifted - boolean
# hand - number
# life - number
# reserved - boolean
# releaseDate - string
# starter - boolean

fieldsep = '|'
newline = '\\'
unary_marker = '&'
unary_counter = '^'
mana_open_delimiter = '{'
mana_close_delimiter = '}'
x_marker = 'X'
tap_marker = 'T'
untap_marker = 'Q'
this_marker = '@'
counter_marker = '#'
bsidesep = '\n'

unary_max = 30

def to_unary(s):
    numbers = re.findall(r'[0123456789]+', s)
    for n in sorted(numbers, cmp = lambda x,y: cmp(int(x), int(y)) * -1):
        i = int(n)
        if i == 40:
            s = s.replace(n, 'forty')
        elif i == 50:
            s = s.replace(n, 'fifty')
        elif i == 100:
            s = s.replace(n, 'one hundred')
        elif i == 200:
            s = s.replace(n, 'two hundred')
        else:
            if i > unary_max:
                i = unary_max
                print s
            s = s.replace(n, unary_marker + unary_counter * i)

    return s


# also handles the tap and untap symbols
def compress_mana(manastring):
    # mana string is of the form '{3}{W}{2/B}', as specified by mtgjson
    translations = {
        '{w}' : 'WW',
        '{u}' : 'UU',
        '{b}' : 'BB',
        '{r}' : 'RR',
        '{g}' : 'GG',
        '{p}' : 'PP',
        '{w/p}' : 'WP',
        '{u/p}' : 'UP',
        '{b/p}' : 'BP',
        '{r/p}' : 'RP',
        '{g/p}' : 'GP',
        '{2/w}' : 'VW',
        '{2/u}' : 'VU',
        '{2/b}' : 'VB',
        '{2/r}' : 'VR',
        '{2/g}' : 'VG',
        '{w/u}' : 'WU',
        '{w/b}' : 'WB',
        '{r/w}' : 'RW',
        '{g/w}' : 'GW',
        '{u/b}' : 'UB',
        '{u/r}' : 'UR',
        '{g/u}' : 'GU',
        '{b/r}' : 'BR',
        '{b/g}' : 'BG',
        '{r/g}' : 'RG',
        '{s}' : 'SS',
        '{x}' : x_marker * 2,
        #'{xx}' : x_marker * 4,
        #'{xxx}' : x_marker * 6,
        '{t}' : tap_marker,
        '{q}' : untap_marker,
    }
    for t in translations:
        manastring = manastring.replace(t, translations[t])

    numbers = re.findall(r'\{[0123456789]+\}', manastring)
    for n in numbers:
        i = int(re.findall(r'[0123456789]+', n)[0])
        manastring = manastring.replace(n, unary_counter * i)
        
    # we don't really need delimiters for tap, it's a unique symbol anyways
    if manastring in [tap_marker, untap_marker]:
        return manastring
    else:
        return '{' + manastring + '}'

def replace_mana(s):
    manastrings = re.findall(r'\{[\{\}wubrgp/xtq0123456789]+\}', s)
    for manastring in manastrings:
        s = s.replace(manastring, compress_mana(manastring))
    return s
    

def strip_reminder_text(s):
    return re.sub(r'\(.*\)', '', s)
    
def replace_newlines(s):
    return s.replace('\n', '\\')


def replace_cardname(s, name):
    # here are some fun edge cases, thanks to jml34 on the forum for 
    # pointing them out
    if name == 'sacrifice':
        s = s.replace(name, this_marker, 1)
        return s
    elif name == 'fear':
        return s

    s = s.replace(name, this_marker)
    
    # so, some legends don't use the full cardname in their text box...
    # this check finds about 400 of them
    nameparts = name.split(',')
    if len(nameparts) > 1:
        mininame = nameparts[0]
        new_s = s.replace(mininame, this_marker)
        if not new_s == s:
            s = new_s
            # on first inspection, the replacements all look good
            # print '------------------'
            # print name
            # print '----'
            # print s
        
    # a few others don't have a convenient comma to detect their nicknames,
    # so we override them here
    overrides = [
        # detectable by splitting on 'the', though that might cause other issues
        'crovax',
        'rashka',
        'phage',
        'shimatsu',
        # random and arbitrary: they have a last name, 1996 world champion, etc.
        'world champion',
        'axelrod',
        'hazezon',
        'rubinia',
        'rasputin',
        'hivis',
    ]
    
    for override in overrides:
        s = s.replace(override, this_marker)

    # some detection code when the overrides need to be fixed...
    # global badwords
    # bad = False
    # for word in name.replace(',', '').split():
    #     if word in s and not word in badwords:
    #             badwords += [word]
    return s


def sanitize_name(s):
    s = s.replace('!', '')
    s = s.replace('?', '')
    s = s.replace('-', dash_marker)
    s = s.replace('100,000', 'one hundred thousand')
    s = s.replace('1,000', 'one thousand')
    s = s.replace('1996', 'nineteen ninety-six')
    return s


# call this before replacing newlines
# this one ends up being really bad because of the confusion
# with 'counter target spell or ability'
def replace_counters(s):
    #so, big fat old dictionary time!!!!!!!!!
    allcounters = [
        'time counter',
        'devotion counter',
        'charge counter',
        'ki counter',
        'matrix counter',
        'spore counter',
        'poison counter',
        'quest counter',
        'hatchling counter',
        'storage counter',
        'growth counter',
        'paralyzation counter',
        'energy counter',
        'study counter',
        'glyph counter',
        'depletion counter',
        'sleight counter',
        'loyalty counter',
        'hoofprint counter',
        'wage counter',
        'echo counter',
        'lore counter',
        'page counter',
        'divinity counter',
        'mannequin counter',
        'ice counter',
        'fade counter',
        'pain counter',
        #'age counter',
        'gold counter',
        'muster counter',
        'infection counter',
        'plague counter',
        'fate counter',
        'slime counter',
        'shell counter',
        'credit counter',
        'despair counter',
        'globe counter',
        'currency counter',
        'blood counter',
        'soot counter',
        'carrion counter',
        'fuse counter',
        'filibuster counter',
        'wind counter',
        'hourglass counter',
        'trap counter',
        'corpse counter',
        'awakening counter',
        'verse counter',
        'scream counter',
        'doom counter',
        'luck counter',
        'intervention counter',
        'eyeball counter',
        'flood counter',
        'eon counter',
        'death counter',
        'delay counter',
        'blaze counter',
        'magnet counter',
        'feather counter',
        'shield counter',
        'wish counter',
        'petal counter',
        'music counter',
        'pressure counter',
        'manifestation counter',
        #'net counter',
        'velocity counter',
        'vitality counter',
        'treasure counter',
        'pin counter',
        'bounty counter',
        'rust counter',
        'mire counter',
        'tower counter',
        #'ore counter',
        'cube counter',
        'strife counter',
        'elixir counter',
        'hunger counter',
        'level counter',
        'winch counter',
        'fungus counter',
        'training counter',
        'theft counter',
        'arrowhead counter',
        'sleep counter',
        'healing counter',
        'mining counter',
        'dream counter',
        'aim counter',
        'arrow counter',
        'javelin counter',
        'gem counter',
        'bribery counter',
        'mine counter',
        'omen counter',
        'phylactery counter',
        'tide counter',
        'polyp counter',
        'petrification counter',
        'shred counter',
        'pupa counter',
    ]
    usedcounters = []
    for countername in allcounters:
        if countername in s:
            usedcounters += [countername]
            s = s.replace(countername, counter_marker + ' counter')
    
    # oh god some of the counter names are suffixes of others...
    shortcounters = [
        'age counter',
        'net counter',
        'ore counter',
    ]
    for countername in shortcounters:
        # SUPER HACKY fix for doubling season
        if countername in s and 'more counter' not in s:
            usedcounters += [countername]
            s = s.replace(countername, counter_marker + ' counter')
    
    # miraculously this doesn't seem to happen
    # if len(usedcounters) > 1:
    #     print usedcounters

    # we haven't done newline replacement yet, so use actual newlines
    if len(usedcounters) == 1:
        # and yeah, this line of code can blow up in all kinds of different ways
        s = 'countertype ' + counter_marker + ' ' + usedcounters[0].split()[0] + '\n' + s

    # random code for finding out all the counter names
    # global badwords
    # countertypes = re.findall(r'[| ][^ ]+ counter', s)
    # for countertype in countertypes:
    #     minicounter = countertype[1:]
    #     if not minicounter in badwords:
    #         badwords += [minicounter]
    return s


# run only after doing unary conversion
def fix_dashes(s):
    s = s.replace('-' + unary_marker, reserved_indicator)
    s = s.replace('-', dash_marker)
    s = s.replace(reserved_indicator, '-' + unary_marker)
    
    # level up is annoying
    levels = re.findall(r'level &\^*\-&', s)
    for level in levels:
        newlevel = level.replace('-', dash_marker)
        s = s.replace(level, newlevel)

    levels = re.findall(r'level &\^*\+', s)
    for level in levels:
        newlevel = level.replace('+', dash_marker)
        s = s.replace(level, newlevel)

    # and we still have the ~x issue

    return s


# run this after fixing dashes, because this unbreaks the ~x issue
# also probably don't run this on names, there are a few names with x~ in them.
def fix_x(s):
    s = s.replace(dash_marker + 'x', '-' + x_marker)
    s = s.replace('+x', '+' + x_marker)
    s = s.replace(' x ', ' ' + x_marker + ' ')
    s = s.replace('x:', x_marker + ':')
    s = s.replace('x~', x_marker + '~')
    s = s.replace('x.', x_marker + '.')
    s = s.replace('x,', x_marker + ',')
    s = s.replace('x/x', x_marker + '/' + x_marker)
    return s


# do before removing newlines
# might as well do this after countertype because we probably care more about
# the location of the equip cost
def relocate_equip(s):
    equips = re.findall(r'equip \{[WUBRGPV/XTQ&^]*\}.?$', s)
    # there don't seem to be any cases with more than one
    if len(equips) == 1:
        equip = equips[0]
        s = s.replace('\n' + equip, '')
        s = s.replace(equip, '')

        if equip[-1:] == ' ':
            equip = equip[0:-1]

        if s == '':
            s = equip
        else:
            s = equip + '\n' + s
        
    return s


def encode(card):
    # filter out vanguard cards
    if card['layout'] in ['token', 'plane', 'scheme', 'phenomenon', 'vanguard']:
        return

    encoding = fieldsep
    name = card['name'].lower()
    encoding += sanitize_name(name)
    encoding += fieldsep
    if 'supertypes' in card:
        encoding += ' '.join(card['supertypes']).lower()
    encoding += fieldsep
    encoding += ' '.join(card['types']).lower()
    encoding += fieldsep
    if 'loyalty' in card:
        encoding += to_unary(str(card['loyalty']))
    encoding += fieldsep
    if 'subtypes' in card:
        encoding += ' '.join(card['subtypes']).lower()
    encoding += fieldsep
    if 'power' in card and 'toughness' in card:
        encoding += to_unary(card['power']) + '/' + to_unary(card['toughness'])        
    encoding += fieldsep
    if 'manaCost' in card:
        encoding += replace_mana(card['manaCost'].lower())
    encoding += fieldsep
    if 'text' in card:
        text = card['text'].lower()
        text = strip_reminder_text(text)
        text = replace_cardname(text, name)
        text = replace_mana(text)
        text = to_unary(text)
        text = fix_dashes(text)
        text = fix_x(text)
        text = replace_counters(text)
        text = relocate_equip(text)
        text = replace_newlines(text)
        encoding += text
    encoding += fieldsep
    # if 'flavor' in card:
    #     encoding += card['flavor'].lower()
    # encoding += fieldsep

    # now output the bside if there is one
    if 'bside' in card:
        encoding += bsidesep
        encoding += encode(card['bside'])
    
    encoding = to_ascii(encoding)
    # encoding = re.sub(valid_encoded_char, '', encoding)
    # if not encoding == '':
    #     print card
    return encoding
    
def encode_duplicated(cards):
    # Boring solution: only write out the first one...
    return encode(cards[0])


def main(fname, oname = None, verbose = True):
    if verbose:
        print 'Opening json file: ' + fname

    allcards = jdecode.mtg_open_json(fname, verbose)

    if not oname == None:
        if verbose:
            print 'Writing output to: ' + oname
        ofile = codecs.open(oname, 'w', 'utf-8')

    for card in allcards:
        val = encode_duplicated(allcards[card])
        if not (val == None or val == ''):
            if oname == None:
                print val + '\n'
            else:
                ofile.write(val + '\n\n')
        
    # print len(badwords)
    # for word in badwords:
    #     print word

    if not oname == None:
        ofile.close()

    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<JSON file> [output filename]'
        exit(1)

