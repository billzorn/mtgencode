# Natural Language Toolkit: Language Models
#
# Copyright (C) 2001-2014 NLTK Project
# Authors: Steven Bird <stevenbird1@gmail.com>
#          Daniel Blanchard <dblanchard@ets.org>
#          Ilia Kurenkov <ilia.kurenkov@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT
#
# adapted for mtgencode Nov. 2015
# an attempt was made to preserve the exact functionality of this code,
# hampered somewhat by its brokenness



from math import log

from nltk.probability import ConditionalProbDist, ConditionalFreqDist, LidstoneProbDist
from nltk.util import ngrams
from nltk_model_api import ModelI

from nltk import compat


def _estimator(fdist, **estimator_kwargs):
    """
    Default estimator function using a LidstoneProbDist.
    """
    # can't be an instance method of NgramModel as they
    # can't be pickled either.
    return LidstoneProbDist(fdist, 0.001, **estimator_kwargs)


@compat.python_2_unicode_compatible
class NgramModel(ModelI):
    """
    A processing interface for assigning a probability to the next word.
    """

    def __init__(self, n, train, pad_left=True, pad_right=False,
                 estimator=None, **estimator_kwargs):
        """
        Create an ngram language model to capture patterns in n consecutive
        words of training text.  An estimator smooths the probabilities derived
        from the text and may allow generation of ngrams not seen during
        training. See model.doctest for more detailed testing

            >>> from nltk.corpus import brown
            >>> lm = NgramModel(3, brown.words(categories='news'))
            >>> lm
            <NgramModel with 91603 3-grams>
            >>> lm._backoff
            <NgramModel with 62888 2-grams>
            >>> lm.entropy(brown.words(categories='humor'))
            ... # doctest: +ELLIPSIS
            12.0399...

        :param n: the order of the language model (ngram size)
        :type n: int
        :param train: the training text
        :type train: list(str) or list(list(str))
        :param pad_left: whether to pad the left of each sentence with an (n-1)-gram of empty strings
        :type pad_left: bool
        :param pad_right: whether to pad the right of each sentence with an (n-1)-gram of empty strings
        :type pad_right: bool
        :param estimator: a function for generating a probability distribution
        :type estimator: a function that takes a ConditionalFreqDist and
            returns a ConditionalProbDist
        :param estimator_kwargs: Extra keyword arguments for the estimator
        :type estimator_kwargs: (any)
        """

        # protection from cryptic behavior for calling programs
        # that use the pre-2.0.2 interface
        assert(isinstance(pad_left, bool))
        assert(isinstance(pad_right, bool))

        self._lpad = ('',) * (n - 1) if pad_left else ()
        self._rpad = ('',) * (n - 1) if pad_right else ()

        # make sure n is greater than zero, otherwise print it
        assert (n > 0), n

        # For explicitness save the check whether this is a unigram model
        self.is_unigram_model = (n == 1)
        # save the ngram order number
        self._n = n
        # save left and right padding
        self._lpad = ('',) * (n - 1) if pad_left else ()
        self._rpad = ('',) * (n - 1) if pad_right else ()

        if estimator is None:
            estimator = _estimator

        cfd = ConditionalFreqDist()

        # set read-only ngrams set (see property declaration below to reconfigure)
        self._ngrams = set()

        # If given a list of strings instead of a list of lists, create enclosing list
        if (train is not None) and isinstance(train[0], compat.string_types):
            train = [train]

        # we need to keep track of the number of word types we encounter
        vocabulary = set()
        for sent in train:
            raw_ngrams = ngrams(sent, n, pad_left, pad_right, pad_symbol='')
            for ngram in raw_ngrams:
                self._ngrams.add(ngram)
                context = tuple(ngram[:-1])
                token = ngram[-1]
                cfd[context][token] += 1
                vocabulary.add(token)

        # Unless number of bins is explicitly passed, we should use the number
        # of word types encountered during training as the bins value.
        # If right padding is on, this includes the padding symbol.
        if 'bins' not in estimator_kwargs:
            estimator_kwargs['bins'] = len(vocabulary)

        self._model = ConditionalProbDist(cfd, estimator, **estimator_kwargs)

        # recursively construct the lower-order models
        if not self.is_unigram_model:
            self._backoff = NgramModel(n-1, train,
                                        pad_left, pad_right,
                                        estimator,
                                        **estimator_kwargs)

            self._backoff_alphas = dict()
            # For each condition (or context)
            for ctxt in cfd.conditions():
                backoff_ctxt = ctxt[1:]
                backoff_total_pr = 0.0
                total_observed_pr = 0.0

                # this is the subset of words that we OBSERVED following
                # this context.
                # i.e. Count(word | context) > 0
                for words in self._words_following(ctxt, cfd):
                    
                    # so, _words_following as fixed gives back a whole list now...
                    for word in words:

                        total_observed_pr += self.prob(word, ctxt)
                        # we also need the total (n-1)-gram probability of
                        # words observed in this n-gram context
                        backoff_total_pr += self._backoff.prob(word, backoff_ctxt)

                assert (0 <= total_observed_pr <= 1), total_observed_pr
                # beta is the remaining probability weight after we factor out
                # the probability of observed words.
                # As a sanity check, both total_observed_pr and backoff_total_pr
                # must be GE 0, since probabilities are never negative
                beta = 1.0 - total_observed_pr

                # backoff total has to be less than one, otherwise we get
                # an error when we try subtracting it from 1 in the denominator
                assert (0 <= backoff_total_pr < 1), backoff_total_pr
                alpha_ctxt = beta / (1.0 - backoff_total_pr)

                self._backoff_alphas[ctxt] = alpha_ctxt

    # broken
    # def _words_following(self, context, cond_freq_dist):
    #     for ctxt, word in cond_freq_dist.iterkeys():
    #         if ctxt == context:
    #             yield word

    # fixed
    def _words_following(self, context, cond_freq_dist):
        for ctxt in cond_freq_dist.keys():
            if ctxt == context:
                yield list(cond_freq_dist[ctxt].keys())

    def prob(self, word, context):
        """
        Evaluate the probability of this word in this context using Katz Backoff.

        :param word: the word to get the probability of
        :type word: str
        :param context: the context the word is in
        :type context: list(str)
        """
        context = tuple(context)
        if (context + (word,) in self._ngrams) or (self.is_unigram_model):
            return self._model[context].prob(word)
        else:
            return self._alpha(context) * self._backoff.prob(word, context[1:])

    def _alpha(self, context):
        """Get the backoff alpha value for the given context
        """
        error_message = "Alphas and backoff are not defined for unigram models"
        assert not self.is_unigram_model, error_message

        if context in self._backoff_alphas:
            return self._backoff_alphas[context]
        else:
            return 1

    def logprob(self, word, context):
        """
        Evaluate the (negative) log probability of this word in this context.

        :param word: the word to get the probability of
        :type word: str
        :param context: the context the word is in
        :type context: list(str)
        """
        return -log(self.prob(word, context), 2)

    @property
    def ngrams(self):
        return self._ngrams

    @property
    def backoff(self):
        return self._backoff

    @property
    def model(self):
        return self._model

    def choose_random_word(self, context):
        '''
        Randomly select a word that is likely to appear in this context.

        :param context: the context the word is in
        :type context: list(str)
        '''

        return self.generate(1, context)[-1]

    # NB, this will always start with same word if the model
    # was trained on a single text
    def generate(self, num_words, context=()):
        '''
        Generate random text based on the language model.

        :param num_words: number of words to generate
        :type num_words: int
        :param context: initial words in generated string
        :type context: list(str)
        '''

        text = list(context)
        for i in range(num_words):
            text.append(self._generate_one(text))
        return text

    def _generate_one(self, context):
        context = (self._lpad + tuple(context))[-self._n + 1:]
        if context in self:
            return self[context].generate()
        elif self._n > 1:
            return self._backoff._generate_one(context[1:])
        else:
            return '.'

    def entropy(self, text):
        """
        Calculate the approximate cross-entropy of the n-gram model for a
        given evaluation text.
        This is the average log probability of each word in the text.

        :param text: words to use for evaluation
        :type text: list(str)
        """

        H = 0.0     # entropy is conventionally denoted by "H"
        text = list(self._lpad) + text + list(self._rpad)
        for i in range(self._n - 1, len(text)):
            context = tuple(text[(i - self._n + 1):i])
            token = text[i]
            H += self.logprob(token, context)
        return H / float(len(text) - (self._n - 1))

    def perplexity(self, text):
        """
        Calculates the perplexity of the given text.
        This is simply 2 ** cross-entropy for the text.

        :param text: words to calculate perplexity of
        :type text: list(str)
        """

        return pow(2.0, self.entropy(text))

    def __contains__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return item in self._model

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return self._model[item]

    def __repr__(self):
        return '<NgramModel with %d %d-grams>' % (len(self._ngrams), self._n)

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
