"""Rev B board, 5th pass (review of 11 Nov 2026, review/REVB-REVIEW-11NOV.md).
usage: python3 edit_pcb5.py in.kicad_pcb out.kicad_pcb STEPS schematic [lib_dir]
STEPS: 1 = part-number fields, 2 = R37 value (both copied from the schematic onto the footprints, for schematic
parity), 3 = J1 drill 0.7 -> 0.8 mm (pad size unchanged), on the board and, with lib_dir, in the library footprint.
Nothing at x < 56 mm changes."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sx import *
import uuid

src, dst, STEPS, SCH = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
LIB = sys.argv[5] if len(sys.argv) > 5 else None
B = parse(open(src).read())
S = parse(open(SCH).read())
LOG = []
X0, Y0 = 98.5011, 80.0036


def ref(f):
    for p in kids(f, 'property'):
        if p[1] == 'Reference':
            return p[2]


def fp(r):
    return [f for f in kids(B, 'footprint') if ref(f) == r][0]


def copy_fields(names, only=None):
    for y in kids(S, 'symbol'):
        props = {p[1]: p[2] for p in kids(y, 'property')}
        r = props.get('Reference', '')
        if r.startswith('#') or (only and r not in only) or not [f for f in kids(B, 'footprint') if ref(f) == r]:
            continue
        f = fp(r)
        for k in names:
            if k not in props:
                continue
            cur = [q for q in kids(f, 'property') if q[1] == k]
            if cur and cur[0][2] == props[k]:
                continue
            if cur:
                cur[0][2] = props[k]
            else:
                f.insert(f.index(kids(f, 'property')[-1]) + 1,
                         ['property', k, props[k], ['at', '0', '0', '0'], ['layer', 'F.Fab'], ['hide', Sym('yes')],
                          ['uuid', str(uuid.uuid4())], ['effects', ['font', ['size', '1', '1'], ['thickness', '0.15']]]])
            LOG.append('field %s %s -> %s' % (r, k, props[k]))


if '1' in STEPS:
    copy_fields(('MPN', 'LCSC', 'Reference MPN'))
if '2' in STEPS:
    copy_fields(('Value', 'MPN', 'LCSC', 'Description'), only={'R37'})


def j1_drill(f, where):
    for p in kids(f, 'pad'):
        if str(p[1]) in ('1', '2') and str(p[2]) == 'thru_hole':
            d = kid(p, 'drill')
            LOG.append('%s pad %s drill %s -> 0.8 (pad %s unchanged)' % (where, p[1], d[1], ' x '.join(map(str, kid(p, 'size')[1:]))))
            d[1:] = [Sym('0.8')]


if '3' in STEPS:
    f = fp('J1')
    a = kid(f, 'at')
    assert float(a[1]) - X0 >= 56, 'J1 is in the digital half'
    j1_drill(f, 'J1')
    if LIB:
        mp = os.path.join(LIB, 'Low_Cost_EEG-import-fps.pretty', 'JST-S2B-PH-K-S_V.kicad_mod')
        M = parse(open(mp).read())
        j1_drill(M, 'library JST-S2B-PH-K-S_V')
        open(mp, 'w').write(dump(numify(M)) + '\n')

open(dst, 'w').write(dump(numify(B)) + '\n')
open(dst + '.log', 'w').write('\n'.join(LOG) + '\n')
print('\n'.join(LOG))
