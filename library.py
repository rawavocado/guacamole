import pickle
from operator import itemgetter
from matplotlib import pyplot
import math

from lbdb import AdKey, Ad, dpklfile
from colors import get_colors

def get_pkl(): 
    '''
    read access to all pickled data
    ex) pkl = get_pkl()
    '''
    with open(dpklfile, 'rb') as handle: return pickle.load(handle)

def pkl_snap(pkl, allsnaps=False):
    '''
    get latest pkl snap value (or all if allsnaps is True)
    ex) pkl = get_pkl()
        snap = pkl_snap(pkl)
        snaps = pkl_snap(pkl, True)
    '''
    if allsnaps: return sorted(set([k[0] for k in pkl.keys()]))
    else: return max([k[0] for k in pkl.keys()])

def lines_chart(kxyl, xlabel=None, ylabel=None, title=None, stylecnt=3, verbose=False):
    '''
    create a lines chart with pre-sorted kxyl data:
        kxyl: a (key,x) sorted iterable of 4tuples having: (key, x, y, label)
            so that a line may be drawn for each key and all lines
            with same label get the same color
        xlabel: a string label for x axis
        ylabel: a string label for y axis
        title: a title for the chart
    '''
    styles, widths = ['solid', 'dashed', 'dotted'][:stylecnt], [1.5, 2, 2.5][:stylecnt]
    if title: pyplot.title(title)
    if xlabel: pyplot.xlabel(xlabel)
    if ylabel: pyplot.ylabel(ylabel)
    keylbls = {k: l for k,l in set([(k,l) for k,x,y,l in kxyl])}
    lbls = (set(l for l in keylbls.values()))
    if verbose: print('lines_chart() legend will have %d labels.' % len(lbls))
    attrs = {l: (clr, style, width) for l, clr, style, width in zip(
        sorted(lbls), sorted(get_colors(int(math.ceil(len(lbls)/float(stylecnt))))*stylecnt), styles*len(lbls), widths*len(lbls))}
    used = {l: False for l in lbls}
    for i, (key, lbl) in enumerate(sorted([(k,l) for k,l in keylbls.items()], key=itemgetter(1))):
        xs = [x for k,x,y,l in kxyl if k==key]
        ys = [y for k,x,y,l in kxyl if k==key]
        clr, style, width = attrs[lbl]
        if verbose: print('...for %s, plotting %s with %d x,y values' % (lbl, key, len(xs)))
        if not used[lbl]: used[lbl] = True
        else: lbl = None
        pyplot.plot(xs, ys, label=lbl, color=clr, linestyle=style, linewidth=width)
    legend = pyplot.legend(loc=2)
    for line, text in zip(legend.get_lines(), legend.get_texts()):
        text.set_color(line.get_color())
    pyplot.show()
