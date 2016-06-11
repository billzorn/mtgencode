#!/usr/bin/env python
import sys
import os
import subprocess
import random

def extract_cp_name(name):
    # "lm_lstm_epoch50.00_0.1870.t7"
    if not (name[:13] == 'lm_lstm_epoch' and name[-3:] == '.t7'):
        return None
    name = name[13:-3]
    (epoch, vloss) = tuple(name.split('_'))
    return (float(epoch), float(vloss))

def sample(cp, temp, count, seed = None, ident = 'output'):
    if seed is None:
        seed = random.randint(-1000000000, 1000000000)
    outfile = cp + '.' + ident + '.' + str(temp) + '.txt'
    cmd = ('th sample.lua ' + cp 
           + ' -temperature ' + str(temp) 
           + ' -length ' + str(count)
           + ' -seed ' + str(seed)
           + ' >> ' + outfile)
    if os.path.exists(outfile):
        print(outfile + ' already exists, skipping')
        return False
    else:
        # UNSAFE SHELL=TRUE FOR CONVENIENCE
        subprocess.call('echo "' + cmd + '" | tee ' + outfile, shell=True)
        subprocess.call(cmd, shell=True)

def find_best_cp(cpdir):
    best = None
    best_cp = None
    for path in os.listdir(cpdir):
        fullpath = os.path.join(cpdir, path)
        if os.path.isfile(fullpath):
            extracted = extract_cp_name(path)
            if not extracted is None:
                (epoch, vloss) = extracted
                if best is None or vloss < best:
                    best = vloss
                    best_cp = fullpath
    return best_cp

def process_dir(cpdir, temp, count, seed = None, ident = 'output', verbose = False):
    if verbose:
        print('processing ' + cpdir)
    best_cp = find_best_cp(cpdir)
    if not best_cp is None:
        sample(best_cp, temp, count, seed=seed, ident=ident)
    for path in os.listdir(cpdir):
        fullpath = os.path.join(cpdir, path)
        if os.path.isdir(fullpath):
            process_dir(fullpath, temp, count, seed=seed, ident=ident, verbose=verbose)

def main(rnndir, cpdir, temp, count, seed = None, ident = 'output', verbose = False):
    if not os.path.isdir(rnndir):
        raise ValueError('bad rnndir: ' + rnndir)
    if not os.path.isdir(cpdir):
        raise ValueError('bad cpdir: ' + cpdir)
    os.chdir(rnndir)
    process_dir(cpdir, temp, count, seed=seed, ident=ident, verbose=verbose)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('rnndir', #nargs='?'. default=None,
                        help='base rnn directory, must contain sample.lua')
    parser.add_argument('cpdir', #nargs='?', default=None,
                        help='checkpoint directory, all subdirectories will be processed')
    parser.add_argument('-t', '--temperature', action='store', default='1.0',
                        help='sampling temperature')
    parser.add_argument('-c', '--count', action='store', default='1000000',
                        help='number of characters to sample each time')
    parser.add_argument('-s', '--seed', action='store', default=None,
                        help='fixed seed; if not present, a random seed will be used')
    parser.add_argument('-i', '--ident', action='store', default='output',
                        help='identifier to include in the output filenames')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    if args.seed is None:
        seed = None
    else:
        seed = int(args.seed)
    main(args.rnndir, args.cpdir, float(args.temperature), int(args.count), 
         seed=seed, ident=args.ident, verbose = args.verbose)
    exit(0)
