"""Copper / placement diff between two boards (same coordinate frame): footprints moved, tracks and vias added/removed.
usage: copperdiff.py base.kicad_pcb new.kicad_pcb"""
import sys, math
sys.path.insert(0, '/home/claude/kw')
from sx import *
RENAME = {'J3%s' % c: 'J%d' % (10 + i) for i, c in enumerate('ABCDEFGHIJ')}   # rev B: J3A-J3J renamed J10-J19 (KiCad needs a trailing number)
X0, Y0 = 98.5011, 80.0036
def nn(e):
    n = kid(e, 'net'); return (n[-1]) if n else ''
def load(f):
    b = parse(open(f).read())
    S = {}
    for s in kids(b, 'segment'):
        a, e = kid(s, 'start'), kid(s, 'end')
        p = (round(float(a[1]) - X0, 2), round(float(a[2]) - Y0, 2)); q = (round(float(e[1]) - X0, 2), round(float(e[2]) - Y0, 2))
        S[(val(s, 'layer'), tuple(sorted([p, q])), val(s, 'width'))] = nn(s)
    V = {}
    for v in kids(b, 'via'):
        a = kid(v, 'at'); V[(round(float(a[1]) - X0, 2), round(float(a[2]) - Y0, 2))] = nn(v)
    F = {}
    for f_ in kids(b, 'footprint'):
        r = [p[2] for p in kids(f_, 'property') if p[1] == 'Reference'][0]
        r = RENAME.get(r, r)
        a = kid(f_, 'at'); F[r or 'hole@%.0f,%.0f' % (float(a[1]) - X0, float(a[2]) - Y0)] = (round(float(a[1]) - X0, 2), round(float(a[2]) - Y0, 2), a[3] if len(a) > 3 else '0', val(f_, 'layer'))
    return S, V, F
S0, V0, F0 = load(sys.argv[1]); S1, V1, F1 = load(sys.argv[2])
def region(p):
    return 'analog half (x<56)' if p[0] < 56 else 'right part (x>=56)'
print('FOOTPRINTS')
for r in sorted(set(F0) - set(F1)): print('  removed', r, F0[r][:2])
for r in sorted(set(F1) - set(F0)): print('  added  ', r, F1[r])
for r in sorted(set(F0) & set(F1)):
    if F0[r] != F1[r]: print('  moved  ', r, F0[r], '->', F1[r])
for title, A, B in (('TRACKS removed', S0, S1), ('TRACKS added', S1, S0)):
    out = {}
    for k, n in A.items():
        if k not in B:
            reg = region(k[1][0]) if k[1][0][0] < 56 or k[1][1][0] < 56 else region(k[1][0])
            if k[1][0][0] < 56 or k[1][1][0] < 56: reg = 'analog half (x<56)'
            out.setdefault(reg, []).append((n, k))
    print(title)
    for reg, L in sorted(out.items()):
        print('  %s: %d' % (reg, len(L)))
        if reg.startswith('analog'):
            for n, k in sorted(L): print('     %-10s %s %s-%s w%s' % (n, k[0], k[1][0], k[1][1], k[2]))
# nets changed on kept tracks
ch = [(k, S0[k], S1[k]) for k in S0 if k in S1 and S0[k] != S1[k]]
print('TRACKS kept but net renamed:', len(ch))
for k, a, b in ch: print('   ', a, '->', b, k[0], k[1])
for title, A, B in (('VIAS removed', V0, V1), ('VIAS added', V1, V0)):
    L = [(p, n) for p, n in A.items() if p not in B]
    print(title, len(L), ' analog half:', sorted([(n, p) for p, n in L if p[0] < 56]))
chv = [(p, V0[p], V1[p]) for p in V0 if p in V1 and V0[p] != V1[p]]
print('VIAS kept but net renamed:', chv)
