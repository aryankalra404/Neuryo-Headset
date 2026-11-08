#!/usr/bin/env python3
"""Write a JLCPCB-style BOM (with part numbers) from the rev B schematic.

kicad-cli's default BOM export (runner.sh) lists only value and footprint, so the
MPN and LCSC fields never reach the order. This reads the placed symbols of the
.kicad_sch directly (no KiCad needed) and groups identical parts.

    python3 scripts/jlcbom.py Neuryo_RevB.kicad_sch review/fab-draft-do-not-order/bom-jlc.csv
"""
import csv
import re
import sys

NOTES = {
    'U6': 'Hand-solder: underside BAT/GND pads need hot air or a hot plate (CHANGES change 7)',
    'J6': '1x4 header or leads soldered in', 'J7': '1x4 header or leads soldered in',
}
for n in range(10, 20):
    NOTES[f'J{n}'] = 'For the v6 pod leave off and solder each lead into its two holes (pcb/README step 5)'


def symbols(text):
    starts = [m.start() for m in re.finditer(r'\n\t\(symbol\n', text)] + [len(text)]
    for k in range(len(starts) - 1):
        blk = text[starts[k]:starts[k + 1]]
        props = dict(re.findall(r'\(property "([^"]+)" "((?:[^"\\]|\\.)*)"', blk))
        flag = lambda name: (re.search(r'^\t\t\(%s (yes|no)\)' % name, blk, re.M) or [None, 'yes'])[1]
        yield props, flag('in_bom'), flag('dnp')


def main(sch, out):
    text = open(sch, encoding='utf-8').read()
    parts = {}
    for p, in_bom, dnp in symbols(text):
        ref = p.get('Reference', '')
        if ref.startswith('#') or in_bom != 'yes' or dnp == 'yes':
            continue
        parts[ref] = p  # multi-unit symbols (U4) appear once per unit; same fields
    groups = {}
    for ref, p in parts.items():
        fp = p.get('Footprint', '').split(':')[-1]
        if fp.startswith('TP_SMD'):
            continue  # copper test pad, nothing to place
        key = (p.get('Value', ''), fp, p.get('MPN', ''), p.get('LCSC', ''), NOTES.get(ref, ''))
        groups.setdefault(key, []).append(ref)
    natural = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
    rows = []
    for (val, fp, mpn, lcsc, note), refs in groups.items():
        refs.sort(key=natural)
        rows.append([val, ', '.join(refs), fp, len(refs), mpn, lcsc, note])
    rows.sort(key=lambda r: natural(r[1].split(',')[0]))
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'Quantity', 'MPN', 'LCSC Part #', 'Note'])
        w.writerows(rows)
    missing = [r for r in rows if not r[4]]
    print(f'{sum(r[3] for r in rows)} parts in {len(rows)} lines -> {out}')
    for r in missing:
        print('  no MPN:', r[1], r[0])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
