import re
import codecs
import sys

class Card:
    '''card representation with data'''

    def __init__(self, text):
        self.raw = text
        fields = self.raw.split('|')
        if not len(fields) == 10:
            self._parsed = False
            self._valid = False
            self.fields = fields
        else:
            self._parsed = True
            self._valid = True

            if not fields[1] == '':
                self.name = fields[1]
            else:
                self.name = ''
                self._valid = False

            if not fields[2] == '':
                self.supertypes = fields[2].split(' ')
            else:
                self.supertypes = None

            if not fields[3] == '':
                self.types = fields[3].split(' ')
            else:
                self.types = ''
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
            else:
                self.subtypes = None

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

            if not fields[7] == '':
                self.cost = fields[7]
            else:
                self.cost = None

            if not fields[8] == '':
                self.text = fields[8]
            else:
                self.text = None

def main(fname, oname = None, verbose = True):
    if verbose:
        print 'Opening encoded card file: ' + fname

    f = open(fname, 'r')
    text = f.read()
    f.close()

    # we get rid of the first and last because they are probably partial
    cardtexts = text.split('\n\n')[1:-1]
    cards = []

    i = 0
    for cardtext in cardtexts:
        cards += [Card(cardtext)]
        i += 1
        if i >= 5:
            break

    print cards


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file> [output filename]'
        exit(1)

