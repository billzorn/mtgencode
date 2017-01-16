import json

import utils
import cardlib

def mtg_open_json(fname, verbose = False):

    with open(fname, 'r') as f:
        jobj = json.load(f)
    
    allcards = {}
    asides = {}
    bsides = {}

    for k_set in jobj:
        set = jobj[k_set]
        setname = set['name']
        if 'magicCardsInfoCode' in set:
            codename = set['magicCardsInfoCode']
        else:
            codename = ''
        
        for card in set['cards']:
            card[utils.json_field_set_name] = setname
            card[utils.json_field_info_code] = codename

            cardnumber = None
            if 'number' in card:
                cardnumber = card['number']
            # the lower avoids duplication of at least one card (Will-o/O'-the-Wisp)
            cardname = card['name'].lower()

            uid = set['code']
            if cardnumber == None:
                uid = uid + '_' + cardname + '_'
            else:
                uid = uid + '_' + cardnumber

            # aggregate by name to avoid duplicates, not counting bsides
            if not uid[-1] == 'b':
                if cardname in allcards:
                    allcards[cardname] += [card]
                else:
                    allcards[cardname] = [card]
                    
            # also aggregate aside cards by uid so we can add bsides later
            if uid[-1:] == 'a':
                asides[uid] = card
            if uid[-1:] == 'b':
                bsides[uid] = card

    for uid in bsides:
        aside_uid = uid[:-1] + 'a'
        if aside_uid in asides:
            # the second check handles the brothers yamazaki edge case
            if not asides[aside_uid]['name'] == bsides[uid]['name']:
                asides[aside_uid][utils.json_field_bside] = bsides[uid]
        else:
            pass
            # this exposes some coldsnap theme deck bsides that aren't
            # really bsides; shouldn't matter too much
            #print aside_uid
            #print bsides[uid]

    if verbose:
        print 'Opened ' + str(len(allcards)) + ' uniquely named cards.'
    return allcards

# filters to ignore some undesirable cards, only used when opening json
def default_exclude_sets(cardset):
    return cardset == 'Unglued' or cardset == 'Unhinged' or cardset == 'Celebration'

def default_exclude_types(cardtype):
    return cardtype in ['conspiracy']

def default_exclude_layouts(layout):
    return layout in ['token', 'plane', 'scheme', 'phenomenon', 'vanguard']

# centralized logic for opening files of cards, either encoded or json
def mtg_open_file(fname, verbose = False,
                  linetrans = True, fmt_ordered = cardlib.fmt_ordered_default,
                  exclude_sets = default_exclude_sets,
                  exclude_types = default_exclude_types,
                  exclude_layouts = default_exclude_layouts):

    cards = []
    valid = 0
    skipped = 0
    invalid = 0
    unparsed = 0

    if fname[-5:] == '.json':
        if verbose:
            print 'This looks like a json file: ' + fname
        json_srcs = mtg_open_json(fname, verbose)
        # sorted for stability
        for json_cardname in sorted(json_srcs):
            if len(json_srcs[json_cardname]) > 0:
                jcards = json_srcs[json_cardname]

                # look for a normal rarity version, in a set we can use
                idx = 0
                card = cardlib.Card(jcards[idx], linetrans=linetrans)
                while (idx < len(jcards)
                       and (card.rarity == utils.rarity_special_marker
                            or exclude_sets(jcards[idx][utils.json_field_set_name]))):
                    idx += 1
                    if idx < len(jcards):
                        card = cardlib.Card(jcards[idx], linetrans=linetrans)
                # if there isn't one, settle with index 0
                if idx >= len(jcards):
                    idx = 0
                    card = cardlib.Card(jcards[idx], linetrans=linetrans)
                # we could go back and look for a card satisfying one of the criteria,
                # but eh

                skip = False
                if (exclude_sets(jcards[idx][utils.json_field_set_name])
                    or exclude_layouts(jcards[idx]['layout'])):
                    skip = True
                for cardtype in card.types:
                    if exclude_types(cardtype):
                        skip = True
                if skip:
                    skipped += 1
                    continue

                if card.valid:
                    valid += 1
                    cards += [card]
                elif card.parsed:
                    invalid += 1
                    if verbose:
		        print 'Invalid card: ' + json_cardname
                else:
                    unparsed += 1

    # fall back to opening a normal encoded file
    else:
        if verbose:
            print 'Opening encoded card file: ' + fname
        with open(fname, 'rt') as f:
            text = f.read()
        for card_src in text.split(utils.cardsep):
            if card_src:
                card = cardlib.Card(card_src, fmt_ordered=fmt_ordered)
                # unlike opening from json, we still want to return invalid cards
                cards += [card]
                if card.valid:
                    valid += 1
                elif card.parsed:
                    invalid += 1
                    if verbose:
		        print 'Invalid card: ' + json_cardname
                else:
                    unparsed += 1

    if verbose:
        print (str(valid) + ' valid, ' + str(skipped) + ' skipped, '
               + str(invalid) + ' invalid, ' + str(unparsed) + ' failed to parse.')

    good_count = 0
    bad_count = 0
    for card in cards:
        if not card.parsed and not card.text.text:
            bad_count += 1
        elif len(card.name) > 50 or len(card.rarity) > 3:
            bad_count += 1
        else:
            good_count += 1
        if good_count + bad_count > 15:
            break
    # random heuristic
    if bad_count > 10:
        print 'WARNING: Saw a bunch of unparsed cards:'
        print '         Is this a legacy format, you may need to specify the field order.'

    return cards
