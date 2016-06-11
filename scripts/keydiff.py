#!/usr/bin/env python

def parse_keyfile(f, d, constructor = lambda x: x):
    for line in f:
        kv = map(lambda s: s.strip(), line.split(':'))
        if not len(kv) == 2:
            continue
        d[kv[0]] = constructor(kv[1])

def merge_dicts(d1, d2):
    d = {}
    for k in d1:
        d[k] = (d1[k], d2[k] if k in d2 else None)
    for k in d2:
        if not k in d:
            d[k] = (None, d2[k])
    return d

def main(fname1, fname2, verbose = True):
    if verbose:
        print 'opening ' + fname1 + ' as base key/value store'
        print 'opening ' + fname2 + ' as target key/value store'

    d1 = {}
    d2 = {}
    with open(fname1, 'rt') as f1:
        parse_keyfile(f1, d1, int)
    with open(fname2, 'rt') as f2:
        parse_keyfile(f2, d2, int)
    
    tot1 = sum(d1.values())
    tot2 = sum(d2.values())

    if verbose:
        print '  ' + fname1 + ': ' + str(len(d1)) + ', total ' + str(tot1)
        print '  ' + fname2 + ': ' + str(len(d2)) + ', total ' + str(tot2)

    d_merged = merge_dicts(d1, d2)

    ratios = {}
    only_1 = {}
    only_2 = {}
    for k in d_merged:
        (v1, v2) = d_merged[k]
        if v1 is None:
            only_2[k] = v2
        elif v2 is None:
            only_1[k] = v1
        else:
            ratios[k] = float(v2 * tot1) / float(v1 * tot2)

    print 'shared: ' + str(len(ratios))
    for k in sorted(ratios, lambda x,y: cmp(d2[x], d2[y]), reverse=True):
        print '  ' + k + ': ' + str(d2[k]) + '/' + str(d1[k]) + ' (' + str(ratios[k]) + ')'
    print ''
        
    print '1 only: ' + str(len(only_1))
    for k in sorted(only_1, lambda x,y: cmp(d1[x], d1[y]), reverse=True):
        print '  ' + k + ': ' + str(d1[k])
    print ''

    print '2 only: ' + str(len(only_2))
    for k in sorted(only_2, lambda x,y: cmp(d2[x], d2[y]), reverse=True):
        print '  ' + k + ': ' + str(d2[k])
    print ''

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('file1', #nargs='?'. default=None,
                        help='base key file to diff against')
    parser.add_argument('file2', nargs='?', default=None,
                        help='other file to compare against the baseline')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    main(args.file1, args.file2, verbose=args.verbose)
    exit(0)
