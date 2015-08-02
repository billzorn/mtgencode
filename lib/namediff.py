import difflib
import os
import jdecode
import cardlib

libdir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.realpath(os.path.join(libdir, '../data'))

class Namediff:
    def __init__(self, verbose = True,
                 json_fname = os.path.join(datadir, 'AllSets.json')):
        self.verbose = verbose
        self.names = {}

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
                    
                if name in self.names:
                    print '  Duplicate name ' + name + ', ignoring.'
                else:
                    self.names[name] = jname
                    namecount += 1

        print '  Read ' + str(namecount) + ' unique cardnames'
        print '  Building SequenceMatcher objects.'
        
        self.matchers = [difflib.SequenceMatcher(b=n, autojunk=False) for n in self.names]

        print '... Done.'
    
    def nearest(self, name, n=3):
        for m in self.matchers:
            m.set_seq1(name)
        ratios = [(m.ratio(), m.b) for m in self.matchers]
        ratios.sort(reverse = True)

        if ratios[0][0] >= 1:
            return ratios[:1]
        else:
            return ratios[:n]
        
            

