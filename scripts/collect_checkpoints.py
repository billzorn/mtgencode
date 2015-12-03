#!/usr/bin/env python
import sys
import os
import shutil

def cleanup_dump(dumpstr):
    cardfrags = dumpstr.split('\n\n')
    if len(cardfrags) < 4:
        return ''
    else:
        return '\n\n'.join(cardfrags[2:-1]) + '\n\n'

def identify_checkpoints(basedir, ident):
    cp_infos = []
    for path in os.listdir(basedir):
        fullpath = os.path.join(basedir, path)
        if not os.path.isfile(fullpath):
            continue
        if not (path[:13] == 'lm_lstm_epoch' and path[-4:] == '.txt'):
            continue
        if not ident in path:
            continue
        # attempt super hacky parsing
        inner = path[13:-4]
        halves = inner.split('_')
        if not len(halves) == 2:
            continue
        parts = halves[1].split('.')
        if not len(parts) == 6:
            continue
        # lm_lstm_epoch[25.00_0.3859.t7.output.1.0].txt
        if not parts[3] == ident:
            continue
        epoch = halves[0]
        vloss = '.'.join([parts[0], parts[1]])
        temp = '.'.join([parts[4], parts[5]])
        cpname = 'lm_lstm_epoch' + epoch + '_' + vloss + '.t7'
        cp_infos += [(fullpath, os.path.join(basedir, cpname),
                      (epoch, vloss, temp))]
    return cp_infos

def process_dir(basedir, targetdir, ident, copy_cp = False, verbose = False):
    (basepath, basedirname) = os.path.split(basedir)
    if basedirname == '':
        (basepath, basedirname) = os.path.split(basepath)

    cp_infos = identify_checkpoints(basedir, ident)
    for (dpath, cpath, (epoch, vloss, temp)) in cp_infos:
        if verbose:
            print('found dumpfile ' + dpath)
        dname = basedirname + '_epoch' + epoch + '_' + vloss + '.' + ident + '.' + temp + '.txt'
        cname = basedirname + '_epoch' + epoch + '_' + vloss + '.t7'
        tdpath = os.path.join(targetdir, dname)
        tcpath = os.path.join(targetdir, cname)
        if verbose:
            print('    cpx ' + dpath + ' ' + tdpath)
        with open(dpath, 'rt') as infile:
            with open(tdpath, 'wt') as outfile:
                outfile.write(cleanup_dump(infile.read()))
        if copy_cp:
            if os.path.isfile(cpath):
                if verbose:
                    print('    cp ' + cpath + ' ' + tcpath)
                shutil.copy(cpath,  tcpath)

    if copy_cp and len(cp_infos) > 0:
        cmdpath = os.path.join(basedir, 'command.txt')
        tcmdpath = os.path.join(targetdir, basedirname + '.command')
        if os.path.isfile(cmdpath):
            if verbose:
                print('    cp ' + cmdpath + ' ' + tcmdpath)
            shutil.copy(cmdpath,  tcmdpath)

    for path in os.listdir(basedir):
        fullpath = os.path.join(basedir, path)
        if os.path.isdir(fullpath):
            process_dir(fullpath, targetdir, ident, copy_cp=copy_cp, verbose=verbose)
            
def main(basedir, targetdir, ident = 'output', copy_cp = False, verbose = False):
    process_dir(basedir, targetdir, ident, copy_cp=copy_cp, verbose=verbose)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('basedir', #nargs='?'. default=None,
                        help='base rnn directory, must contain sample.lua')
    parser.add_argument('targetdir', #nargs='?', default=None,
                        help='checkpoint directory, all subdirectories will be processed')
    parser.add_argument('-c', '--copy_cp', action='store_true', 
                        help='copy checkpoints used to generate the output files')
    parser.add_argument('-i', '--ident', action='store', default='output',
                        help='identifier to look for to determine checkpoints')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='verbose output')

    args = parser.parse_args()
    main(args.basedir, args.targetdir, ident=args.ident, copy_cp=args.copy_cp, verbose=args.verbose)
    exit(0)
