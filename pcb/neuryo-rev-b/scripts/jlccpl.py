"""KiCad position file -> JLCPCB placement (CPL) file.

    python3 scripts/jlccpl.py positions-kicad.csv cpl-jlc.csv bom-jlc.csv

Columns become JLCPCB's: Designator, Mid X, Mid Y, Rotation, Layer (Top/Bottom); values in mm, as plain numbers.
Rotation is KiCad's angle as exported, normalised to 0-360. No part is pre-rotated: which parts JLCPCB shows
turned is checked in its placement preview (ASSEMBLY.md lists the ones the 11 Nov review expects).
Only the designators in bom-jlc.csv are kept: the hand-soldered parts (jlcbom.NOT_ASSEMBLED) and the copper test pads
(nothing to place) are left out, so the CPL and the BOM list the same parts."""
import csv, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jlcbom import NOT_ASSEMBLED

src, dst, bom = sys.argv[1], sys.argv[2], sys.argv[3]
keep = set()
for b in csv.DictReader(open(bom, encoding='utf-8')):
    keep.update(b['Designator'].split(', '))
rows, skipped = [], []
for r in csv.DictReader(open(src, encoding='utf-8')):
    if r['Ref'] in NOT_ASSEMBLED or r['Ref'] not in keep:
        skipped.append(r['Ref'])
        continue
    rot = float(r['Rot']) % 360
    rows.append([r['Ref'], '%.4f' % float(r['PosX']), '%.4f' % float(r['PosY']), '%g' % rot, r['Side'].capitalize()])
missing = keep - set(r[0] for r in rows)
assert not missing, 'in the BOM but not in the position file: %s' % sorted(missing)
with open(dst, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer'])
    w.writerows(rows)
print('%d placements -> %s; left out (hand-soldered or nothing to place): %s' % (len(rows), dst, ' '.join(skipped)))
