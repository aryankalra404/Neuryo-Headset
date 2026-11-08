"""Compare two KiCad netlists by connectivity (net names ignored where membership is unchanged).
usage: netdiff.py a.net b.net  -> prints every pin whose connections changed"""
import sys
sys.path.insert(0, '/home/claude/kw')
from sx import *
RENAME = {'J3%s' % c: 'J%d' % (10 + i) for i, c in enumerate('ABCDEFGHIJ')}   # rev B: J3A-J3J renamed J10-J19 (KiCad needs a trailing number)


def load(f):
    g = netlist_groups(open(f).read())
    pin = {}
    for n, ps in g.items():
        for p in ps:
            pin[p] = n
    g = {n: frozenset(RENAME.get(p.split('.')[0], p.split('.')[0]) + '.' + p.split('.')[1] for p in ps) for n, ps in g.items()}
    pin = {}
    for n, ps in g.items():
        for p in ps:
            pin[p] = n
    return g, pin


def peers(g, pin, p):
    return frozenset(g[pin[p]]) - {p} if p in pin else None


def diff(fa, fb, quiet=False):
    ga, pa = load(fa)
    gb, pb = load(fb)
    out = []
    removed = sorted(set(pa) - set(pb))
    added = sorted(set(pb) - set(pa))
    comps_rm = sorted(set(p.split('.')[0] for p in removed) - set(p.split('.')[0] for p in pb))
    comps_add = sorted(set(p.split('.')[0] for p in added) - set(p.split('.')[0] for p in pa))
    out.append('parts removed: ' + ' '.join(comps_rm))
    out.append('parts added:   ' + ' '.join(comps_add))
    rest = [p for p in removed if p.split('.')[0] not in comps_rm]
    if rest:
        out.append('pins removed from kept parts: ' + ' '.join(rest))
    changed = []
    for p in sorted(set(pa) & set(pb)):
        a = set(x for x in ga[pa[p]] if x in pb) - {p}
        b = set(x for x in gb[pb[p]] if x in pa) - {p}
        if a != b:
            changed.append((p, pa[p], pb[p], sorted(a - b), sorted(b - a)))
    out.append('pins of kept parts whose connections changed: %d' % len(changed))
    for p, na, nb, lost, gained in changed:
        out.append('  %-10s %s -> %s   lost %s  gained %s' % (p, na, nb, ' '.join(lost[:8]) + (' ...' if len(lost) > 8 else ''),
                                                          ' '.join(gained[:8]) + (' ...' if len(gained) > 8 else '')))
    for p in added:
        if p.split('.')[0] in comps_add:
            n = pb[p]
            out.append('  new %-10s on %-14s with %s' % (p, n, ' '.join(sorted(gb[n] - {p})[:10]) + (' ...' if len(gb[n]) > 11 else '')))
    return '\n'.join(out)


if __name__ == '__main__':
    print(diff(sys.argv[1], sys.argv[2]))
