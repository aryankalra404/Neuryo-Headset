"""Rev B schematic, 5th pass (review of 11 Nov 2026, review/REVB-REVIEW-11NOV.md).
usage: python3 edit_sch5.py in.kicad_sch out.kicad_sch STEPS   (1 = BOM part numbers, 2 = R37 100k -> 10k)
Neither step changes a connection: step 1 changes MPN/LCSC fields, step 2 a value."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sch import *

src, dst, STEPS = sys.argv[1], sys.argv[2], sys.argv[3]
s = parse(open(src).read())
log = []

# Each part page opened again on 11 Nov 2026 (JLCPCB part page: MPN, value, tolerance, rating, case; LCSC page: stock).
# Rows the review found in stock keep their MPN and get its LCSC number. Rows it found at zero stock, not listed or
# nearly out get the in-stock equivalent it names (same value, tolerance and case); the MPN field then names that part.
BOM5 = {
    # exact MPN, in stock
    'C1': ('KEMET C0603C474K4RACAUTO', 'C561783'),
    'C4 C5': ('Murata GCM21BR71C225KA64K', 'C1852484'),
    'C10 C35 C36 C38 C39 C40 C43 C44 C46': ('Yageo CC0603KRX7R7BB105', 'C106248'),
    'C34': ('Murata GRM31CR61A107MEA8L', 'C883598'),
    'D6': ('onsemi SD05T1G', 'C233423'),
    'R2': ('Yageo RT0603BRD07120KL', 'C705720'),
    'R3': ('Yageo RT0603BRD07105KL', 'C861072'),
    'R4': ('Yageo AT0603BRD07100KL', 'C855559'),
    # equivalents (reference MPN out of stock or not listed)
    'C15 C16 C17 C18 C19 C20 C21 C22 C23 C24 C25 C26 C27 C28 C29 C30 C31': ('Murata GRM1885C1H102FA01D', 'C913702'),
    'C32 C37 C41 C42 C45 C47': ('KEMET C0603C104J4RACTU', 'C22401913'),
    'R1': ('Yageo RT0603BRD07130KL', 'C861109'),
    'R9': ('UNI-ROYAL 0603WAF1004T5E', 'C22935'),
    'R10': ('Yageo RT0603BRD0751KL', 'C861458'),
    'R11 R12 R13 R14 R15 R16 R17 R18 R19 R20 R21 R22 R23 R24 R25 R26 R27': ('Yageo RT0603BRD072K2L', 'C861295'),
    'C2 C3 C49': ('Samsung CL21B475KOFNNNE', 'C107365'),
    'C9 C33': ('Samsung CL21A106KAYNNNE', 'C15850'),
    'C14': ('Murata GRM1885C1H152JA01D', 'C162204'),
}
# what the reference used, for the BOM note (scripts/jlcbom.py reads the field "Reference MPN")
WAS = {
    'C15': 'Yageo C0603C102F5GACTU', 'C32': 'Yageo C0603X104J4RACTU', 'R1': 'Vishay MCT06030D1303BP100',
    'R9': 'Vishay MCT06030C1004FPW00', 'R10': 'Vishay MCT06030D5102BP500', 'R11': 'Vishay MCT06030D2201BP500',
    'C2': 'Murata GCJ21BR71C475KA01K', 'C9': 'Murata GRJ21BR61E106KE01L', 'C14': 'Murata GRM1885C2A152JA01D',
}


def by_ref(r):
    return [y for y in kids(s, 'symbol') if ref_of(y) == r]


def field(y, name):
    v = [p[2] for p in kids(y, 'property') if p[1] == name]
    return v[0] if v else None


def set_field(y, name, value):
    for p in kids(y, 'property'):
        if p[1] == name:
            p[2] = value
            return
    a = kid(y, 'at')
    i = max(i for i, x in enumerate(y) if isinstance(x, list) and x[0] == 'property')
    y.insert(i + 1, ['property', name, value, ['at', a[1], a[2], '0'], ['hide', Sym('yes')],
                     ['effects', ['font', ['size', '1.27', '1.27']]]])


if '1' in STEPS:
    for refs, (mpn, lcsc) in BOM5.items():
        group = refs.split()
        was = None
        for r in group:
            if r in WAS:
                was = WAS[r]
        for r in group:
            ys = by_ref(r)
            assert ys, r
            for y in ys:
                old = field(y, 'MPN')
                if was:
                    set_field(y, 'Reference MPN', old)
                set_field(y, 'MPN', mpn)
                set_field(y, 'LCSC', lcsc)
        log.append('%-60s MPN %s, LCSC %s%s' % (refs[:60], mpn, lcsc, ('  (was %s)' % was) if was else ''))

if '2' in STEPS:
    for y in by_ref('R37'):
        old = field(y, 'Value')
        set_field(y, 'Value', '10k')
        set_field(y, 'MPN', 'UNI-ROYAL 0603WAF1002T5E')
        set_field(y, 'LCSC', 'C25804')
        for p in kids(y, 'property'):       # R37 carries the Description field twice (2nd pass); set both
            if p[1] == 'Description':
                p[2] = 'RES 10k 1% 0603'
        log.append('R37: value %s -> 10k, MPN UNI-ROYAL 0603WAF1002T5E, LCSC C25804' % old)

open(dst, 'w').write(dump(numify(s)) + '\n')
open(dst + '.log', 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
