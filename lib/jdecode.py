import json

import config

def mtg_open_json(fname, verbose = False):

    with open(fname, 'r') as f:
        jobj = json.load(f)
    
    allcards = {}
    asides = {}
    bsides = {}

    for k_set in jobj:
        set = jobj[k_set]
        setname = set['name']
        
        for card in set['cards']:
            card[config.json_field_set_name] = setname

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
                asides[aside_uid][config.json_field_bside] = bsides[uid]
        else:
            pass
            # this exposes some coldsnap theme deck bsides that aren't
            # really bsides; shouldn't matter too much
            #print aside_uid
            #print bsides[uid]

    if verbose:
        print 'Opened ' + str(len(allcards)) + ' uniquely named cards.'
    return allcards
