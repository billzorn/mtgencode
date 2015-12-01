# This module is misleadingly named, as it has other utilities as well
# that are generally necessary when trying to postprocess output by
# comparing it against existing cards.

import difflib
import os
import multiprocessing

import utils
import jdecode
import cardlib

libdir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.realpath(os.path.join(libdir, '../data'))

# multithreading control parameters
cores = multiprocessing.cpu_count()

# split a list into n pieces; return a list of these lists
# has slightly interesting behavior, in that if n is large, it can
# run out of elements early and return less than n lists
def list_split(l, n):
    if n <= 0:
        return l
    split_size = len(l) / n
    if len(l) % n > 0:
        split_size += 1
    return [l[i:i+split_size] for i in range(0, len(l), split_size)]

# flatten a list of lists into a single list of all their contents, in order
def list_flatten(l):
    return [item for sublist in l for item in sublist]


# isolated logic for multiprocessing
def f_nearest(name, matchers, n):
    for m in matchers:
        m.set_seq1(name)
    ratios = [(m.ratio(), m.b) for m in matchers]
    ratios.sort(reverse = True)

    if ratios[0][0] >= 1:
        return ratios[:1]
    else:
        return ratios[:n]

def f_nearest_per_thread(workitem):
    (worknames, names, n) = workitem
    # each thread (well, process) needs to generate its own matchers
    matchers = [difflib.SequenceMatcher(b=name, autojunk=False) for name in names]
    return map(lambda name: f_nearest(name, matchers, n), worknames)

class Namediff:
    def __init__(self, verbose = True,
                 json_fname = os.path.join(datadir, 'AllSets.json')):
        self.verbose = verbose
        self.names = {}
        self.codes = {}
        self.cardstrings = {}

        if self.verbose:
            print 'Setting up namediff...'

        if self.verbose:
            print '  Reading names from: ' + json_fname
        json_srcs = jdecode.mtg_open_json(json_fname, verbose)
        namecount = 0
        for json_cardname in sorted(json_srcs):
            if len(json_srcs[json_cardname]) > 0:
                jcards = json_srcs[json_cardname]

                # just use the first one
                idx = 0
                card = cardlib.Card(jcards[idx])
                name = card.name
                jname = jcards[idx]['name']
                jcode = jcards[idx][utils.json_field_info_code]
                if 'number' in jcards[idx]:
                    jnum = jcards[idx]['number']
                else:
                    jnum = ''
                    
                if name in self.names:
                    print '  Duplicate name ' + name + ', ignoring.'
                else:
                    self.names[name] = jname
                    self.cardstrings[name] = card.encode()
                    if jcode and jnum:
                        self.codes[name] = jcode + '/' + jnum + '.jpg'
                    else:
                        self.codes[name] = ''
                    namecount += 1

        print '  Read ' + str(namecount) + ' unique cardnames'
        print '  Building SequenceMatcher objects.'
        
        self.matchers = [difflib.SequenceMatcher(b=n, autojunk=False) for n in self.names]
        self.card_matchers = [difflib.SequenceMatcher(b=self.cardstrings[n], autojunk=False) for n in self.cardstrings]

        print '... Done.'
    
    def nearest(self, name, n=3):
        return f_nearest(name, self.matchers, n)

    def nearest_par(self, names, n=3, threads=cores):
        workpool = multiprocessing.Pool(threads)
        proto_worklist = list_split(names, threads)
        worklist = map(lambda x: (x, self.names, n), proto_worklist)
        donelist = workpool.map(f_nearest_per_thread, worklist)
        return list_flatten(donelist)

    def nearest_card(self, card, n=5):
        return f_nearest(card.encode(), self.card_matchers, n)

    def nearest_card_par(self, cards, n=5, threads=cores):
        workpool = multiprocessing.Pool(threads)
        proto_worklist = list_split(cards, threads)
        worklist = map(lambda x: (map(lambda c: c.encode(), x), self.cardstrings.values(), n), proto_worklist)
        donelist = workpool.map(f_nearest_per_thread, worklist)
        return list_flatten(donelist)
