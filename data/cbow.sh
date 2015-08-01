#!/bin/bash

word2vec -train cbow.txt -output cbow.bin -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 8 -binary 1 -iter 15
