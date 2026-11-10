"""Rev B schematic, 4th pass (review of 10 Nov 2026, REVB-4TH-PASS-PLAN.md).
usage: python3 edit_sch4.py in.kicad_sch out.kicad_sch STEPS   (letters of the plan's steps, e.g. C, CD, CDE, CDEF)
Steps A and B change no connection; C-F are applied here. New parts go in a free column right of the XIAO."""
import sys, copy, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sch import *

src, dst, STEPS = sys.argv[1], sys.argv[2], sys.argv[3]
s = parse(open(src).read())
log = []
R = lambda v: round(float(v), 3)
ROOT = '/' + kid(s, 'uuid')[1]
PROJECT = kid(kid([y for y in kids(s, 'symbol') if ref_of(y) == 'R42'][0], 'instances'), 'project')[1]
RES = 'Altium Content Vault:1029c3af85768c4190bb7ad29bc67b5'
FP_R = 'Low_Cost_EEG-import-fps:FP-AC0603-MFG'


def syms():
    return kids(s, 'symbol')


def by_ref(r):
    return [y for y in syms() if ref_of(y) == r]


def label_at(name, p):
    for l in kids(s, 'label'):
        if l[1] == name and (R(kid(l, 'at')[1]), R(kid(l, 'at')[2])) == p:
            return l
    raise KeyError((name, p))


def label(name, p, ang=0):
    s.append(['label', name, ['at', str(p[0]), str(p[1]), str(ang)],
              ['effects', ['font', ['size', '1.27', '1.27']], ['justify', Sym('left'), Sym('bottom')]], ['uuid', new_uuid()]])


def place(lib_id, ref, value, footprint, at, conns, props, bom=True):
    ls = [x for x in kids(kid(s, 'lib_symbols'), 'symbol') if x[1] == lib_id][0]
    pins = sorted(set(str(val(p, 'number')) for sub in kids(ls, 'symbol') for p in kids(sub, 'pin')))
    yn = lambda b: Sym('yes' if b else 'no')
    y = ['symbol', ['lib_id', lib_id], ['at', str(at[0]), str(at[1]), '0'], ['unit', '1'], ['body_style', '1'],
         ['exclude_from_sim', Sym('no')], ['in_bom', yn(bom)], ['on_board', Sym('yes')], ['in_pos_files', yn(bom)],
         ['dnp', Sym('no')], ['uuid', new_uuid()]]

    def P(n, v, dx, dy, hide):
        e = ['property', n, v, ['at', '%.2f' % (at[0] + dx), '%.2f' % (at[1] + dy), '0']]
        if hide:
            e.append(['hide', Sym('yes')])
        e.append(['effects', ['font', ['size', '1.27', '1.27']], ['justify', Sym('left')]])
        return e
    y += [P('Reference', ref, 3, -2, False), P('Value', value, 3, 1, False), P('Footprint', footprint, 0, 0, True),
          P('Datasheet', '', 0, 0, True)]
    for k, v in props.items():
        y.append(P(k, v, 0, 0, True))
    for n in pins:
        y.append(['pin', n, ['uuid', new_uuid()]])
    y.append(['instances', ['project', PROJECT, ['path', ROOT, ['reference', ref], ['unit', '1']]]])
    s.insert(s.index(kid(s, 'sheet_instances')), y)
    pp = pin_points(s, y)
    if set(pins) != set(conns):
        raise SystemExit('%s: pins %s, connections %s' % (ref, pins, sorted(conns)))
    for n, net in conns.items():
        label(net, pp[n][:2])
    log.append('add %s %s %s pins %s' % (ref, value, footprint, ', '.join('%s=%s' % kv for kv in sorted(conns.items()))))
    return y


X = (553.72, 226.06)     # free column right of the XIAO symbol (its labels end near x 540)
if 'C' in STEPS:
    U6 = pin_points(s, by_ref('U6')[0])
    for pin, net in (('3', 'CS'), ('4', 'MOSI'), ('5', 'SCLK')):
        l = label_at(net, U6[pin][:2])
        l[1] = net + '_X'
        log.append('U6 pin %s (%s) label %s -> %s_X' % (pin, U6[pin][2], net, net))
    R330 = {'Description': 'RES 330R 1% 1/10W 0603', 'MPN': 'UNI-ROYAL 0603WAF3300T5E', 'LCSC': 'C23138'}
    for k, (r, net) in enumerate((('R43', 'SCLK'), ('R44', 'MOSI'), ('R45', 'CS'))):
        place(RES, r, '330', FP_R, (X[0], X[1] + 10.16 * k), {'1': net + '_X', '2': net}, R330)

if 'D' in STEPS:
    R4K7 = {'Description': 'RES 4.7k 1% 1/10W 0603', 'MPN': 'UNI-ROYAL 0603WAF4701T5E', 'LCSC': 'C23162'}
    place(RES, 'R46', '4.7k', FP_R, (X[0], X[1] + 40.64), {'1': 'I2C_SDA', '2': 'XIAO_3V3'}, R4K7)
    place(RES, 'R47', '4.7k', FP_R, (X[0], X[1] + 50.8), {'1': 'I2C_SCL', '2': 'XIAO_3V3'}, R4K7)

if 'E' in STEPS:
    p = pin_points(s, by_ref('U6')[0])['11'][:2]
    for nc in list(kids(s, 'no_connect')):
        if (R(kid(nc, 'at')[1]), R(kid(nc, 'at')[2])) == p:
            s.remove(nc)
    label('ADS_RESET', p)
    log.append('U6 pin 11 (D10): no-connect -> ADS_RESET (with U4 pin 36 and R30)')

if 'F' in STEPS:
    TPLIB = 'Test_Points:TestPoint_SMD'
    for k, (r, net) in enumerate((('TP7', 'MISO'), ('TP8', 'DRDY'), ('TP9', 'AEN'))):
        place(TPLIB, r, 'TP', 'Neuryo_RevB:TP_SMD_D1.0', (X[0] + 20.32, X[1] + 10.16 * k), {'1': net},
              {'Description': 'Test pad 1.0 mm, no paste', 'MPN': '(copper test pad, not assembled)'}, bom=False)

# ---------------------------------------------------------------- H: JLCPCB part numbers still missing (CHANGES "Change 8" / checklist 5)
# Each checked on its JLCPCB part page on 10 Nov 2026 (manufacturer, value, 1 %, 0603, Basic/Extended).
LCSC_H = {
    'R28 R29 R30 R31 R32 R33 R34 R35 R36': ('UNI-ROYAL 0603WAF1002T5E', 'C25804'),   # 10k 1% 0603, Basic
    'R37 R38 R39': ('UNI-ROYAL 0603WAF1003T5E', 'C25803'),                            # 100k 1% 0603, Basic
    'R40': ('UNI-ROYAL 0603WAF1503T5E', 'C22807'),                                    # 150k 1% 0603, Basic
    'R41 R42': ('UNI-ROYAL 0603WAF2203T5E', 'C22961'),                                # 220k 1% 0603, Basic
    'C50': ('YAGEO CC0603KRX7R9BB104', 'C14663'),                                     # 100nF 50V X7R 0603, Basic
    'Q1': ('Nexperia 2N7002,215', 'C65189'),                                          # same part as before, Extended
}


def set_field(y, name, value):
    for p in kids(y, 'property'):
        if p[1] == name:
            p[2] = value
            return
    a = kid(y, 'at')
    i = max(i for i, x in enumerate(y) if isinstance(x, list) and x[0] == 'property')
    y.insert(i + 1, ['property', name, value, ['at', a[1], a[2], '0'], ['hide', Sym('yes')], ['effects', ['font', ['size', '1.27', '1.27']]]])


if 'H' in STEPS:
    for refs, (mpn, lcsc) in LCSC_H.items():
        for r in refs.split():
            for y in by_ref(r):
                old = [p[2] for p in kids(y, 'property') if p[1] == 'MPN']
                set_field(y, 'MPN', mpn)
                set_field(y, 'LCSC', lcsc)
            log.append('%s: MPN %s -> %s, LCSC %s' % (r, old[0] if old else '-', mpn, lcsc))

open(dst, 'w').write(dump(numify(s)) + '\n')
open(dst + '.log', 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
