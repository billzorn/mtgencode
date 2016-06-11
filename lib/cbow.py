# Infinite thanks to Talcos from the mtgsalvation forums, who among
# many, many other things wrote the original version of this code.
# I have merely ported it to fit my needs.

import re
import sys
import subprocess
import os
import struct
import math
import multiprocessing

import utils
import cardlib
import transforms
import namediff

libdir = os.path.dirname(os.path.realpath(__file__))
datadir = os.path.realpath(os.path.join(libdir, '../data'))

# multithreading control parameters
cores = multiprocessing.cpu_count()

# max length of vocabulary entries
max_w = 50


#### snip! ####

def read_vector_file(fname):
    with open(fname, 'rb') as f:
        words = int(f.read(4))
        size = int(f.read(4))
        vocab = [' '] * (words * max_w)
        M = []
        for b in range(0,words):
            a = 0
            while True:
                c = f.read(1)
                vocab[b * max_w + a] = c;
                if len(c) == 0 or c == ' ':
                    break
                if (a < max_w) and vocab[b * max_w + a] != '\n':
                    a += 1
            tmp = list(struct.unpack('f'*size,f.read(4 * size)))
            length = math.sqrt(sum([tmp[i] * tmp[i] for i in range(0,len(tmp))]))
            for i in range(0,len(tmp)):
                tmp[i] /= length
            M.append(tmp)
        return ((''.join(vocab)).split(),M)

def makevector(vocabulary,vecs,sequence):
    words = sequence.split()
    indices = []
    for word in words:
        if word not in vocabulary:
            #print("Missing word in vocabulary: " + word)
            continue
            #return [0.0]*len(vecs[0])
        indices.append(vocabulary.index(word))
    #res = map(sum,[vecs[i] for i in indices])
    res = None
    for v in [vecs[i] for i in indices]:
        if res == None:
            res = v
        else:
            res = [x + y for x, y in zip(res,v)]

    # bad things happen if we have a vector of only unknown words
    if res is None:
        return [0.0]*len(vecs[0])

    length = math.sqrt(sum([res[i] * res[i] for i in range(0,len(res))]))
    for i in range(0,len(res)):
        res[i] /= length
    return res

#### !snip ####


try:
    import numpy
    def cosine_similarity(v1,v2):
        A = numpy.array([v1,v2])

        # from http://stackoverflow.com/questions/17627219/whats-the-fastest-way-in-python-to-calculate-cosine-similarity-given-sparse-mat

        # base similarity matrix (all dot products)
        # replace this with A.dot(A.T).todense() for sparse representation
        similarity = numpy.dot(A, A.T)
        
        # squared magnitude of preference vectors (number of occurrences)
        square_mag = numpy.diag(similarity)

        # inverse squared magnitude
        inv_square_mag = 1 / square_mag

        # if it doesn't occur, set it's inverse magnitude to zero (instead of inf)
        inv_square_mag[numpy.isinf(inv_square_mag)] = 0

        # inverse of the magnitude
        inv_mag = numpy.sqrt(inv_square_mag)
        
        # cosine similarity (elementwise multiply by inverse magnitudes)
        cosine = similarity * inv_mag
        cosine = cosine.T * inv_mag
    
        return cosine[0][1]

except ImportError:
    def cosine_similarity(v1,v2):
        #compute cosine similarity of v1 to v2: (v1 dot v1)/{||v1||*||v2||)
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i]; y = v2[i]
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        return sumxy/math.sqrt(sumxx*sumyy)

def cosine_similarity_name(cardvec, v, name):
    return (cosine_similarity(cardvec, v), name)

# we need to put the logic in a regular function (as opposed to a method of an object)
# so that we can pass the function to multiprocessing
def f_nearest(card, vocab, vecs, cardvecs, n):
    if isinstance(card, cardlib.Card):
        words = card.vectorize().split('\n\n')[0]
    else:
        # assume it's a string (that's already a vector)
        words = card
            
    if not words:
        return []

    cardvec = makevector(vocab, vecs, words)

    comparisons = [cosine_similarity_name(cardvec, v, name) for (name, v) in cardvecs]

    comparisons.sort(reverse = True)
    comp_n = comparisons[:n]
    
    if isinstance(card, cardlib.Card) and card.bside:
        comp_n += f_nearest(card.bside, vocab, vecs, cardvecs, n=n)

    return comp_n

def f_nearest_per_thread(workitem):
    (workcards, vocab, vecs, cardvecs, n) = workitem
    return map(lambda card: f_nearest(card, vocab, vecs, cardvecs, n), workcards)

class CBOW:
    def __init__(self, verbose = True,
                 vector_fname = os.path.join(datadir, 'cbow.bin'), 
                 card_fname = os.path.join(datadir, 'output.txt')):
        self.verbose = verbose
        self.cardvecs = []

        if self.verbose:
            print 'Building a cbow model...'

        if self.verbose:
            print '  Reading binary vector data from: ' + vector_fname
        (vocab, vecs) = read_vector_file(vector_fname)
        self.vocab = vocab
        self.vecs = vecs
        
        if self.verbose:
            print '  Reading encoded cards from: ' + card_fname
            print '  They\'d better be in the same order as the file used to build the vector model!'
        with open(card_fname, 'rt') as f:
            text = f.read()
        for card_src in text.split(utils.cardsep):
            if card_src:
                card = cardlib.Card(card_src)
                name = card.name
                self.cardvecs += [(name, makevector(self.vocab, 
                                                    self.vecs, 
                                                    card.vectorize()))]
                
        if self.verbose:
            print '... Done.'
            print '  vocab size: ' + str(len(self.vocab))
            print '  raw vecs:   ' + str(len(self.vecs))
            print '  card vecs:  ' + str(len(self.cardvecs))

    def nearest(self, card, n=5):
        return f_nearest(card, self.vocab, self.vecs, self.cardvecs, n)

    def nearest_par(self, cards, n=5, threads=cores):
        workpool = multiprocessing.Pool(threads)
        proto_worklist = namediff.list_split(cards, threads)
        worklist = map(lambda x: (x, self.vocab, self.vecs, self.cardvecs, n), proto_worklist)
        donelist = workpool.map(f_nearest_per_thread, worklist)
        return namediff.list_flatten(donelist)
