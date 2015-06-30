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

def cleanup_mana(s, pretty = False):
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

    untranslations_pretty = {
        'WW' : 'W',
        'UU' : 'U',
        'BB' : 'B',
        'RR' : 'R',
        'GG' : 'G',
        'PP' : 'P',
        'SS' : 'S',
        'XX' : 'X',
    }

    if pretty:
        ldelim = ''
        rdelim = ''
    else:
        ldelim = '{'
        rdelim = '}'

    manacosts = re.findall(r'\{[WUBRGPVSX\^]*\}', s)
    for cost in manacosts:
        if cost == '{}':
            s = s.replace(cost, ldelim + '0' + rdelim)
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
            newcost += ldelim + str(colorless_total) + rdelim

        # now try to read the remaining characters in pairs
        success = True
        while len(innercost) > 1:
            fragment = innercost[0:2]
            if pretty and fragment in untranslations_pretty:
                newcost += untranslations_pretty[fragment]
            elif fragment in untranslations:
                newcost += untranslations[fragment]
            else:
                success = False
                break
            innercost = innercost[2:]

        if pretty:
            cost = '[mana]' + cost + '[/mana]'
        
        if len(innercost) == 0 and success:
            s = s.replace(cost, newcost)
        # else:
        #     print cost
        #     print newcost
    
    return s


def unreplace_newlines(s):
    return s.replace('\\', '\n')


def forum_reorder(s):
    fields = s.split('|')
    # should see ten of em
    if not len(fields) == 10:
        #print 'badlen ' + str(len(fields))
        return s
    # first and last should be empty, if we had | on the ends
    if not (fields[0] == '' and fields [-1] == '\n'):
        #print 'badfields ' + repr(fields[0]) + ', ' + repr(fields[-1]) 
        return s
    name = fields[1]
    supertypes = fields[2]
    types = fields[3]
    loyalty = fields[4]
    subtypes = fields[5]
    pt = fields[6]
    cost = fields[7]
    text = fields[8]

    new_s = ''
    if not name == '':
        new_s += name + '\n'
    if not cost == '':
        new_s += cost + '\n'

    if not supertypes == '':
        new_s += supertypes + ' '
    if not types == '':
        new_s += types
    if not subtypes == '':
        new_s += ' ~ ' + subtypes + '\n'
    else:
        new_s += '\n'
    # super special case, doubt it will come up
    if types == '' and subtypes == '':
        new_s += '\n'
    
    if not text == '':
        new_s += text + '\n'
    if not pt == '':
        new_s += pt + '\n'
    if not loyalty == '':
        new_s += '(' + loyalty + ')\n'

    return new_s

def unscramble(s, pretty = False):
    s = from_unary(s)
    s = cleanup_mana(s, pretty)
    s = unreplace_newlines(s)
    s = forum_reorder(s)
    return s
    

def main(fname, oname = None, verbose = True, pretty = False):
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
        val = unscramble(line, pretty)
        if oname == None:
            sys.stdout.write(val)
        else:
            ofile.write(val)

    if not oname == None:
        ofile.close()

    
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], oname = sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[3] in ['p', '-p', 'pretty', '-pretty', '--pretty']:
        main(sys.argv[1], oname = sys.argv[2], pretty = True)
    else:
        print 'Usage: ' + sys.argv[0] + ' ' + '<encoded file> [output filename [p]]'
        exit(1)

