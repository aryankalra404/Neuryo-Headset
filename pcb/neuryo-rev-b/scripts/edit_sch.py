"""Rev B schematic edits on the imported Low-Cost-EEG schematic.
usage: python3 edit_sch.py in.kicad_sch out.kicad_sch STEP   (STEP = 1..N applies changes cumulatively up to N)"""
import sys, copy, math
sys.path.insert(0, '/home/claude/kw')
from sch import *

src, dst, STEP = sys.argv[1], sys.argv[2], int(sys.argv[3])
s = parse(open(src).read())
LIB = parse(open('/home/claude/kw/revb/Neuryo_RevB.kicad_sym').read())
PATH = '/872c0b8b-1d9e-4dd7-a98c-7e5a56213b3f'
log = []

R = lambda v: round(float(v), 3)


def syms():
    return kids(s, 'symbol')


def by_ref(r):
    return [y for y in syms() if ref_of(y) == r]


FREED = set()   # points where something was deleted; only stubs ending there are trimmed


def remove(item):
    if isinstance(item, list) and item and item[0] == 'symbol':
        for n, (x, y, nm) in pin_points(s, item).items():
            FREED.add((x, y))
    if isinstance(item, list) and item and item[0] == 'wire':
        for p in wpts(item):
            FREED.add(p)
    s.remove(item)


def is_pwr(y):
    return ref_of(y).startswith('#')


def pwr_name(y):
    return [p[2] for p in kids(y, 'property') if p[1] == 'Value'][0]


def wires():
    return kids(s, 'wire')


def wpts(w):
    return [(R(q[1]), R(q[2])) for q in kid(w, 'pts')[1:]]


def on_seg(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if (x, y) in (a, b):
        return False
    cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
    if abs(cross) > 1e-6:
        return False
    return min(x1, x2) - 1e-6 <= x <= max(x1, x2) + 1e-6 and min(y1, y2) - 1e-6 <= y <= max(y1, y2) + 1e-6


def find_wire(a, b):
    for w in wires():
        if set(wpts(w)) == {a, b}:
            return w
    raise KeyError((a, b))


def prune():
    """remove what the deletions left without a pin: wire groups with no symbol pin (and their labels / power symbols),
    then bare wire stubs whose free end carries nothing, junctions off wires, no-connects off pins"""
    pins = set()
    for y in syms():
        if not is_pwr(y):
            for n, (x, yy, nm) in pin_points(s, y).items():
                pins.add((x, yy))
    W = [(w, wpts(w)) for w in wires()]
    par = list(range(len(W)))
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    def touches(p, seg):
        return p in seg or on_seg(p, seg[0], seg[1])
    for i in range(len(W)):
        for j in range(i + 1, len(W)):
            a, b = W[i][1], W[j][1]
            if touches(a[0], b) or touches(a[1], b) or touches(b[0], a) or touches(b[1], a):
                par[f(i)] = f(j)
    alive = set()
    for i, (w, seg) in enumerate(W):
        if any(touches(p, seg) for p in pins if min(seg[0][0], seg[1][0]) - 1e-6 <= p[0] <= max(seg[0][0], seg[1][0]) + 1e-6
               and min(seg[0][1], seg[1][1]) - 1e-6 <= p[1] <= max(seg[0][1], seg[1][1]) + 1e-6):
            alive.add(f(i))
    for i, (w, seg) in enumerate(W):
        if f(i) not in alive:
            remove(w); log.append('prune wire %s-%s' % tuple(seg))
    # stubs: free end with nothing on the stub
    changed = True
    while changed:
        changed = False
        W = [(w, wpts(w)) for w in wires()]
        labpts = [(R(kid(l, 'at')[1]), R(kid(l, 'at')[2])) for l in kids(s, 'label')]
        pwrpts = [(R(kid(y, 'at')[1]), R(kid(y, 'at')[2])) for y in syms() if is_pwr(y)]
        for w, seg in W:
            others = [sg for ww, sg in W if ww is not w]
            carries = any(touches(p, seg) for p in labpts + pwrpts) or any(on_seg(p, seg[0], seg[1]) for p in pins)
            if carries:
                continue
            for e in seg:
                if e in FREED and e not in pins and not any(touches(e, sg) for sg in others):
                    remove(w); log.append('prune stub %s-%s' % tuple(seg)); changed = True; break
            if changed:
                break
    segs = [wpts(w) for w in wires()]
    on_any = lambda p: any(touches(p, sg) for sg in segs)
    for l in list(kids(s, 'label')):
        p = (R(kid(l, 'at')[1]), R(kid(l, 'at')[2]))
        if p not in pins and not on_any(p):
            remove(l); log.append('prune label %s at %s' % (l[1], p))
    for y in list(syms()):
        if is_pwr(y):
            p = (R(kid(y, 'at')[1]), R(kid(y, 'at')[2]))
            if p not in pins and not on_any(p):
                remove(y); log.append('prune power %s at %s' % (pwr_name(y), p))
    for j in list(kids(s, 'junction')):
        p = (R(kid(j, 'at')[1]), R(kid(j, 'at')[2]))
        pw = [(R(kid(y, 'at')[1]), R(kid(y, 'at')[2])) for y in syms() if is_pwr(y)]
        n = sum((1 if p in sg else 2) for sg in segs if touches(p, sg)) + (1 if p in pins else 0) + (1 if p in pw else 0)
        if n < 3:
            remove(j); log.append('prune junction %s' % (p,))
    for nc in list(kids(s, 'no_connect')):
        p = (R(kid(nc, 'at')[1]), R(kid(nc, 'at')[2]))
        if p not in pins and not on_any(p):
            remove(nc); log.append('prune no_connect %s' % (p,))


def label(name, p, ang=0):
    s.append(['label', name, ['at', str(p[0]), str(p[1]), str(ang)],
              ['effects', ['font', ['size', '1.27', '1.27']], ['justify', Sym('left'), Sym('bottom')]], ['uuid', new_uuid()]])


def no_connect(p):
    s.append(['no_connect', ['at', str(p[0]), str(p[1])], ['uuid', new_uuid()]])


_pwr_tpl = {}
for y in syms():
    if is_pwr(y):
        _pwr_tpl.setdefault(pwr_name(y), copy.deepcopy(y))


def power(name, p, rot=0):
    y = copy.deepcopy(_pwr_tpl[name])
    a = kid(y, 'at'); dx, dy = float(p[0]) - float(a[1]), float(p[1]) - float(a[2])
    a[1], a[2] = str(p[0]), str(p[1])
    if len(a) > 3:
        a[3] = str(rot)
    for pr in kids(y, 'property'):
        pa = kid(pr, 'at'); pa[1] = '%.3f' % (float(pa[1]) + dx); pa[2] = '%.3f' % (float(pa[2]) + dy)
    kid(y, 'uuid')[1] = new_uuid()
    for pn in kids(y, 'pin'):
        kid(pn, 'uuid')[1] = new_uuid()
    s.insert(s.index(kid(s, 'sheet_instances')), y)
    return y


def set_prop(y, name, value, hide=True):
    for p in kids(y, 'property'):
        if p[1] == name:
            p[2] = value; return
    a = kid(y, 'at')
    e = ['property', name, value, ['at', a[1], a[2], '0']]
    if hide:
        e.append(['hide', Sym('yes')])
    e.append(['effects', ['font', ['size', '1.27', '1.27']]])
    i = max(i for i, x in enumerate(y) if isinstance(x, list) and x[0] == 'property')
    y.insert(i + 1, e)


def ensure_lib(lib_id, src_sym):
    ls = kid(s, 'lib_symbols')
    if any(x[1] == lib_id for x in kids(ls, 'symbol')):
        return
    c = copy.deepcopy(src_sym); c[1] = lib_id
    ls.append(c)


def lib_from(name):
    return [x for x in kids(LIB, 'symbol') if x[1] == name][0]


def place(lib_id, ref, value, footprint, at, rot, conns, props=None, dnp=False):
    """conns: {pin: ('L', name) | ('P', powername) | ('NC',)}"""
    if lib_id.startswith('Neuryo_RevB:'):
        ensure_lib(lib_id, lib_from(lib_id.split(':')[1]))
    ls = [x for x in kids(kid(s, 'lib_symbols'), 'symbol') if x[1] == lib_id][0]
    pins = []
    for sub in kids(ls, 'symbol'):
        for p in kids(sub, 'pin'):
            pins.append(str(val(p, 'number')))
    y = ['symbol', ['lib_id', lib_id], ['at', str(at[0]), str(at[1]), str(rot)], ['unit', '1'], ['body_style', '1'],
         ['exclude_from_sim', Sym('no')], ['in_bom', Sym('no' if dnp else 'yes')], ['on_board', Sym('yes')], ['in_pos_files', Sym('yes')],
         ['dnp', Sym('yes' if dnp else 'no')], ['uuid', new_uuid()]]
    def P(n, v, dx, dy, hide):
        e = ['property', n, v, ['at', '%.2f' % (at[0] + dx), '%.2f' % (at[1] + dy), '0']]
        if hide:
            e.append(['hide', Sym('yes')])
        e.append(['effects', ['font', ['size', '1.27', '1.27']], ['justify', Sym('left')]])
        return e
    y += [P('Reference', ref, 3, -2, False), P('Value', value, 3, 1, False), P('Footprint', footprint, 0, 0, True),
          P('Datasheet', '', 0, 0, True), P('Description', '', 0, 0, True)]
    for k, v in (props or {}).items():
        y.append(P(k, v, 0, 0, True))
    for n in pins:
        y.append(['pin', n, ['uuid', new_uuid()]])
    y.append(['instances', ['project', 'Low_Cost_EEG', ['path', PATH, ['reference', ref], ['unit', '1']]]])
    s.insert(s.index(kid(s, 'sheet_instances')), y)
    pp = pin_points(s, y)
    for n, c in conns.items():
        p = pp[n][:2]
        if c[0] == 'L':
            label(c[1], p)
        elif c[0] == 'P':
            power(c[1], p)
        else:
            no_connect(p)
    missing = set(pins) - set(conns)
    if missing:
        raise SystemExit('%s: pins without connection %s' % (ref, sorted(missing)))
    log.append('add %s %s %s' % (ref, value, lib_id))
    return y


# ---------------------------------------------------------------- step 1: remove the ESP32-S3 module side
if STEP >= 1:
    DEL = 'U5 C11 C12 C13 R7 R8 SW2 SW3 U2 C6 C7 J2 C48 D7 R5 R6 J5 TP5'.split()
    for r in DEL:
        for y in by_ref(r):
            remove(y); log.append('delete %s' % r)
    # SW1 throw 3 was VBUS (USB/battery selector); rev B: battery on/off, throw 3 open
    for y in syms():
        if is_pwr(y) and pwr_name(y) == 'VBUS':
            remove(y); log.append('delete VBUS power symbol')
    prune()
    no_connect((180.34, 353.06))   # SW1 pin 3
    # SW1: Altium 1101M2S3CQE2 (12.9 x 6.8 mm THT) -> C&K PCM12SMTR (SMD, 0.3 A @ 6 VDC, terminal 2 common), so the battery
    # entry fits at the right-hand end of the 77 mm board. Same pins: 1 VBAT, 2 VIN (common), 3 open.
    y = by_ref('SW1')[0]
    set_prop(y, 'Footprint', 'Neuryo_RevB:SW_SPDT_PCM12')
    for p in list(kids(y, 'property')):
        if p[1] not in ('Reference', 'Value', 'Footprint', 'Datasheet', 'Description'):
            y.remove(p)                      # the Altium part's parametric fields (6 A, THT, ...) no longer apply
    set_prop(y, 'Description', 'SWITCH SLIDE SPDT 0.3A 6VDC SMD')
    set_prop(y, 'Datasheet', 'https://www.ckswitches.com/media/1424/pcm.pdf')
    set_prop(y, 'MPN', 'C&K PCM12SMTR'); set_prop(y, 'LCSC', 'C221841')
    set_prop(y, 'Value', 'PCM12SMTR')
    log.append('SW1 -> C&K PCM12SMTR, footprint Neuryo_RevB:SW_SPDT_PCM12')

# ---------------------------------------------------------------- step 2: change 1, reference via SRB2 through R27/C31
if STEP >= 2:
    for l in kids(s, 'label'):
        a = (R(kid(l, 'at')[1]), R(kid(l, 'at')[2]))
        if l[1] == 'SRB1' and a == (203.2, 266.7):
            l[1] = 'SRB2'; log.append('R27/C31 node SRB1 -> SRB2')
        elif l[1] == 'SRB2' and a in ((76.2, 231.14), (43.18, 228.6)):
            l[1] = 'SRB2_HDR'; log.append('header SRB2 pin + D5 IO4 -> SRB2_HDR (not connected to the ADS1299)')
    for l in kids(s, 'label'):
        if l[1] == 'SRB1':
            p = (R(kid(l, 'at')[1]), R(kid(l, 'at')[2]))
            remove(l)
            for w in list(wires()):
                if (350.52, 190.5) in wpts(w):
                    remove(w); log.append('wire from U4 pin 17 removed %s' % (wpts(w),))
            no_connect((350.52, 190.5)); log.append('U4 pin 17 SRB1 -> no connect')

# ---------------------------------------------------------------- step 3: change 5, BIAS series resistor 51k
if STEP >= 3:
    y = by_ref('R10')[0]
    set_prop(y, 'Value', '51k', hide=True)
    set_prop(y, 'RESISTANCE', '51kR')
    set_prop(y, 'Description', 'RES SMD 51K OHM 0.1% 1/10W 0603 thin film')
    set_prop(y, 'MPN', 'Vishay MCT06030D5102BP500')
    log.append('R10 2.2k -> 51k')

# ---------------------------------------------------------------- step 4: change 4, START tied low via 10k
RES = 'Altium Content Vault:1029c3af85768c4190bb7ad29bc67b5'
CAP = 'Altium Content Vault:b4654b650e69147ec39a6b967a45e02'
FP_R = 'Low_Cost_EEG-import-fps:FP-AC0603-MFG'
FP_C = 'Low_Cost_EEG-import-fps:FP-CGA3E-0_3-0_1-MFG'
if STEP >= 4:
    place(RES, 'R36', '10k', FP_R, (447.04, 134.62), 0, {'1': ('L', 'ADS_START'), '2': ('P', 'GND')},
          {'MPN': 'Yageo AC0603FR-7W10KL (same as R28-R35)', 'Description': 'RES 10k 1% 0603'})

# ---------------------------------------------------------------- step 5: change 2, analog enables on AEN + USB interlock
if STEP >= 5:
    remove(find_wire((266.7, 60.96), (266.7, 66.04)))     # U1 EN+/EN- off VIN
    label('AEN', (266.7, 66.04))
    remove(find_wire((416.56, 66.04), (416.56, 60.96)))   # U3 EN off IN
    label('AEN', (416.56, 66.04))
    prune()
    place('Neuryo_RevB:2N7002', 'Q1', '2N7002', 'Neuryo_RevB:SOT-23', (510.54, 134.62), 0,
          {'1': ('L', 'VUSB'), '2': ('P', 'GND'), '3': ('L', 'AEN')}, {'MPN': 'Nexperia 2N7002,215'})
    place(RES, 'R37', '100k', FP_R, (447.04, 144.78), 0, {'1': ('L', 'VUSB'), '2': ('P', 'GND')},
          {'Description': 'RES 100k 1% 0603', 'MPN': 'Yageo AC0603FR-07100KL'})
    place(RES, 'R38', '100k', FP_R, (447.04, 154.94), 0, {'1': ('P', 'VIN'), '2': ('L', 'AEN')},
          {'Description': 'RES 100k 1% 0603', 'MPN': 'Yageo AC0603FR-07100KL'})
    place(RES, 'R39', '100k', FP_R, (447.04, 165.1), 0, {'1': ('L', 'VUSB'), '2': ('L', 'USB_SENSE')},
          {'Description': 'RES 100k 1% 0603', 'MPN': 'Yageo AC0603FR-07100KL'})
    place(RES, 'R40', '150k', FP_R, (447.04, 175.26), 0, {'1': ('L', 'USB_SENSE'), '2': ('P', 'GND')},
          {'Description': 'RES 150k 1% 0603', 'MPN': 'Yageo AC0603FR-07150KL'})

# ---------------------------------------------------------------- step 6: XIAO ESP32-S3, battery divider, I2C headers
if STEP >= 6:
    place(RES, 'R41', '220k', FP_R, (447.04, 190.5), 0, {'1': ('P', 'VIN'), '2': ('L', 'VBAT_SENSE')},
          {'Description': 'RES 220k 1% 0603', 'MPN': 'Yageo AC0603FR-07220KL'})
    place(RES, 'R42', '220k', FP_R, (447.04, 200.66), 0, {'1': ('L', 'VBAT_SENSE'), '2': ('P', 'GND')},
          {'Description': 'RES 220k 1% 0603', 'MPN': 'Yageo AC0603FR-07220KL'})
    place(CAP, 'C50', '0.1uF', 'Low_Cost_EEG-import-fps:FP-C0603C-CF-MFG', (447.04, 210.82), 0, {'1': ('L', 'VBAT_SENSE'), '2': ('P', 'GND')},
          {'Description': 'Cap Ceramic 100nF 50V X7R 0603', 'MPN': 'TDK CGA3E2X7R1H104K080AD (as reference C13)'})
    X = {'1': ('L', 'VBAT_SENSE'), '2': ('L', 'DRDY'), '3': ('L', 'CS'), '4': ('L', 'MOSI'), '5': ('L', 'SCLK'),
         '6': ('L', 'MISO'), '7': ('NC',), '8': ('L', 'I2C_SCL'), '9': ('L', 'I2C_SDA'), '10': ('L', 'USB_SENSE'),
         '11': ('NC',), '12': ('L', 'XIAO_3V3'), '13': ('P', 'GND'), '14': ('L', 'VUSB'),
         '15': ('NC',), '16': ('NC',), '17': ('NC',), '18': ('NC',), '19': ('NC',), '20': ('NC',), '21': ('NC',), '22': ('NC',),
         '23': ('P', 'VIN'), '24': ('P', 'GND'), '25': ('P', 'GND')}   # 25: module's exposed GND copper (Seeed module PCB)
    place('Neuryo_RevB:XIAO-ESP32-S3-SMD', 'U6', 'XIAO ESP32-S3', 'Neuryo_RevB:XIAO-ESP32-S3-SMD', (502.92, 228.6), 0, X,
          {'MPN': 'Seeed Studio XIAO ESP32-S3 (113991114)'})
    place('Neuryo_RevB:Conn_1x04', 'J6', 'MAX30102 earlobe', 'Neuryo_RevB:PinHeader_1x04_P2.54_TSW', (464.82, 297.18), 0,
          {'1': ('P', 'GND'), '2': ('L', 'XIAO_3V3'), '3': ('L', 'I2C_SDA'), '4': ('L', 'I2C_SCL')}, {'MPN': 'Samtec TSW-104-07-T-S or leads soldered in'})
    place('Neuryo_RevB:Conn_1x04', 'J7', 'BMI270', 'Neuryo_RevB:PinHeader_1x04_P2.54_TSW', (464.82, 320.04), 0,
          {'1': ('P', 'GND'), '2': ('L', 'XIAO_3V3'), '3': ('L', 'I2C_SDA'), '4': ('L', 'I2C_SCL')}, {'MPN': 'Samtec TSW-104-07-T-S or leads soldered in'})
    for t in kids(s, 'text'):
        if t[1] == 'ESP32':
            t[1] = 'XIAO ESP32-S3 (rev B)'

# ---------------------------------------------------------------- step 7: PWR_FLAGs (ERC only; the import has no power-output pins on these nets)
if STEP >= 7:
    ensure_lib('Neuryo_RevB:PWR_FLAG', lib_from('PWR_FLAG'))
    for k, net in enumerate(['VIN', 'VBAT', 'GND', 'AVDD', 'AVSS', 'DVDD']):
        p = (452.12 + 10.16 * k, 355.6)
        power(net, p)
        fl = ['symbol', ['lib_id', 'Neuryo_RevB:PWR_FLAG'], ['at', str(p[0]), str(p[1]), '0'], ['unit', '1'], ['body_style', '1'],
              ['exclude_from_sim', Sym('no')], ['in_bom', Sym('no')], ['on_board', Sym('no')], ['in_pos_files', Sym('no')], ['dnp', Sym('no')], ['uuid', new_uuid()],
              ['property', 'Reference', '#FLG%02d' % (k + 1), ['at', str(p[0]), str(p[1] - 1.9), '0'], ['hide', Sym('yes')], ['effects', ['font', ['size', '1.27', '1.27']]]],
              ['property', 'Value', 'PWR_FLAG', ['at', str(p[0]), str(p[1] - 3.8), '0'], ['effects', ['font', ['size', '1.27', '1.27']]]],
              ['property', 'Footprint', '', ['at', str(p[0]), str(p[1]), '0'], ['hide', Sym('yes')], ['effects', ['font', ['size', '1.27', '1.27']]]],
              ['property', 'Datasheet', '', ['at', str(p[0]), str(p[1]), '0'], ['hide', Sym('yes')], ['effects', ['font', ['size', '1.27', '1.27']]]],
              ['property', 'Description', '', ['at', str(p[0]), str(p[1]), '0'], ['hide', Sym('yes')], ['effects', ['font', ['size', '1.27', '1.27']]]],
              ['pin', '1', ['uuid', new_uuid()]],
              ['instances', ['project', 'Low_Cost_EEG', ['path', PATH, ['reference', '#FLG%02d' % (k + 1)], ['unit', '1']]]]]
        s.insert(s.index(kid(s, 'sheet_instances')), fl)
        log.append('PWR_FLAG on %s' % net)

# ---------------------------------------------------------------- final: number the power symbols (#PWR? from the import)
n = 0
for y in syms():
    if ref_of(y) == '#PWR?' or (ref_of(y).startswith('#PWR') and STEP >= 1):
        n += 1
        r = '#PWR%03d' % n
        for p in kids(y, 'property'):
            if p[1] == 'Reference':
                p[2] = r
        for pth in kids(kid(kid(y, 'instances'), 'project'), 'path'):
            kid(pth, 'reference')[1] = r

if STEP >= 8:   # housekeeping: the importer wrote instance paths that don't match the root sheet uuid ("annotation errors")
    root = '/' + kid(s, 'uuid')[1]
    for y in syms():
        for pth in kids(kid(kid(y, 'instances'), 'project'), 'path'):
            pth[1] = root
    log.append('instance paths -> %s' % root)
    # the import named the ten electrode headers J3A-J3J; KiCad treats a reference without a trailing number as
    # unannotated ("J3A?" in the BOM, annotation-error warning). Renamed J10-J19 in the same order; no connection change.
    for i, c in enumerate('ABCDEFGHIJ'):
        for y in by_ref('J3' + c):
            for p in kids(y, 'property'):
                if p[1] == 'Reference':
                    p[2] = 'J%d' % (10 + i)
            for pth in kids(kid(kid(y, 'instances'), 'project'), 'path'):
                kid(pth, 'reference')[1] = 'J%d' % (10 + i)
            log.append('rename J3%s -> J%d' % (c, 10 + i))
open(dst, 'w').write(dump(numify(s)) + '\n')
open(dst + '.log', 'w').write('\n'.join(log) + '\n')
print('\n'.join(l for l in log if not l.startswith('prune')))
print('pruned items:', sum(1 for l in log if l.startswith('prune')))
