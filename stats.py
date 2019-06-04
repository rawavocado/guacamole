import math

def describe(data, pop=False, only=[]):
    '''
    returns dict describing statistics of numeric data w/ keys like:
       (cnt, min, max, mean, median, modes, variance, stddev) 
       where, by default, variance/stddev treat data as sample 
       else if pop==True, variance/stddev treat data as population.
       if only is a subset of the stats keys above, processing
       is optimised for only the calcs necessary to produce
       and return a dict with the keys listed in only.
    ex) stats = describe([0, 1, 2, 3, 4, 5, 5, 6, 7, 8, 9])
    '''
    answer = {}

    cnt = len([x for x in data if x!=None])
    if cnt < 2: return None
    if not only or 'cnt' in only: 
        answer['cnt'] = cnt

    if not only or 'min' in only:
        answer['min'] = min((x for x in data if x!=None))

    if not only or 'max' in only:
        answer['max'] = max((x for x in data if x!=None))

    if not only or set(['mean','variance','stddev']).intersection(only): 
        mean = sum([x for x in data if x!=None]) / float(cnt)
        if not only or 'mean' in only:
            answer['mean'] = mean

    if not only or 'median' in only:
        midtuple = sorted([x for x in data if x!=None])[cnt/2-1:cnt/2+1]
        if cnt % 2: answer['median'] = midtuple[1]
        else: answer['median'] = sum(midtuple) / 2.0

    if not only or 'modes' in only:
        modes, maxcnt = [], 0
        valcnt = {v: None for v in set([x for x in data if x!=None])}
        for k in valcnt.keys():
            valcnt[k] = len([None for x in data if x==k])
            if valcnt[k] > maxcnt: 
                modes = [k]
                maxcnt = valcnt[k]
            elif valcnt[k] == maxcnt:
                modes.append(k)
        answer['modes'] = modes

    if not only or 'variance' in only or 'stddev' in only:
        if pop: divisor = float(cnt)
        else: divisor = float(cnt) - 1

        if pop: variance = (sum([(x)**2 for x in data if x!=None]) / divisor) - mean**2
        else: variance = (sum([(x)**2 for x in data if x!=None]) / divisor) - ((mean**2)*cnt) / divisor
        # textbook but slow, above is faster, result is ALMOST the same
        #slowvariance = sum([(x-mean)**2 for x in data]) / divisor 
        if not only or 'variance' in only: 
            answer['variance'] = variance

        if not only or 'stddev' in only:
            answer['stddev'] = math.sqrt(variance)

    return answer

def describe_str(aDict):
    '''
    returns a string formatted from a describe() dict
    ex) stats = describe([0, 1, 2, 3, 4, 5, 5, 6, 7, 8, 9])
        print describe_str(stats) 
    '''
    return ''.join([
        aDict.get('cnt', False) and 'cnt:%d ' % aDict['cnt'] or '',
        aDict.get('min', False) and 'min:%s ' % aDict['min'] or '',
        aDict.get('max', False) and 'max:%s ' % aDict['max'] or '',
        aDict.get('mean', False) and 'mean:%.2f ' % aDict['mean'] or '',
        aDict.get('median', False) and 'median:%s ' % aDict['median'] or '',
        aDict.get('modes', False) and 'modes:%s ' % aDict['modes'] or '',
        aDict.get('variance', False) and 'variance:%.2f ' % aDict['variance'] or '',
        aDict.get('stddev', False) and 'stddev:%.2f ' % aDict['stddev'] or '',
        ])

if __name__ == '__main__':

    samples = [
        [1,1,2,3,4],
        [3,3,3,3,3,100],
        [2,2,3,3],
        [0,0,5,5],
        [1,2,3,8,7],
        [0,0,5,9,9], [0,0,5,9,9]*2,
        [None, 0, 1]
        ]

    for samp in samples:
        for pop in [True, False]:
            a_all = describe(samp, pop)
            print('%4s %s: %s' % (pop and 'pop' or 'samp', samp, describe_str(a_all)))
            for key in ['cnt','mean','median','modes','variance','stddev']:
                assert a_all[key] == describe(samp, pop, only=[key])[key] 
