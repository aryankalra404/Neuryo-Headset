#!/usr/bin/env python3
"""Write a JLCPCB-style BOM (with part numbers) from the rev B schematic.

kicad-cli's default BOM export (runner.sh) lists only value and footprint, so the
MPN and LCSC fields never reach the order. This reads the placed symbols of the
.kicad_sch directly (no KiCad needed) and groups identical parts.

    python3 scripts/jlcbom.py Neuryo_RevB.kicad_sch review/fab-draft-do-not-order/bom-jlc.csv

4th pass: parts JLCPCB does not assemble (the XIAO, J1, the headers, JP1, TP1) go to bom-hand.csv next to it.
"""
import csv
import re
import sys

NOTES = {
    'U6': 'Hand-solder (ASSEMBLY.md): castellations with an iron, then BAT+/BAT- through their plated holes from the back',
    'J1': 'Hand-solder; check the battery lead polarity against the "+" mark first (ASSEMBLY.md)',
    'J6': '1x4 header or leads soldered in', 'J7': '1x4 header or leads soldered in',
    'JP1': 'Hand-solder if wanted', 'TP1': 'Hand-solder if wanted',
}
for n in range(10, 20):
    NOTES[f'J{n}'] = 'For the v6 pod leave off and solder each lead into its two holes (pcb/README step 5)'
for r in ('R28', 'R29', 'R30', 'R31', 'R32', 'R33', 'R34', 'R35'):
    NOTES[r] = 'JLCPCB Basic equivalent (10k 1% 0603 thick film) of the reference Yageo AC0603FR-7W10KL'
# 4th pass: not assembled by JLCPCB (hand-soldered or left off); listed in bom-hand.csv instead of bom-jlc.csv
NOT_ASSEMBLED = {'U6', 'J1', 'J6', 'J7', 'JP1', 'TP1'} | {f'J{n}' for n in range(10, 20)}


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
    hand = [r for r in rows if r[1].split(', ')[0] in NOT_ASSEMBLED]
    jlc = [r for r in rows if r not in hand]
    assert all(set(r[1].split(', ')) <= NOT_ASSEMBLED for r in hand) and not any(set(r[1].split(', ')) & NOT_ASSEMBLED for r in jlc)
    hand_out = out.replace('bom-jlc', 'bom-hand') if 'bom-jlc' in out else out + '.hand.csv'
    for path, rr in ((out, jlc), (hand_out, hand)):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Comment', 'Designator', 'Footprint', 'Quantity', 'MPN', 'LCSC Part #', 'Note'])
            w.writerows(rr)
        print(f'{sum(r[3] for r in rr)} parts in {len(rr)} lines -> {path}')
    for r in jlc:
        if not r[4] or not r[5]:
            print('  JLCPCB line without', 'MPN' if not r[4] else 'LCSC', ':', r[1], r[0])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
