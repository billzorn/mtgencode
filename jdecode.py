import json

# to allow filtering of sets like un sets, etc...
def legal_set(set):
    return not (set['type'] == 'un' or set['name'] == 'Celebration')

def mtg_open_json(fname, verbose = False):

    f = open(fname, 'r')    
    jobj = json.load(f)
    f.close()
    
    allcards = {}
    asides = {}
    bsides = {}

    for k_set in jobj:
        set = jobj[k_set]
        setname = set['name']
        
        if legal_set(set):
            for card in set['cards']:
                card['setName'] = setname

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
                asides[aside_uid]['bside'] = bsides[uid]
        else:
            pass
            # this exposes some coldsnap theme deck bsides that aren't
            # really bsides; shouldn't matter too much
            #print aside_uid
            #print bsides[uid]

    if verbose:
        print 'Opened ' + str(len(allcards)) + ' uniquely named cards.'
    return allcards
