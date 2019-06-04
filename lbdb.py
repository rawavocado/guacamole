'''
lbdb.py     gathers localbitcoins cash ads for select locations
            stores them raw in shelf like:
                db[datetime]                    # rounded up to nearest 15m round time
                db[datetime]['lbcavg']          # bitcoinaverage dict by currency
                db[datetime][location]          # location_id/location_slug
                db[datetime][location]['asks']  # list of seller ads
                db[datetime][location]['bids']  # list of buyer ads
            then in a more efficient 'only what we need' pickled dict 
                like pkl[(datetime, int(location), (b)id/(a)ask)] as key
                (where key can be accessed difficultly by position or
                easily by named attribute in class AdKey) and list of 
                ads as the value (where each ad is a tuple of values 
                accessed difficultly by position or easily by named 
                attribute in class Ad)

'''
import json
import shelve
import pickle
import copy
import random
from urllib import urlencode
from urllib2 import urlopen, Request
from datetime import datetime, timedelta
from time import sleep

timeout = 30
locations = [x.rstrip() for x in open('location_idslugs.txt').readlines()]

class AdKey(tuple):
    '''useful for accessing the snap time, location, asks|bids keys to ad lists'''
    all = ('snap', 'loc', 'type_')
    types_ = ('a', 'b')
    def __getattr__(self, a):
        if a in self.all: return self[self.all.index(a)]
        elif a in ('bids', 'asks'): return self[2] == a[0]
        elif a == 'location': return locations[self.loc]
        else: raise AttributeError('AdKey has no attribute %s' % a)
    def __str__(self): return "%s,%d,%s" % self
    def __new__(cls, anIter):
        if type(anIter) == str: 
            anIter = anIter.split(',')
            anIter = (anIter[0], int(anIter[1]), anIter[2])
        assert len(anIter) == 3
        snap, loc, type_ = anIter
        if type(anIter[0]) != datetime: 
            snap = datetime.strptime(anIter[0], '%Y-%m-%d %H:%M:%S')
        if type(anIter[1]) != int: loc = locations.index(anIter[1])
        else: assert loc < len(locations)
        if anIter[2][0] in cls.types_: type_ = anIter[2][0]
        else: raise ValueError('type_:%s not in %s' % (anIter[2], cls._types))
        return super(AdKey, cls).__new__(cls, (snap, loc, type_))

class Ad(list):
    '''useful for accessing ad elements by name'''
    all = ('id', 'user', 'lastlogin', 'country', 'curr', 'price', 'usd', 
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

def _get_Request(url_suffix, params=[], url_base='https://localbitcoins.com'):
    '''returns a request object for accessing a particular localbitcoins api'''
    url = url_base + url_suffix
    if params: url += '?' + urlencode(params)
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0') # else 'HTTP Error 403: Forbidden'
    return request

def get_spot_prices():
    '''returns dict of {curr: price} that josoj sets up to track spot price'''
    request = _get_Request('/buy-bitcoins-with-cash/463110285/bermuda/.json')
    data = json.load(urlopen(request, timeout=timeout))
    answer = {}
    adList = data['data']['ad_list']
    for ad in adList:
        if ad['data']['ad_id'] == 814672: # josoj
            curr = ad['data']['currency']
            spot_price = ad['data']['temp_price']
            answer.update({curr: spot_price})
    return answer

def get_avgprices():
    '''returns raw localbitcoins bitcoinaverage per currency data'''
    request = _get_Request('/bitcoinaverage/ticker-all-currencies/')
    data = json.load(urlopen(request, timeout=timeout))
    return data

def get_ads_by_location(prefix, idslug):
    '''returns raw localbitcoins cash ads prefix=buy|sell for a particular location idslug'''
    assert prefix in ('buy', 'sell')
    if prefix == 'buy': url = '/buy-bitcoins-with-cash/%s/.json' % idslug
    elif prefix == 'sell': url = '/sell-bitcoins-for-cash/%s/.json' % idslug
    data = json.load(urlopen(_get_Request(url), timeout=timeout))
    return data['data']['ad_list']

def get_current_snap_datetime():
    '''returns the current snapshot as a datetime, see get_current_snap_string() for dbkey'''
    mins = 15
    snap_delta = timedelta(0, mins*60)
    now = datetime.utcnow() # changed from local to utc asof 20180818_1030
    return datetime(now.year, now.month, now.day, now.hour, (now.minute / mins) * mins) + snap_delta

def get_current_snap_string(): 
    '''returns the current snapshot as a string, used as key in db like db[snap]'''
    return str(get_current_snap_datetime())[:19]

rawdbfile = 'db_lbcraw.shelf'
def update_db(verbose=False):
    '''updates db for current snapshot, if not already updated'''
    def shuffled(aList):
        aList = copy.copy(aList)
        random.shuffle(aList)
        return aList

    updates, failures = [], []
    snap = get_current_snap_string()

    try: db = shelve.open(rawdbfile, 'w')
    except Exception: db = shelve.open(rawdbfile, 'c')

    if verbose or snap not in db: 
        print('update_db(verbose=%s) %s at %s...' % (verbose, snap, datetime.now()))

    if snap not in db: aDict = {}
    else: aDict = db[snap]

    if 'lbcavg' not in aDict:
        if verbose: print('  ...getting lbcavg')
        data = None     # localbitcoins fails (500) often on first connection
        try: data = get_avgprices()
        except: 
            print('  failed getting lbcavg, trying again.')
            sleep(10)
            try: data = get_avgprices()
            except Exception, e:
                print('  %s %s' % ('lbcavg', e))
        if data: 
            aDict['lbcavg'] = data
            updates.append('lbcavg:%d' % len(data))
        else: failures.append('lbcavg')
        del data

    for loc in shuffled(locations):
        if verbose: print '  ...checking %s' % loc
        if loc not in aDict: aDict[loc] = {}

        for type_ in shuffled(['bids', 'asks']):
            if type_ in aDict[loc]: continue
            if verbose: print('  ...getting %s' % type_)
            try:
                if type_ == 'bids': data = get_ads_by_location('sell', loc)
                else: data = get_ads_by_location('buy', loc)
                if data:
                    aDict[loc][type_] = data
                    updates.append('%s:%s:%d' % (loc, type_, len(data)))
                else: failures.append('%s:%s' % (loc, type_))
                del data
            except Exception, e: 
                failures.append('%s:%s' % (loc, type_))
                print('  %s %s %s' % (loc, type_, e))

    if verbose or updates or failures:
        print('  ...done(verbose=%s) %s at %s: updates:%d, failures:%s' % (
            verbose, snap, datetime.now(), len(updates), failures))

    if updates: db[snap] = aDict
    db.close()

    if not failures: 
        if not update_pkl(snap, aDict, verbose):
            failures.append('update_pkl() failed')

    return failures == []

dpklfile = 'db_lbc.dpkl'
def update_pkl(snap, aDict, verbose=False):
    max_distance = 50   # localbitcoins fills ~30 far-away ads when too few
    updates, failures = [], []

    if verbose: print('  ...unpickling')
    try: 
        with open(dpklfile, 'rb') as handle: 
            pkl = pickle.load(handle)
    except Exception: pkl = {}

    if verbose or snap not in [str(x[0]) for x in pkl.keys() if str(x[0])==snap]: 
        print('  ..._pkl(verbose=%s) %s at %s...' % (verbose, snap, datetime.now()))

    numkeys, numads = 0, 0
    spot_prices = get_spot_prices()
    prices = {
        '1husd': aDict.get('lbcavg', {}).get('USD', {}).get('avg_1h', None),
        'spotusd': spot_prices.get('USD', None)
        }

    for loc in [x for x in aDict.keys() if x!='lbcavg']:
        if verbose: print('  ...checking %s' % loc)
        for type_ in aDict[loc]:
            if AdKey([snap, loc, type_]) in pkl: continue
            if verbose: print('  ...setting %s' % type_)
            if type_ == 'asks':  diff_f = lambda mkt, ask: float('%15.2f' % (ask - mkt))
            else: diff_f = lambda mkt, bid: float('%15.2f' % (mkt - bid))
            ads = [raw_ad2ad(x) for x in aDict[loc][type_] 
                if x['data']['distance'] <= max_distance]
            old_curr = ''
            for ad in ads:
                if ad.curr != old_curr:
                    prices.update({
                        '1h': aDict.get('lbcavg', {}).get(ad.curr, {}).get('avg_1h', None),
                        'spot': spot_prices.get(ad.curr, None)
                        })
                old_curr = ad.curr

                # append elements
                if prices['1h'] and ad.price: ad.append(diff_f(float(prices['1h']), ad.price))
                else: ad.append(None)
                if prices['1husd'] and ad.usd: ad.append(diff_f(float(prices['1husd']), ad.usd))
                else: ad.append(None)
                if prices['spot'] and ad.price: ad.append(diff_f(float(prices['spot']), ad.price))
                else: ad.append(None)
                if prices['spotusd'] and ad.usd: ad.append(diff_f(float(prices['spotusd']), ad.usd))
                else: ad.append(None)
            pkl[AdKey([snap, loc, type_])] = ads
            updates.append('%s:%d' % (AdKey([snap, loc, type_]), len(ads)))

    if verbose: print('  ...pickling')
    with open(dpklfile, 'wb') as handle:
        pickle.dump(pkl, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if verbose or updates or failures: 
        print('  ...done(verbose=%s) %s at %s: updates:%d, failures:%s' % (
            verbose, snap, datetime.now(), len(updates), failures))

    return failures == []

if __name__ == '__main__':
    verbose = False
    while True:
        try: 
            snapdt = get_current_snap_datetime() 
            if update_db(verbose):
                verbose = False
                tdelta = snapdt - datetime.utcnow()
                if tdelta.days >= 0 and tdelta.seconds >=0 and tdelta.microseconds >=0:
                    sleep(tdelta.seconds + ((tdelta.microseconds + 1) * pow(10,-6)))
            else:
                verbose = True
                sleep(10)
        except Exception, e: 
            print('main loop: %s' % e)

