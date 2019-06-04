import json
import urllib
import time
import shelve
from datetime import date
from library import lines_chart
from datetime import date

def parseCommandLine():
    from optparse import OptionParser
    usage = 'Usage: %prog [options] [sym0 sym1 ...symN]'
    descr = 'View line chart of localbitcoins volume for one or more symbols'
    parser = OptionParser(usage=usage, description=descr)
    parser.add_option('-b', '--btc', action='store_true', default=False,
        help='view volume in btc instead of local currency, default:[%default]')
    parser.add_option('-l', '--list', action='store_true', default=False,
        help='list all available symbols, default:[%default]')
    parser.add_option('-a', '--all', action='store_true', default=False,
        help='graph all available symbols, default:[%default]')
    (opts, args) = parser.parse_args()
    symbols = [x.upper() for x in args]
    if not (opts.list or opts.all or len(symbols)):
        parser.print_help()
        exit(1)
    return (opts, symbols)

rawdbfile = 'coindance_lbwk_volume.shelf'
def initialize():
    try: db = shelve.open(rawdbfile, 'w')
    except: db = shelve.open(rawdbfile, 'c')

    baseurl = 'https://coin.dance/volume/localbitcoins/'
    currencies = [x.rstrip() for x in 
        open('coindance_currencies.txt').readlines()]

    prefix = "\t\t\t\t\tdataSource: '"
    suffix = "',\n"

    for curr in currencies:
        url = baseurl + curr
        btcdata, currdata = None, None
        print("\ngetting %s..." % url)
        page_lines = urllib.urlopen(baseurl + curr).readlines()
        for i, line in enumerate(page_lines):
            if line.startswith(prefix) and line.endswith(suffix):
                data = json.loads(line[len(prefix):-len(suffix)])['data']
                if not btcdata: btcdata = data
                else: currdata = data
                print('found %d elements of data on line %d' % (len(data), i))

        if btcdata and currdata:
            print('btc:%d ranging %s to %s, %s:%d ranging %s to %s' % (
                len(btcdata), 
                min([float(x['value']) for x in btcdata]),
                max([float(x['value']) for x in btcdata]),
                curr,
                len(currdata),
                min([float(x['value']) for x in currdata]),
                max([float(x['value']) for x in currdata])
                ))

            db[curr] = {
                curr: [(date(*[int(i) for i in x['label'].split('-')]), 
                    float(x['value'])) for x in currdata],
                'BTC': [(date(*[int(i) for i in x['label'].split('-')]), 
                    float(x['value'])) for x in btcdata]
                }

    db.close()

if __name__ == '__main__':
    opts, symbols = parseCommandLine()

    try: db = shelve.open(rawdbfile, 'r')
    except: 
        initialize()
        db = shelve.open(rawdbfile, 'r')

    if opts.list: 
        print(db.keys())
        exit()
    if opts.all: symbols = db.keys()
    else: 
        invalids = [x for x in symbols if x not in db.keys()]
        symbols = [x for x in symbols if x in db.keys()]
        if invalids: print('Some symbols are invalid: %s' % invalids)

    if symbols:
        kxyl = []
        for sym in symbols:
            if not opts.btc: subsym = sym
            else: subsym = 'BTC'
            kxyl.extend([(sym, x, y, sym) for x,y in db[sym][subsym]])
        xlabel = 'end of week'
        if opts.btc: ylabel = 'volume in BTC'
        else: ylabel = 'volume in local currency'
        title = 'localbitcoins weekly volume. credit: coin.dance'
        lines_chart(kxyl, xlabel, ylabel, title)
