#!/usr/bin/env python3
"""Rev B, 3rd pass: restore the reference board's part numbers in the schematic.

The Altium import kept the reference's part numbers on only some symbols, under
several field names (PARTNUMBER, MANUFACTURER PART NUMBER, PART NUMBER), and many
had none. This adds one hidden "MPN" field ("Manufacturer PartNumber") to every
symbol that lacks it, taken from the reference's production BOM
(low-cost-eeg/Production_Files/PCB Bill of Materials.xlsx, the parts it was built
with), plus the LCSC numbers already recorded in CHANGES.md. It also replaces the
reference's wrong "RES SMD 100 OHM 1% 1/8W 0603" descriptions (the part numbers
were right, the description text was copied from another part).

No connection, value or footprint changes. Run from the rev B folder:
    python3 scripts/edit_sch_mpn.py Neuryo_RevB.kicad_sch
"""
import re
import sys

# Reference production BOM: designator -> "Manufacturer PartNumber".
# Rev B renamed J3A..J3J to J10..J19 (same order); those already carry their part number.
MPN = {
    'C2': 'Murata GCJ21BR71C475KA01K', 'C3': 'Murata GCJ21BR71C475KA01K',
    'C49': 'Murata GCJ21BR71C475KA01K',
    'C4': 'Murata GCM21BR71C225KA64K', 'C5': 'Murata GCM21BR71C225KA64K',
    'C9': 'Murata GRJ21BR61E106KE01L', 'C33': 'Murata GRJ21BR61E106KE01L',
    'C34': 'Murata GRM31CR61A107MEA8L',
    'C1': 'Yageo C0603C474K4RACAUTO',
    'C14': 'Murata GRM1885C2A152JA01D',
    'D6': 'onsemi SD05T1G',
    'J1': 'JST S2B-PH-K-S(LF)(SN)',
    'R1': 'Vishay MCT06030D1303BP100',
    'R2': 'Yageo RT0603BRD07120KL', 'R3': 'Yageo RT0603BRD07105KL',
    'R4': 'Yageo AT0603BRD07100KL',
    'R9': 'Vishay MCT06030C1004FPW00',
    'TP1': 'Keystone 5003',
    'U1': 'Texas Instruments LM27762DSSR',
    'U3': 'Texas Instruments TPS7A2033PDBVR',
    'U4': 'Texas Instruments ADS1299IPAGR',
}
for n in [10, 11, 35, 36, 38, 39, 40, 43, 44, 46]:
    MPN[f'C{n}'] = 'Yageo CC0603KRX7R7BB105'
for n in range(15, 32):
    MPN[f'C{n}'] = 'Yageo C0603C102F5GACTU'
for n in [32, 37, 41, 42, 45, 47]:
    MPN[f'C{n}'] = 'Yageo C0603X104J4RACTU'
for n in range(1, 6):
    MPN[f'D{n}'] = 'Texas Instruments TPD4E1B06DCKR'
for n in range(11, 28):
    MPN[f'R{n}'] = 'Vishay MCT06030D2201BP500'
for n in range(28, 36):
    MPN[f'R{n}'] = 'Yageo AC0603FR-7W10KL'
for n in range(10, 20):
    MPN[f'J{n}'] = 'Samtec TSW-102-26-F-S'
MPN['JP1'] = 'Samtec TSW-102-26-F-S'

# LCSC numbers already found and recorded in CHANGES.md ("Not changed", change 8). Live stock unverified.
LCSC = {'U4': 'C476817', 'U1': 'C473398', 'U3': 'C2862740'}
for n in range(1, 6):
    LCSC[f'D{n}'] = 'C840093'

# Wrong descriptions copied by the reference; tolerance from the Vishay code letter (B = 0.1 %, F = 1 %).
DESC = {'R1': 'RES SMD 130K OHM 0.1% 0603 thin film (Vishay MCT0603)',
        'R9': 'RES SMD 1M OHM 1% 0603 thin film (Vishay MCT0603)'}
for n in range(11, 28):
    DESC[f'R{n}'] = 'RES SMD 2.2K OHM 0.1% 0603 thin film (Vishay MCT0603)'


def hidden_prop(name, value, x, y):
    return (f'\t\t(property "{name}" "{value}"\n'
            f'\t\t\t(at {x} {y} 0)\n'
            f'\t\t\t(hide yes)\n'
            f'\t\t\t(show_name no)\n'
            f'\t\t\t(do_not_autoplace no)\n'
            f'\t\t\t(effects\n'
            f'\t\t\t\t(font\n'
            f'\t\t\t\t\t(size 1.27 1.27)\n'
            f'\t\t\t\t)\n'
            f'\t\t\t)\n'
            f'\t\t)\n')


def main(path):
    s = open(path, encoding='utf-8').read()
    starts = [m.start() + 1 for m in re.finditer(r'\n\t\(symbol\n', s)]
    starts.append(len(s))
    out, last = [], 0
    done = {'mpn': set(), 'lcsc': set(), 'desc': set()}
    for k in range(len(starts) - 1):
        st, en = starts[k], starts[k + 1]
        blk = s[st:en]
        m = re.search(r'\(property "Reference" "([^"]+)"', blk)
        if not m:
            continue
        ref = m.group(1)
        if ref.startswith('#'):
            continue
        at = re.search(r'^\t\t\(at ([-\d.]+) ([-\d.]+)', blk, re.M)
        x, y = at.group(1), at.group(2)
        new = blk
        if ref in DESC:
            new2 = re.sub(r'(\(property "Description" ")RES SMD 100 OHM 1% 1/8W 0603(")',
                          lambda mm: mm.group(1) + DESC[ref] + mm.group(2), new, count=1)
            if new2 != new:
                done['desc'].add(ref)
            new = new2
        # insert new fields right after the Description property block
        ins = ''
        if ref in MPN and '(property "MPN"' not in new:
            ins += hidden_prop('MPN', MPN[ref], x, y)
            done['mpn'].add(ref)
        if ref in LCSC and '(property "LCSC"' not in new:
            ins += hidden_prop('LCSC', LCSC[ref], x, y)
            done['lcsc'].add(ref)
        if ins:
            d = re.search(r'\t\t\(property "Description" "(?:[^"\\]|\\.)*"\n.*?\n\t\t\)\n', new, re.S)
            if not d:
                raise SystemExit(f'{ref}: no Description property to insert after')
            new = new[:d.end()] + ins + new[d.end():]
        out.append(s[last:st])
        out.append(new)
        last = en
    out.append(s[last:])
    res = ''.join(out)
    if res.count('(') - res.count(')') != s.count('(') - s.count(')'):
        raise SystemExit('unbalanced parentheses, not written')
    open(path, 'w', encoding='utf-8').write(res)
    missing = set(MPN) - done['mpn']
    print('MPN added:', len(done['mpn']), 'LCSC added:', len(done['lcsc']), 'descriptions fixed:', len(done['desc']))
    if missing:
        print('MPN not added (symbol missing or already had one):', sorted(missing))


if __name__ == '__main__':
    main(sys.argv[1])
