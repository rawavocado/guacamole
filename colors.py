import math

def get_factors(p, numfactors=2, minsum=True):
    '''
    find numfactors of p:
        when minsum==True: return first factors w/smallest sum
        when minsum==False: return first factors w/greatest sum
    '''
    answers = []
    for i in range(1, p):
        if p % i == 0: 
            if numfactors == 2: 
                answers.append((i, p//i))
            else: 
                subanswer = get_factors(p//i, numfactors-1, minsum)
                answers.append(tuple([i] + list(subanswer)))

    if minsum: f = min
    else: f = max
    target = f([sum(x) for x in answers])
    for answer in answers:
        if sum(answer) == target: break;
    return answer

def get_colors(n):
    '''
    returns smallish list of >=n colors w/ large intervals, avoids whites
    '''
    def get_rgbdivs(n):
        '''
        returns balancedish, fewest number of values each for (r, g, and b)
        '''
        answers = []
        for i in range(n//2):
            factors = get_factors(n+i, 3)
            score = sum([sum(factors), max(factors) - min(factors)])
            answers.append({'p': n+i, 'factors': factors, 'score': score})
        target = min([x['score'] for x in answers])
        for answer in answers:
            if target == answer['score']: break
        return answer['factors']

    answer, minrgb, maxrgb = [], 0, 192
    if n <= 1: return ['#%.2X%.2X%.2X' % (minrgb, maxrgb, minrgb)]
    intervals = [(maxrgb-minrgb) / (x-1 or x) for x in get_rgbdivs(n)]
    rvals, gvals, bvals = [range(minrgb, maxrgb+1, x) for x in intervals]
    for r in rvals:
        for g in gvals:
            for b in bvals:
                answer.append('#%.2X%.2X%.2X' % (r, g, b))
    return answer

def get_colorsOld(n):
    '''
    returns a list of >=n colors w/ large intervals, avoids whites
    '''
    #return [x for x in matplotlib.colors.cnames.values()]
    answer, minrgb, maxrgb = [], 0, 192
    cuberoot = math.ceil((n**(1/3.0))-1)
    if cuberoot != 0: intvl = (maxrgb - minrgb) / cuberoot
    else: intvl = maxrgb + 1
    rgbvals = range(minrgb, maxrgb + 1, int(intvl))
    for r in rgbvals:
        for g in rgbvals[::-1]:
            for b in rgbvals[::-1]:
                answer.append('#%.2X%.2X%.2X' % (r, g, b))
    return answer

import random
def get_colors2(n):
    answer, minrgb, maxrgb = [], 0, 192
    cuberoot = math.ceil((n**(1/3.0))-1)
    if cuberoot != 0: intvl = (maxrgb - minrgb) / cuberoot
    else: intvl = maxrgb + 1
    cube = int(cuberoot ** 3)
    #r2, g2, b2, t2 = [range(cube)] * 4
    r2, g2, b2, t2 = [], [], [], []
    rgbvals = range(minrgb, 255, int(intvl))
    iterator=0
    for r in rgbvals:
                '''
        for g in rgbvals[::-1]:
            for b in rgbvals[::-1]:
                r2[iterator]=r
                g2[iterator]=g
                b2[iterator]=b
                t2[iterator]=1
                '''
                r2.append(r)
                g2.append(r)
                b2.append(r)
                t2.append(1)
                iterator += 1
    iterator2=0
    '''
    for x in range(iterator):
        if r2[x]>maxrgb and g2[x]>maxrgb and b2[x]>maxrgb: 
            t2[x]=0
            iterator2 += 1
    for x in range(iterator):
        if r2[x]==g2[x]==b2[x] and t2[x]==1: 
            t2[x]=0
            iterator2 += 1
    '''

    toremove=cube-n-iterator2
    toremove=iterator2

    print 'cube', cube
    print 'toremove', toremove 
    print 'r2', r2 
    print 'b2', b2 
    print 'g2', g2
    print 't2', t2
    print rgbvals

    iterator3=0
    while True:
        #rand1=random.randint(0, cube)
        rand1=random.randint(0, len(t2))
        print rand1
        if t2[rand1]==1: 
            t2[rand1]=0
        iterator3 += 1

        answer.append('#%.2X%.2X%.2X' % (r2[iterator3], g2[iterator3], b2[iterator3]))
        if iterator3>toremove: 
            break
                
    return answer

if __name__ == '__main__':
    for n in 3, 4, 8, 9, 10, 11, 20, 25, 27, 28, 35, 41, 50, 60, 64, 65:
        print("\nget_colors(%d):" % n)
        colors = get_colors(n)
        print '%s %s' % (len(colors), colors)

    '''
    print get_colors2(27)
    '''

    for i in range(2,300):
        answers = []
        for j in range(i//2):
            factors = get_factors(i+j, 3)
            score = sum([sum(factors), max(factors) - min(factors)])
            answers.append({'p': i+j, 'factors': factors, 'score': score})
        target = answers[0]['score']
        target = min([x['score'] for x in answers])
        for answer in answers:
            if target == answer['score']: break
        print('get_factors(%3d, 3): %12s, best: %3d recs %s' % (
            i, answers[0]['factors'], answer['p'], answer['factors']
            ))
