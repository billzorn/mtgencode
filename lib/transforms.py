# transform passes used to encode / decode cards
import re

# These could probably use a little love... They tend to hardcode in lots
# of things very specific to the mtgjson format.

import utils

cardsep = utils.cardsep
fieldsep = utils.fieldsep
bsidesep = utils.bsidesep
newline = utils.newline
dash_marker = utils.dash_marker
bullet_marker = utils.bullet_marker
this_marker = utils.this_marker
counter_marker = utils.counter_marker
reserved_marker = utils.reserved_marker
choice_open_delimiter = utils.choice_open_delimiter
choice_close_delimiter = utils.choice_close_delimiter
x_marker = utils.x_marker
tap_marker = utils.tap_marker
untap_marker = utils.untap_marker
counter_rename = utils.counter_rename
unary_marker = utils.unary_marker
unary_counter = utils.unary_counter


# Name Passes.


def name_pass_1_sanitize(s):
    s = s.replace('!', '')
    s = s.replace('?', '')
    s = s.replace('-', dash_marker)
    s = s.replace('100,000', 'one hundred thousand')
    s = s.replace('1,000', 'one thousand')
    s = s.replace('1996', 'nineteen ninety-six')
    return s


# Name unpasses.


# particularly helpful if you want to call text_unpass_8_unicode later
# and NOT have it stick unicode long dashes into names.
def name_unpass_1_dashes(s):
    return s.replace(dash_marker, '-')


# Text Passes.


def text_pass_1_strip_rt(s):
    return re.sub(r'\(.*\)', '', s)


def text_pass_2_cardname(s, name):
    # Here are some fun edge cases, thanks to jml34 on the forum for 
    # pointing them out.
    if name == 'sacrifice':
        s = s.replace(name, this_marker, 1)
        return s
    elif name == 'fear':
        return s

    s = s.replace(name, this_marker)
    
    # So, some legends don't use the full cardname in their text box...
    # this check finds about 400 of them.
    nameparts = name.split(',')
    if len(nameparts) > 1:
        mininame = nameparts[0]
        new_s = s.replace(mininame, this_marker)
        if not new_s == s:
            s = new_s
        
    # A few others don't have a convenient comma to detect their nicknames,
    # so we override them here.
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

    return s


def text_pass_3_unary(s):
    return utils.to_unary(s)


# Run only after doing unary conversion.
def text_pass_4a_dashes(s):
    s = s.replace('-' + unary_marker, reserved_marker)
    s = s.replace('-', dash_marker)
    s = s.replace(reserved_marker, '-' + unary_marker)
    
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


# Run this after fixing dashes, because this unbreaks the ~x issue.
# Also probably don't run this on names, there are a few names with x~ in them.
def text_pass_4b_x(s):
    s = s.replace(dash_marker + 'x', '-' + x_marker)
    s = s.replace('+x', '+' + x_marker)
    s = s.replace(' x ', ' ' + x_marker + ' ')
    s = s.replace('x:', x_marker + ':')
    s = s.replace('x~', x_marker + '~')
    s = s.replace(u'x\u2014', x_marker + u'\u2014')
    s = s.replace('x.', x_marker + '.')
    s = s.replace('x,', x_marker + ',')
    s = s.replace('x/x', x_marker + '/' + x_marker)
    return s


# Call this before replacing newlines.
# This one ends up being really bad because of the confusion
# with 'counter target spell or ability'.
def text_pass_5_counters(s):
    # so, big fat old dictionary time!!!!!!!!!
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

    return s


# The word 'counter' is confusing when used to refer to what we do to spells
# and sometimes abilities to make them not happen. Let's rename that.
# Call this after doing the counter replacement to simplify the regexes.
counter_rename = 'uncast'
def text_pass_6_uncast(s):
    # pre-checks to make sure we aren't doing anything dumb
    # if '% counter target ' in s or '^ counter target ' in s or '& counter target ' in s:
    #     print s + '\n'
    # if '% counter a ' in s or '^ counter a ' in s or '& counter a ' in s:
    #     print s + '\n'
    # if '% counter all ' in s or '^ counter all ' in s or '& counter all ' in s:
    #     print s + '\n'
    # if '% counter a ' in s or '^ counter a ' in s or '& counter a ' in s:
    #     print s + '\n'
    # if '% counter that ' in s or '^ counter that ' in s or '& counter that ' in s:
    #     print s + '\n'
    # if '% counter @' in s or '^ counter @' in s or '& counter @' in s:
    #     print s + '\n'
    # if '% counter the ' in s or '^ counter the ' in s or '& counter the ' in s:
    #     print s + '\n'

    # counter target
    s = s.replace('counter target ', counter_rename + ' target ')
    # counter a
    s = s.replace('counter a ', counter_rename + ' a ')
    # counter all
    s = s.replace('counter all ', counter_rename + ' all ')
    # counters a
    s = s.replace('counters a ', counter_rename + 's a ')
    # countered (this could get weird in terms of englishing the word; lets just go for hilarious)
    s = s.replace('countered', counter_rename + 'ed')
    # counter that
    s = s.replace('counter that ', counter_rename + ' that ')
    # counter @
    s = s.replace('counter @', counter_rename + ' @')
    # counter it (this is tricky
    s = s.replace(', counter it', ', ' + counter_rename + ' it')
    # counter the (it happens at least once, thanks wizards!)
    s = s.replace('counter the ', counter_rename + ' the ')
    # counter up to
    s = s.replace('counter up to ', counter_rename + ' up to ')

    # check if the word exists in any other context
    # if 'counter' in (s.replace('% counter', '').replace('countertype', '')
    #                  .replace('^ counter', '').replace('& counter', ''):
    #     print s + '\n'

    # whew! by manual inspection of a few dozen texts, it looks like this about covers it.
    return s    
    

# Run after fixing dashes, it makes the regexes better, but before replacing newlines.
def text_pass_7_choice(s):
    # the idea is to take 'choose n ~\n=ability\n=ability\n'
    # to '[n = ability = ability]\n'
    
    def choice_formatting_helper(s_helper, prefix, count):
        single_choices = re.findall(ur'(' + prefix + ur'\n?(\u2022.*(\n|$))+)', s_helper)
        for choice in single_choices:
            newchoice = choice[0]
            newchoice = newchoice.replace(prefix, unary_marker + (unary_counter * count))
            newchoice = newchoice.replace('\n', ' ')
            if newchoice[-1:] == ' ':
                newchoice = choice_open_delimiter + newchoice[:-1] + choice_close_delimiter + '\n'
            else:
                newchoice = choice_open_delimiter + newchoice + choice_close_delimiter
            s_helper = s_helper.replace(choice[0], newchoice)
        return s_helper

    s = choice_formatting_helper(s, ur'choose one \u2014', 1)
    s = choice_formatting_helper(s, ur'choose one \u2014 ', 1) # ty Promise of Power
    s = choice_formatting_helper(s, ur'choose two \u2014', 2)
    s = choice_formatting_helper(s, ur'choose two \u2014 ', 2) # ty Profane Command
    s = choice_formatting_helper(s, ur'choose one or both \u2014', 0)
    s = choice_formatting_helper(s, ur'choose one or more \u2014', 0)
    s = choice_formatting_helper(s, ur'choose khans or dragons.', 1)
    # this is for 'an opponent chooses one', which will be a bit weird but still work out
    s = choice_formatting_helper(s, ur'chooses one \u2014', 1)

    return s


# do before removing newlines
# might as well do this after countertype because we probably care more about
# the location of the equip cost
def text_pass_8_equip(s):
    equips = re.findall(r'equip ' + utils.mana_json_regex + r'.?$', s)
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

    nonmana = re.findall(ur'(equip\u2014.*(\n|$))', s)
    if len(nonmana) == 1:
        equip = nonmana[0][0]
        s = s.replace('\n' + equip, '')
        s = s.replace(equip, '')
        
        if equip[-1:] == ' ':
            equip = equip[0:-1]

        if s == '':
            s = equip
        else:
            s = equip + '\n' + s
        
    return s


def text_pass_9_newlines(s):
    return s.replace('\n', '\\')


def text_pass_10_symbols(s):
    return utils.to_symbols(s)


# Text unpasses, for decoding. All assume the text inside a Manatext, so don't do anything
# weird with the mana cost symbol.


def text_unpass_1_choice(s, delimit = False):
    choice_regex = (re.escape(choice_open_delimiter) + re.escape(unary_marker)
                    + r'.*' + re.escape(bullet_marker) + r'.*' + re.escape(choice_close_delimiter))
    choices = re.findall(choice_regex, s)
    for choice in sorted(choices, lambda x,y: cmp(len(x), len(y)), reverse = True):
        fragments = choice[1:-1].split(bullet_marker)
        countfrag = fragments[0]
        optfrags = fragments[1:]
        choicecount = int(utils.from_unary(re.findall(utils.number_unary_regex, countfrag)[0]))
        newchoice = ''

        if choicecount == 0:
            if len(countfrag) == 2:
                newchoice += 'choose one or both '
            else:
                newchoice += 'choose one or more '
        elif choicecount == 1:
            newchoice += 'choose one '
        elif choicecount == 2:
            newchoice += 'choose two '
        else:
            newchoice += 'choose ' + utils.to_unary(str(choicecount)) + ' '
        newchoice += dash_marker
        
        for option in optfrags:
            option = option.strip()
            if option:
                newchoice += newline + bullet_marker + ' ' + option

        if delimit:
            s = s.replace(choice, choice_open_delimiter + newchoice + choice_close_delimiter)
            s = s.replace('an opponent ' + choice_open_delimiter + 'choose ', 
                          'an opponent ' + choice_open_delimiter + 'chooses ')
        else:
            s = s.replace(choice, newchoice)
            s = s.replace('an opponent choose ', 'an opponent chooses ')
    
    return s


def text_unpass_2_counters(s):
    countertypes = re.findall(r'countertype ' + re.escape(counter_marker) 
                              + r'[^' + re.escape(newline) + r']*' + re.escape(newline), s)
    # lazier than using groups in the regex
    countertypes += re.findall(r'countertype ' + re.escape(counter_marker) 
                              + r'[^' + re.escape(newline) + r']*$', s)
    if len(countertypes) > 0:
        countertype = countertypes[0].replace('countertype ' + counter_marker, '')
        countertype = countertype.replace(newline, '\n').strip()
        s = s.replace(countertypes[0], '')
        s = s.replace(counter_marker, countertype)
    
    return s


def text_unpass_3_uncast(s):
    return s.replace(counter_rename, 'counter')


def text_unpass_4_unary(s):
    return utils.from_unary(s)


def text_unpass_5_symbols(s, for_forum):
    return utils.from_symbols(s, for_forum = for_forum)


def text_unpass_6_cardname(s, name):
    return s.replace(this_marker, name)


def text_unpass_7_newlines(s):
    return s.replace(newline, '\n')


def text_unpass_8_unicode(s):
    s = s.replace(dash_marker, u'\u2014')
    s = s.replace(bullet_marker, u'\u2022')
    return s
