'''
canned recipes for creating reports and or charts
    call one of the recipe functions below with any arguments 
    required by that particular recipe. does it's thing, whatever that is
'''

from datetime import datetime, timedelta
from operator import itemgetter
from library import AdKey, Ad, get_pkl, pkl_snap, lines_chart
from stats import describe, describe_str

# config for this session
since = datetime.now() - timedelta(30)
pkl = {k:v for k,v in get_pkl().items() if k.snap>=since}
snaps = pkl_snap(pkl, True)
verbose = True

def lc001(type_):
    '''
    chart diff_spotusd for ads matching (type_) by country
    Prints a line for all ads of this type, styled by country.
    '''
    kxyl = sorted([(ad.id, k.snap, ad.diff_spotusd, ad.country) 
        for k, ads in pkl.items() for ad in ads 
        if k.type_==type_])
    title = 'ads of type:%s by country' % type_
    xlabel, ylabel = '15m samples', 'diff_spotusd'
    lines_chart(kxyl, xlabel, ylabel, title, verbose=verbose)

def lc002(type_, country):
    '''
    chart diff_spotusd for ads matching (type_,country) by user
    Prints a line for all ads of this type and in this country
    styled by the trader/user.
    '''
    kxyl = sorted([(ad.id, k.snap, ad.diff_spotusd, ad.user) 
        for k, ads in pkl.items() for ad in ads 
        if k.type_==type_ and ad.country==country])
    title = 'ads of type:%s in country:%s by user' % (type_, country)
    xlabel, ylabel = '15m samples', 'diff_spotusd'
    lines_chart(kxyl, xlabel, ylabel, title, verbose=verbose)

def lc003(type_, country):
    '''
    chart equivalent usd price matching (type_,country) by location
    Prints a line for all ads of this type and in this county
    style by location.
    '''
    kxyl = sorted([(ad.id, k.snap, ad.usd, k.location.split('/')[1][:30]) 
        for k, ads in pkl.items() for ad in ads 
        if k.type_==type_ and ad.country==country])
    title = 'ads of type:%s in country:%s by location' % (type_, country)
    xlabel, ylabel = '15m samples', 'equiv usd price'
    lines_chart(kxyl, xlabel, ylabel, title, verbose=verbose)

def lc004(type_):
    '''
    chart number of (type_) ads by location
    Prints a line per location based on how many ads of this type were
    running over time.
    '''
    kxyl = sorted([('%d-%s' % (k.loc, k.type_), k.snap, len(vlist), 
        '%s %s' % (k.location.split('/')[1][:30], k.type_)) 
        for k, vlist in pkl.items() if k.type_==type_])
    title = 'number of ads by location,type_'
    xlabel, ylabel = '15m samples', 'ad listings'
    lines_chart(kxyl, xlabel, ylabel, title, verbose=verbose)

def lc005(type_, country):
    '''
    report statistics matching (type_,country) by ad, location, and whole set,
    then chart ads colored by location, styled by type_
    Prints a line for all ads of this type and country styled by 
    location; preceded by a report.
    '''
    kxyl = sorted([
        (ad.id, k.snap, ad.diff_spotusd, k.location.split('/')[1][:30]) 
        for k, ads in pkl.items() for ad in ads 
        if k.type_==type_ and ad.diff_spotusd != None and ad.country==country
        ])

    print("\n%s:%s stats per ad" % (type_, country))
    keys = sorted(set([k for k,x,y,l in kxyl]))
    for key in keys:
        answer = describe([y for k,x,y,l in kxyl if k==key], only=('mean','stddev'))
        if answer: print('ad:%s ' % key + describe_str(answer))

    print("\n%s:%s stats per location" % (type_, country))
    labels = sorted(set([l for k,x,y,l in kxyl]))
    for label in labels:
        print('label:%s ' % label + describe_str(
            describe([y for k,x,y,l in kxyl if l==label])))

    print
    print(describe_str(describe([y for k,x,y,l in kxyl])))

    # create a lines chart
    title = 'ads of type:%s in country:%s' % (type_, country)
    xlabel, ylabel = '15m samples', 'difference from spot usd price'
    lines_chart(kxyl, xlabel, ylabel, title)

def lc006(type_):
    '''
    chart mean and stddev for ads of (type_) by location
    Prints two lines per location (mean and stddev) for ads of this type, 
    '''
    ## below kept as an example of how NOT to access pkl
    #temp = sorted([(k.location.split('/')[1][:30], k.snap, ad.diff_spotusd) 
    #    for k, ads in pkl.items() for ad in ads 
    #    if k.type_==type_ and ad.diff_spotusd != None])
    #keys = sorted(set([x[0] for x in temp]))
    #xs = sorted(set([x[1] for x in temp]))
    #kxyl = []
    #for snap in xs:
    #    print(snap)
    #    for key in keys:
    #        ystats = describe([y for k,x,y in temp if x==snap and k==key], 
    #            only=['mean','stddev'])
    #        if not ystats: continue
    #        kxyl.append(('%s mean' % key, snap, ystats['mean'], '%s mean' % key))
    #        kxyl.append(('%s stddev' % key, snap, ystats['stddev'], '%s stddev' % key))
    #        print('  %-37s, %15.2f, %15.2f' % (key, ystats['mean'], ystats['stddev']))
    temp = [(k, describe([ad.diff_spotusd for ad in ads], only=('mean','stddev'))) 
            for k, ads in pkl.items() if k.type_==type_]
    kxyl = sorted([('m%d' % k.loc, k.snap, v['mean'], '%s mean' % k.location.split('/')[1][:30]) for k, v in temp if v!=None])
    kxyl.extend(sorted([('s%d' % k.loc, k.snap, v['stddev'], '%s stddev' % k.location.split('/')[1][:30]) for k, v in temp if v!=None]))
    title = 'stddev, mean of diff_spotusd for all ads of type:%s by location' % type_
    xlabel, ylabel = '15m samples', 'stddev, mean of diff_spotusd'
    lines_chart(sorted(kxyl), xlabel, ylabel, title, stylecnt=2, verbose=verbose)

def lc007(sortreversed):
    '''
    report and chart most severe mean diff_spotusd by trader
        if True then highest else lowest
    Each trader will have similarly-styled-lines for each of their ads 
    and the report will show the traders with the greatest or least mean
    based on their historic above-spotusd prices (for both bids and asks).
    A higher mean means that their markup was likely very pricey.  A lower 
    mean means that their markup was closer to spot.  A negative mean indicates
    that they are advertising at prices which result in loss and may hint that
    the trader is practicing bait-and-switch.
    '''
    if sortreversed: label = 'highest'
    else: label = 'lowest'
    temp = sorted([((k.type_, ad.user), k.snap, ad.diff_spotusd) 
        for k, ads in pkl.items() for ad in ads if ad.diff_spotusd != None])
    keys = sorted(set(x[0] for x in temp))
    kstats = {}
    for key in keys:
        kstats[key] = describe([y for k,x,y in temp if k==key], only=('mean','stddev'))

    print('40 traders with %s diff_spotusd:' % label)
    kvals = sorted([(k,v['mean'],v['stddev']) for k,v in kstats.items() if v!=None], key=itemgetter(1), reverse=sortreversed)[:40]
    for kval in kvals:
        print('%s %-30s %15.2f mean %15.2f stddev' % (kval[0][0], kval[0][1][:30], kval[1], kval[2]))
    kxyl = sorted([(ad.id, k.snap, ad.diff_spotusd, '%s %s %s' % (k.type_, ad.user, ad.country)) 
        for k, ads in pkl.items() for ad in ads 
        if (k.type_, ad.user) in [x[0] for x in kvals] and ad.diff_spotusd != None])

    title = 'ads from 40 %s diff_spotusd traders' % label
    xlabel, ylabel = '15m samples', 'difference from spot usd price'
    lines_chart(kxyl, xlabel, ylabel, title)

def lc008(sortreversed):
    '''
    report and chart most severe stddev diff_spotusd by trader
        if True then most else least
    Each trader will have a line based on the standard deviation of their 
    historic above-spotusd prices (for both bids and asks).  A greater
    standard deviation means that their markup varied throughout their 
    history.  A lesser standard deviation means they ran a consistent 
    markup over time... It says nothing about how much their markup was,
    just weather it varied significantly or not.  Depending on how this
    recipe is called, it will answer for the the traders with the
    greatest (most erratic) or least (most consistent) markup over time.
    '''
    if sortreversed: label = 'most'
    else: label = 'least'
    temp = sorted([((k.type_, ad.user), k.snap, ad.diff_spotusd) 
        for k, ads in pkl.items() for ad in ads if ad.diff_spotusd != None])
    keys = sorted(set(x[0] for x in temp))
    kstats = {}
    for key in keys:
        kstats[key] = describe([y for k,x,y in temp if k==key], only=('mean','stddev'))

    print('40 traders with %s erratic diff_spotusd:' % label)
    kvals = sorted([(k,v['mean'],v['stddev']) for k,v in kstats.items() if v!=None], key=itemgetter(2), reverse=sortreversed)[:40]
    for kval in kvals:
        print('%s %-30s %15.2f mean %15.2f stddev' % (kval[0][0], kval[0][1][:30], kval[1], kval[2]))
    kxyl = sorted([(ad.id, k.snap, ad.diff_spotusd, '%s %s %s' % (k.type_, ad.user, ad.country)) 
        for k, ads in pkl.items() for ad in ads 
        if (k.type_, ad.user) in [x[0] for x in kvals] and ad.diff_spotusd != None])

    title = 'ads from 40 %s erratic diff_spotusd traders' % label
    xlabel, ylabel = '15m samples', 'difference from spot usd price'
    lines_chart(kxyl, xlabel, ylabel, title)

def lc009(type_, stat):
    '''
    for ads of (type_), chart (stat) of diff_spotusd by location
        type_ in ('a','b'), stat in ('min','max','mean','median','stddev')
    Each location will have a single line based on the average 
    above-spotusd-markup for all ads of this type at that location.
    '''
    keys = sorted(set(k for k in pkl.keys() if k.type_==type_))
    kstats = {}
    for key in keys:
        astat = describe([ad.diff_spotusd for ad in pkl[key] 
            if ad.diff_spotusd!=None], only=[stat])
        if astat: kstats[key] = astat[stat]
    kxyl = sorted([('%s %s' % (k.type_, k.loc), k.snap, kstats[k], 
        '%s %s' % (k.type_, k.location.split('/')[1][:30])) 
        for k,y in kstats.items()])
    title = '%s diff_spotusd of type:%s by location' % (stat, type_)
    xlabel, ylabel = '15m samples', 'difference from spot usd price'
    lines_chart(kxyl, xlabel, ylabel, title)
