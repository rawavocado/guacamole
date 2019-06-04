'''
sometimes changes are made where a database that persists on disc must be
changed to support new code.  This module will hold functions dated for 
the change for one-time-use to bring persistant data into compatibility.
'''
import pickle, shelve
from datetime import datetime, timedelta
from lbdb import AdKey, Ad

def f_20180818():
    old_dpkl = 'db_lbc.dpkl'
    new_dpkl = 'db_lbc-new.dpkl'

    fourhours = timedelta(0, 60*60*4)
    with open(old_dpkl, 'rb') as handle:
        pkl = pickle.load(handle)
    newpkl = {}
    for key, value in pkl.items():
        newkey = AdKey((key[0] + fourhours, key[1], key[2]))
        newpkl[newkey] = value
        print 'key:%s becomes %s of type:%s' % (key, newkey, type(newkey))
    with open(new_dpkl, 'wb') as handle:
        pickle.dump(newpkl, handle, protocol=pickle.HIGHEST_PROTOCOL)

def f_20180907():
    rawdbfile = 'db_lbcraw.shelf'
    locadsfile = 'location_ads.dpkl'
    olddbfile = 'db_lbc.dpkl'
    newdbfile = 'db_lbcnew.dpkl'

    dbr = shelve.open(rawdbfile, 'r')

    try:
        with open(locadsfile, 'rb') as handle:
            locs = pickle.load(handle)
    except:
        locs = {}

        for key in sorted(dbr.keys()): 
            print key
            for loc in dbr[key].keys():
                ads = []
                if 'bids' in dbr[key][loc]:
                    ads.extend([x['data']['ad_id'] for x in 
                        dbr[key][loc]['bids'] if x['data']['distance'] <= 50])
                if 'asks' in dbr[key][loc]:
                    ads.extend([x['data']['ad_id'] for x in 
                        dbr[key][loc]['asks'] if x['data']['distance'] <= 50])
                if loc in locs: 
                    ads.extend(locs[loc])
                locs[loc] = set(ads)
                print ' %s %d' % (loc, len(locs[loc]))
        for loc in locs:
            print loc, locs[loc]
        with open(locadsfile, 'wb') as handle:
            pickle.dump(locs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(olddbfile, 'rb') as handle:
        olddb = pickle.load(handle)
    newdb = {}

    for key, values in olddb.items():
        newdb[key] = [x for x in values if x.id in locs[key.location]]
        print key, len(newdb[key])

    with open(newdbfile, 'wb') as handle:
        pickle.dump(newdb, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    f_20180907()
