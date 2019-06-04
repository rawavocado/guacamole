from library import AdKey, Ad
import library
from lbdb import locations
import stats
import recipes

def menu():
    '''
    useful info to get console users started
    ex) menu()
    '''
    functions = [library.get_pkl, library.pkl_snap, library.lines_chart, stats.describe, stats.describe_str]
    functions.extend([getattr(recipes, x) for x in [i for i in dir(recipes) if i[:2]=='lc']])
    print "\nEntering menu() call..."
    for f in functions:
        print('func %s(): %s' % (f.__name__, f.__doc__))
    print "...Leaving menu() call.\n"

if __name__ == '__main__':
    menu()
    snaps = recipes.snaps
    pkl = recipes.pkl
    print('pkl has %d ad-sets in %d snaps ranging from %s to %s' % (
        len(pkl), len(snaps), min(snaps), max(snaps)))

    for type_ in ('a','b'):
        print recipes.lc004.__doc__
        recipes.lc004(type_)
