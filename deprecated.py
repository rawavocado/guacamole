### from old console.py

import shelve
from lbdb import AdKey, Ad, rawdbfile, dpklfile, locations
from colors import get_colors

def _get_db(): return shelve.open(rawdbfile, 'r')

def get_snap(allsnaps=False): 
    '''
    returns latest snapshot time string, or all ascending keys if not lastsnap
        useful as key or keys for accessing db and ads
    params: n/a
    ex)
       snap = get_snap()
       snaps = get_snap(allFalse)
    '''
    db = _get_db()
    if allsnaps: answer = sorted(db.keys())
    else: answer = max(db.keys())
    db.close()
    return answer

class Ad(list):
    '''useful for accessing ad elements by name'''
    all = ('ad', 'user', 'lastlogin', 'country', 'curr', 'price', 'usd', 
            'diff_1h', 'diff_1husd', 'diff_spot', 'diff_spotusd')
    def __getattr__(self, a):
        if a in self.all: return self[self.all.index(a)]
        else: raise AttributeError('Ad has no attribute %s' % a)
def raw_ad2ad(raw_ad):
    '''converts raw localbitcoins ad dict into a flattened Ad list of useful values'''
    answer = [
        raw_ad['data']['ad_id'], 
        raw_ad['data']['profile']['username'], 
        raw_ad['data']['profile']['last_online'][:-6], 
        raw_ad['data']['countrycode'],
        raw_ad['data']['currency'],
        raw_ad['data']['temp_price'],
        raw_ad['data']['temp_price_usd'],
        ]
    # convert types if necessary
    for i in [5, 6]:
        try: answer[i] = float(answer[i])
        except Exception: answer[i] = None
    return Ad(answer)

def get_ads(snaps, loc=None, type_=None, user=None, curr=None, country=None, spot_prices={}, verbose=False):
    '''
    gets raw localbitcoins ads from db, filters, returns dict of useful ad data
    params: snap=None, loc=None, type_=None, user=None, curr=None, country=None, verbose=False
    return dict structure: [snap][loc][type_][ad0, ad1, ..., adn]
    ex)
       ads = get_ads(snaps=[get_snap()], type_='asks', curr='GBP', country='GB')
    '''
    answer = {}

    db = _get_db()
    for i, asnap in enumerate(snaps):
        if verbose: print('snap: %s' % asnap)
        adsnap = db.get(asnap, {})
        pxsnap = db.get(snaps[min([i+2, len(snaps)-1])]).get('lbcavg', {}) 
        prices = {
            '1husd': pxsnap.get('USD', {}).get('avg_1h', None),
            'spotusd': spot_prices.get('USD', None)
            }

        if loc: locs = [loc]
        else: locs = sorted([x for x in adsnap.keys() if x!='lbcavg'])

        for aloc in locs:
            if not adsnap.has_key(aloc): continue
            if verbose: print('%s %s' % (asnap, aloc))

            if type_: types_ = [type_]
            else: types_ = ['asks', 'bids']

            for atype in types_:
                if not adsnap[aloc].has_key(atype): continue
                if verbose: print('%s %s %s ' % (asnap, aloc, atype))

                # for adding diff elements later
                if atype == 'asks':  diff_f = lambda mkt, ask: float('%15.2f' % (ask - mkt))
                else: diff_f = lambda mkt, bid: float('%15.2f' % (mkt - bid))

                ad_list = [raw_ad2ad(x) for x in adsnap[aloc][atype]]

                old_curr = ''
                for ad in ad_list:
                    if curr and curr != ad.curr: continue
                    if country and country != ad.country: continue
                    if user and user != ad.user: continue

                    if ad.curr != old_curr:
                        prices.update({
                            '1h': pxsnap.get(ad.curr, {}).get('avg_1h', None),
                            'spot': spot_prices.get(ad.curr, None)
                            })
                    # append elements
                    if prices['1h'] and ad.price: ad.append(diff_f(float(prices['1h']), ad.price))
                    else: ad.append(None)
                    if prices['1husd'] and ad.usd: ad.append(diff_f(float(prices['1husd']), ad.usd))
                    else: ad.append(None)
                    if prices['spot'] and ad.price: ad.append(diff_f(float(prices['spot']), ad.price))
                    else: ad.append(None)
                    if prices['spotusd'] and ad.usd: ad.append(diff_f(float(prices['spotusd']), ad.usd))
                    else: ad.append(None)

                    if not answer.has_key(asnap): answer[asnap] = {}
                    if not answer[asnap].has_key(aloc): answer[asnap][aloc] = {}
                    if not answer[asnap][aloc].has_key(atype): answer[asnap][aloc][atype] = []
                    answer[asnap][aloc][atype].append(ad)
                    old_curr = ad.curr

    db.close()
    return answer

def flatten_dict(aDict):
    '''
    receives a db or ads dict, separates keys from data, returns a list of (keys, data)
    params: ads or db dict
    returned list structure: [((snap, loc, type_), data), ...]
    ex)
       flat_ads = flaten_dict(get_ads(snaps=get_snap(True), type_='asks', curr="GBP", country='GB'))
    '''
    answer = []
    for snap in sorted([x for x in aDict.keys()]):
        for loc in sorted([x for x in aDict[snap].keys()]):
            for type_ in sorted([x for x in aDict[snap][loc].keys()]):
                answer.extend(
                    [((snap, loc, type_), x) for x in aDict[snap][loc][type_]])
    return answer

def show_ads(ads, headers=True):
    '''
    receives a pre-prepared ads dict, prints formatted ads data
    params: ads dict, headers=True
    ex)
       show_ads(get_ads(snaps=[get_snap()], curr="GBP", country='GB'))
    '''
    def formatted(x):
        '''
        return u'%12.2f%s (%12s) %8.2f$ ad:%-6d u:%s %s %s' % (
            ad.price, ad.curr, ad[-1], ad.usd, ad.ad,
            ad.lastlogin, ad.country, ad.user)
        '''
        return str(x)
    for snap in sorted([x for x in ads.keys()]):
        for loc in sorted([x for x in ads[snap].keys()]):
            for type_ in sorted([x for x in ads[snap][loc].keys()]):
                if headers: print('%s %s %s' % (snap, loc, type_))
                for ad in ads[snap][loc][type_]: print(formatted(ad))


### from old mpl.py
from matplotlib import pyplot as plt
import matplotlib
import console as c
import colors
from lbdb import locations
import math, random

# get some data
def show_randchart():
    '''
    displays a random chart
    '''
    print("\nEntering show_randchart()...")
    snaps = c.get_snap(True)

    loc = random.choice(locations + [None])
    type_ = random.choice(['asks', 'bids'])
    curr, country = random.choice(list(set([(x[1].curr, x[1].country) for x in 
        c.flatten_dict(c.get_ads(snaps=[snaps[-1]], loc=loc, type_=type_))])))
    user = None
    #loc, type_, curr, country = '1167263622/moscow-russia-109012', 'asks',  'EUR', 'RU'
    loc, country = None, None, 
    #loc, country, type_, curr = None, 'US', 'asks', 'USD'
    curr = None

    print('latest show_ads() for params:loc=%s, type_=%s, curr=%s, country=%s, user=%s' % (
        loc, type_, curr, country, user))
    c.show_ads(c.get_ads([snaps[-1]], loc=loc, type_=type_, user=user, curr=curr, country=country))

    print('gathering historic data sets for chart...')
    ads = c.get_ads(snaps, loc=loc, type_=type_, curr=curr, country=country, user=user)
    print('...and done.')

    keys = sorted(set(['%s:%s' % (x.user, x.ad) for k, x in c.flatten_dict(ads)]))
    users = sorted(set([k.split(':')[0] for k in keys]))
    colors = {u.split(':')[0]: c for u, c in zip(users, get_colors(len(users)))}
    print get_colors(len(users))
    print users

    lines = {x: [] for x in keys}
    snaps = sorted(ads.keys())
    for asnap in snaps:
        samples = {x: None for x in keys}
        for aloc in [x for x in ads[asnap].keys() if x==loc or loc==None]:
            #samples.update({'%s:%s' % (x.user, x.ad): x.price for x in ads[asnap][aloc][type_]})
            samples.update({'%s:%s' % (x.user, x.ad): x.usd for x in ads[asnap][aloc][type_]})
        for k in keys:
            lines[k].append(samples[k])

    plt.title('%s %s %s %s' % (loc, type_, curr, country))
    for k in keys:
        user = k.split(':')[0]
        plt.plot(range(len(snaps)), lines[k], color=colors[user], label=user)
    plt.xlabel('time (15m)')
    plt.ylabel('price (%s)' % (curr))
    plt.legend(loc=2)
    #plt.legend(color='red', label='red')
    #plt.legend(color='blue', label='green')
    #plt.legend(color='green', label='green')
    plt.show()

def loop():
    while True: 
        show_randchart()

if __name__ == '__main__':
    from lbdb import AdKey, Ad
    pkl = c._get_pkl()
    kxyl = sorted([(ad.id, k.snap, ad.diff_spotusd, ad.user) 
        for k, ads in pkl.items() for ad in ads 
        if k.bids and ad.country=='US'])
    lines_chart(kxyl, '15m samples', 'diff usd spot price', 'diff usd spot of bids in US')
    pass

