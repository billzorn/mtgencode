import re
import codecs
import sys

# there should really be a separate file to store the character choices and such

def from_unary(s):
    numbers = re.findall(r'&\^*', s)
    for number in sorted(numbers, cmp = lambda x,y: cmp(len(x), len(y)) * -1):
        i = len(number) - 1
        s = s.replace(number, str(i))
    return s

def cleanup_mana(s):
    untranslations = {
        'WW' : '{W}',
        'UU' : '{U}',
        'BB' : '{B}',
        'RR' : '{R}',
        'GG' : '{G}',
        'PP' : '{P}',
        'WP' : '{W/P}',
        'UP' : '{U/P}',
        'BP' : '{B/P}',
        'RP' : '{R/P}',
        'GP' : '{G/P}',
        'VW' : '{2/W}',
        'VU' : '{2/U}',
        'VB' : '{2/B}',
        'VR' : '{2/R}',
        'VG' : '{2/G}',
        'WU' : '{W/U}',
        'WB' : '{W/B}',
        'RW' : '{R/W}',
        'GW' : '{G/W}',
        'UB' : '{U/B}',
        'UR' : '{U/R}',
        'GU' : '{G/U}',
        'BR' : '{B/R}',
        'BG' : '{B/G}',
        'RG' : '{R/G}',
        'SS' : '{S}',
        'XX' : '{X}',
    }

    manacosts = re.findall(r'\{[WUBRGPVSX\^]*\}', s)
    for cost in manacosts:
        if cost == '{}':
            s = s.replace(cost, '{0}')
            continue

        innercost = cost[1:-1]
        newcost = ''
        colorless_total = 0

        # pull out unary countingses
        colorless_counts = re.findall(r'\^+', innercost)
        for count in colorless_counts:
            innercost = innercost.replace(count, '')
            colorless_total += len(count)            
        if colorless_total > 0:
            newcost += '{' + str(colorless_total) + '}'

        # now try to read the remaining characters in pairs
        success = True
        while len(innercost) > 1:
            fragment = innercost[0:2]
            if fragment in untranslations:
                newcost += untranslations[fragment]
            else:
                success = False
                break
            innercost = innercost[2:]
        
        if len(innercost) == 0 and success:
            s = s.replace(cost, newcost)
        # else:
        #     print cost
        #     print newcost
    
    return s


def unreplace_newlines(s):
    return s.replace('\\', '\n')

def unscramble(s):
    s = from_unary(s)
    s = cleanup_mana(s)
    s = unreplace_newlines(s)
    return s
    

def main(fname, oname = None, verbose = True):
    if verbose:
        print 'Opening encoded card file: ' + fname

    f = open(fname, 'r')
    lines = f.readlines()
    f.close()

    if not oname == None:
        if verbose:
            print 'Writing output to: ' + oname
        ofile = codecs.open(oname, 'w', 'utf-8')

    for line in lines:
        val = unscramble(line)
        if oname == None:
            sys.stdout.write(val)
        else:
            ofile.write(val)
        
    # print len(badwords)
    # for word in badwords:
    #     print word

    if not oname == None:
        ofile.close()

    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file> [output filename]'
        exit(1)

