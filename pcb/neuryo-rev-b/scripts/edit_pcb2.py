"""Rev B board, part 2: outline, new parts, routing of the changed nets, stitching-via clean-up, silkscreen.
usage: python3 edit_pcb2.py p1.kicad_pcb p2.kicad_pcb"""
import sys, copy, math, uuid
sys.path.insert(0, '/home/claude/kw')
from sx import *

X0, Y0 = 98.5011, 80.0036
src, dst = sys.argv[1], sys.argv[2]
B = parse(open(src).read())
LOG = []
U = lambda: str(uuid.uuid4())
F = lambda v: '%.4f' % v
AX = lambda x: F(x + X0)
AY = lambda y: F(y + Y0)
MOD = '/home/claude/kw/revb/Neuryo_RevB.pretty/'
NEW = []   # new copper: ('seg', layer, a, b, w, net) / ('via', c, size, net) / ('pad', ...)


def log(*a):
    LOG.append(' '.join(str(x) for x in a))


def nn(e):
    n = kid(e, 'net')
    return (n[2] if len(n) > 2 else n[1]) if n else ''


def ref(fp):
    for p in kids(fp, 'property'):
        if p[1] == 'Reference':
            return p[2]


def fp(r):
    return [f for f in kids(B, 'footprint') if ref(f) == r][0]


def rot(x, y, deg):
    r = math.radians(deg)
    return x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r)


def fp_at(f):
    a = kid(f, 'at')
    return float(a[1]) - X0, float(a[2]) - Y0, (float(a[3]) if len(a) > 3 else 0.0)


def pads(f):
    fx, fy, fr = fp_at(f)
    out = {}
    for p in kids(f, 'pad'):
        a = kid(p, 'at')
        dx, dy = rot(float(a[1]), float(a[2]), fr)
        out.setdefault(str(p[1]), (fx + dx, fy + dy))
    return out


def P(r, n):
    return pads(fp(r))[str(n)]


def pt(e, k):
    a = kid(e, k)
    return float(a[1]) - X0, float(a[2]) - Y0


def near(p, q, tol=0.03):
    return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol


def seg(a, b, net, w=0.254, layer='F.Cu'):
    e = ['segment', ['start', Sym(AX(a[0])), Sym(AY(a[1]))], ['end', Sym(AX(b[0])), Sym(AY(b[1]))], ['width', Sym(F(w))],
         ['layer', layer], ['net', net], ['uuid', U()]]
    B.insert(B.index(kids(B, 'segment')[-1]) + 1, e)
    NEW.append(('seg', layer, a, b, w, net))
    return e


def path(pts, net, w=0.254, layer='F.Cu'):
    for a, b in zip(pts, pts[1:]):
        seg(a, b, net, w, layer)


def via(c, net, size=0.6, drill=0.3):
    e = ['via', ['at', Sym(AX(c[0])), Sym(AY(c[1]))], ['size', Sym(F(size))], ['drill', Sym(F(drill))], ['layers', 'F.Cu', 'B.Cu'],
         ['tenting', ['front', Sym('yes')], ['back', Sym('yes')]], ['net', net], ['uuid', U()]]
    B.insert(B.index(kids(B, 'via')[-1]) + 1, e)
    NEW.append(('via', c, size, net))
    return e


def del_seg(a, b, net=None):
    for s in kids(B, 'segment'):
        p, q = pt(s, 'start'), pt(s, 'end')
        if ((near(p, a) and near(q, b)) or (near(p, b) and near(q, a))) and (net is None or nn(s) == net):
            B.remove(s); log('delete segment', nn(s), a, b); return
    raise KeyError(('segment', a, b, net))


def del_via(c, net=None):
    for v in kids(B, 'via'):
        if near(pt(v, 'at'), c) and (net is None or nn(v) == net):
            B.remove(v); log('delete via', nn(v), c); return
    raise KeyError(('via', c))


def set_seg_net(a, b, net):
    for s in kids(B, 'segment'):
        p, q = pt(s, 'start'), pt(s, 'end')
        if (near(p, a) and near(q, b)) or (near(p, b) and near(q, a)):
            kid(s, 'net')[1:] = [net]; return
    raise KeyError(('segment', a, b))


def set_via_net(c, net):
    for v in kids(B, 'via'):
        if near(pt(v, 'at'), c):
            kid(v, 'net')[1:] = [net]; return
    raise KeyError(('via', c))


def newfp(lib_fp, refd, value, at, rot_, layer, nets, extra=None):
    """place a footprint: lib_fp = path of a .kicad_mod or an existing ref to clone"""
    if lib_fp.endswith('.kicad_mod'):
        m = parse(open(MOD + lib_fp).read())
        f = ['footprint', 'Neuryo_RevB:' + m[1]]
        for x in m[2:]:
            if isinstance(x, list) and x[0] in ('version', 'generator', 'generator_version'):
                continue
            f.append(x)
        f.insert(2, ['layer', 'F.Cu'])
        f[:] = [x for i, x in enumerate(f) if not (isinstance(x, list) and x and x[0] == 'layer' and i > 2)]
        f.insert(3, ['uuid', U()])
        f.insert(4, ['at', '0', '0', '0'])
        base_rot = 0.0
    else:
        f = copy.deepcopy(fp(lib_fp))
        base_rot = fp_at(f)[2]
        for k in ('path', 'sheetname', 'sheetfile'):
            for e in kids(f, k):
                f.remove(e)

    def renew(e):
        if isinstance(e, list):
            for x in e:
                if isinstance(x, list) and x and x[0] == 'uuid':
                    x[1] = U()
                renew(x)
    renew(f)
    a = kid(f, 'at')
    a[1:] = [Sym(AX(at[0])), Sym(AY(at[1])), Sym('%g' % rot_)]
    d = rot_ - base_rot
    for p in kids(f, 'pad') + kids(f, 'property') + kids(f, 'fp_text'):
        pa = kid(p, 'at')
        if pa is None:
            continue
        ang = float(pa[3]) if len(pa) > 3 else 0.0
        while len(pa) < 4:
            pa.append(Sym('0'))
        pa[3] = Sym('%g' % ((ang + d) % 360))
    for p in kids(f, 'property'):
        if p[1] == 'Reference':
            p[2] = refd
        if p[1] == 'Value':
            p[2] = value
    for k, v in (extra or {}).items():
        f.insert(f.index(kids(f, 'property')[-1]) + 1,
                 ['property', k, v, ['at', '0', '0', '0'], ['layer', 'F.Fab'], ['hide', Sym('yes')], ['uuid', U()], ['effects', ['font', ['size', '1', '1']]]])
    for p in kids(f, 'pad'):
        for e in kids(p, 'net'):
            p.remove(e)
        n = nets.get(str(p[1]))
        if n:
            p.insert(p.index(kid(p, 'layers')) + 1, ['net', n])
    if not lib_fp.endswith('.kicad_mod'):
        for p in kids(f, 'property'):
            if p[1] == 'Reference':
                pa = kid(p, 'at'); pa[1], pa[2] = Sym('0'), Sym('-1.3')
                fnt = kid(kid(p, 'effects'), 'font'); kid(fnt, 'size')[1:] = [Sym('0.8'), Sym('0.8')]
    B.insert(B.index(kids(B, 'footprint')[-1]) + 1, f)
    log('add footprint', refd, value, 'at %.2f,%.2f rot %g %s' % (at[0], at[1], rot_, layer))
    return f


# ================================================================== outline 77 x 50 mm
for g in list(B):
    if isinstance(g, list) and g and g[0] in ('gr_line', 'gr_arc', 'gr_rect', 'gr_poly') and val(g, 'layer') == 'Edge.Cuts':
        B.remove(g)
W, H = 77.0, 50.0


def eline(a, b):
    B.append(['gr_line', ['start', Sym(AX(a[0])), Sym(AY(a[1]))], ['end', Sym(AX(b[0])), Sym(AY(b[1]))],
              ['stroke', ['width', Sym('0.1')], ['type', Sym('default')]], ['layer', 'Edge.Cuts'], ['uuid', U()]])


def earc(a, m, b):
    B.append(['gr_arc', ['start', Sym(AX(a[0])), Sym(AY(a[1]))], ['mid', Sym(AX(m[0])), Sym(AY(m[1]))], ['end', Sym(AX(b[0])), Sym(AY(b[1]))],
              ['stroke', ['width', Sym('0.1')], ['type', Sym('default')]], ['layer', 'Edge.Cuts'], ['uuid', U()]])


r5, r1 = 5.0, 1.0
c = 1 - 1 / math.sqrt(2)
eline((r5, 0), (W - r1, 0)); earc((W - r1, 0), (W - r1 * c, r1 * c), (W, r1))
eline((W, r1), (W, H - r1)); earc((W, H - r1), (W - r1 * c, H - r1 * c), (W - r1, H))
eline((W - r1, H), (r5, H)); earc((r5, H), (r5 * c, H - r5 * c), (0, H - r5))
eline((0, H - r5), (0, r5)); earc((0, r5), (r5 * c, r5 * c), (r5, 0))
log('outline 77 x 50 mm: left corners R5 as the reference, right corners R1 (the XIAO pads reach the bottom right)')

# ================================================================== change 1: R27/C31 to SRB2 (pin 18), pin 17 open
# R27/C31 node (old SRB1 copper up to via 25.5,44.5) becomes SRB2; header SRB2 run from D5 IO4 onwards is removed;
# the old SRB2 run from via (26.25,42.5) to pin 18 is kept and joined to via (25.5,44.5) on B.Cu.
for s in kids(B, 'segment'):
    if nn(s) == 'SRB1':
        kid(s, 'net')[1:] = ['SRB2']
for v in kids(B, 'via'):
    if nn(v) == 'SRB1':
        kid(v, 'net')[1:] = ['SRB2']
for a, b in (((25.50, 44.50), (31.50, 38.50)), ((31.50, 38.50), (31.50, 31.75)), ((31.50, 31.75), (32.42, 30.82)), ((32.42, 30.82), (35.75, 30.82))):
    del_seg(a, b, 'SRB2')
del_seg((19.35, 43.75), (20.25, 43.75), 'SRB2'); del_via((20.25, 43.75), 'SRB2')
del_seg((20.25, 43.75), (25.00, 43.75), 'SRB2'); del_seg((25.00, 43.75), (26.25, 42.50), 'SRB2')
for a, b in (((13.54, 43.00), (15.79, 45.25)), ((15.79, 45.25), (17.27, 45.25)), ((17.27, 45.25), (18.70, 43.82)),
             ((18.70, 43.82), (19.28, 43.82)), ((19.28, 43.82), (19.35, 43.75))):
    set_seg_net(a, b, 'SRB2_HDR')
path([(25.50, 44.50), (26.25, 43.75), (26.25, 42.50)], 'SRB2', 0.254, 'B.Cu')
log('change 1: REF -> R27 -> via 25.5,44.5 -> B.Cu -> via 26.25,42.5 -> old SRB2 run -> U4 pin 18; pin 17 has no copper')

# ================================================================== change 4: START low through R36 (10k) near the ADS1299
for a, b in (((54.85, 31.60), (56.00, 32.75)), ((76.72, 36.50), (76.75, 36.47)), ((75.25, 36.50), (76.72, 36.50))):
    del_seg(a, b, 'ADS_START')
for a, b in (((58.00, 32.75), (59.88, 34.62)), ((56.00, 32.75), (58.00, 32.75)), ((59.88, 34.62), (73.38, 34.62)), ((73.38, 34.62), (75.25, 36.50))):
    del_seg(a, b, 'ADS_START')
del_via((56.00, 32.75), 'ADS_START'); del_via((75.25, 36.50), 'ADS_START')
del_seg((44.96, 31.60), (54.85, 31.60), 'ADS_START')
r36 = newfp('R30', 'R36', '10k', (52.5, 31.6), 0, 'F.Cu', {'1': 'ADS_START', '2': 'GND'}, {'MPN': 'Yageo AC0603FR-7W10KL'})
seg((44.96, 31.60), P('R36', 1), 'ADS_START')

# ================================================================== XIAO ESP32-S3 (U6)
# old copper under the module footprint (ESP32 thermal-pad fan-out, its GND vias, stubs) goes first
for e in list(kids(B, 'segment')) + list(kids(B, 'via')):
    pts_ = [pt(e, 'start'), pt(e, 'end')] if e[0] == 'segment' else [pt(e, 'at')]
    if any(55.6 <= x <= 77.5 and 30.6 <= y <= 50.5 for x, y in pts_) and nn(e) not in ('DRDY', 'CS', 'MOSI', 'SCLK', 'MISO', 'ADS_START'):
        B.remove(e); log('delete old copper under the XIAO', e[0], nn(e), pts_)
XN = {'1': 'VBAT_SENSE', '2': 'DRDY', '3': 'CS', '4': 'MOSI', '5': 'SCLK', '6': 'MISO', '8': 'I2C_SCL', '9': 'I2C_SDA',
      '10': 'USB_SENSE', '12': 'XIAO_3V3', '13': 'GND', '14': 'VUSB', '23': 'VIN', '24': 'GND', '25': 'GND'}
u6 = newfp('XIAO-ESP32-S3-SMD.kicad_mod', 'U6', 'XIAO ESP32-S3', (56.0, 31.0), 270, 'F.Cu', XN, {'MPN': 'Seeed Studio 113991114'})
for p_ in kids(u6, 'property'):
    if p_[1] == 'Reference':
        kid(p_, 'at')[1:3] = [Sym('9'), Sym('-10.5')]
        fnt = kid(kid(p_, 'effects'), 'font'); kid(fnt, 'size')[1:] = [Sym('1'), Sym('1')]
# pads 15-22 face the module's JTAG/EN/USB test pads, which rev B does not use: copper only (no mask opening, no paste),
# so nothing is soldered to them and they can't bridge. Pad 25 faces the module's exposed GND copper: GND, with a via.
for p_ in kids(u6, 'pad'):
    if str(p_[1]) in [str(k) for k in range(15, 23)]:
        kid(p_, 'layers')[1:] = ['F.Cu']
log('U6 pads 15-22: F.Cu only (no F.Mask, no F.Paste); pad 25 -> GND')
XP = pads(fp('U6'))
TOP = lambda n: (XP[n][0], 30.9)      # inside the top-row pad (pad spans y 30.46-33.21)
BOT = lambda n: (XP[n][0], 47.1)      # inside the bottom-row pad (46.62-49.38)

# ---- SPI: same traces from the ADS1299, last bends re-aimed at the XIAO pads
del_seg((63.08, 21.75), (72.45, 31.11), 'DRDY'); del_seg((72.45, 31.41), (72.45, 31.11), 'DRDY')
path([(63.08, 21.75), (71.58, 30.25), TOP('2')], 'DRDY')
del_seg((62.67, 22.60), (71.17, 31.11), 'CS'); del_seg((71.17, 31.41), (71.17, 31.11), 'CS')
path([(62.67, 22.60), (69.04, 28.97), TOP('3')], 'CS')
del_seg((62.78, 25.25), (68.64, 31.11), 'SCLK'); del_seg((68.64, 31.41), (68.64, 31.11), 'SCLK')
path([(62.78, 25.25), (63.96, 26.43), TOP('5')], 'SCLK')
for a, b in (((67.32, 28.52), (69.91, 31.11)), ((69.91, 31.41), (69.91, 31.11)), ((67.25, 28.25), (67.32, 28.32)), ((67.32, 28.52), (67.32, 28.32))):
    del_seg(a, b, 'MOSI')
path([(67.25, 28.25), (66.50, 29.00), TOP('4')], 'MOSI')
for a, b in (((62.51, 26.25), (67.36, 31.11)), ((67.36, 31.41), (67.36, 31.11)), ((62.50, 26.25), (62.51, 26.25))):
    del_seg(a, b, 'MISO')
path([(62.50, 26.25), (61.42, 27.33), TOP('6')], 'MISO')

# ---- I2C headers J6 (earlobe MAX30102) and J7 (BMI270): 1 GND, 2 3V3, 3 SDA, 4 SCL (pin 1 at the top); left of the
#      LM27762 block, joined pin to pin on F.Cu. Three B.Cu traces run down over the In2 VIN plane (x 62.6-63.5), step
#      left at y 20.6-21.6 and run down x 55.75-56.65 (over DVDD, then VIN) to vias beside the XIAO pads.
newfp('PinHeader_1x04_P2.54_TSW.kicad_mod', 'J6', 'MAX30102 earlobe', (58.3, 4.6), 270, 'F.Cu', {'1': 'GND', '2': 'XIAO_3V3', '3': 'I2C_SDA', '4': 'I2C_SCL'})
newfp('PinHeader_1x04_P2.54_TSW.kicad_mod', 'J7', 'BMI270', (61.3, 4.6), 270, 'F.Cu', {'1': 'GND', '2': 'XIAO_3V3', '3': 'I2C_SDA', '4': 'I2C_SCL'})
for k, n in ((2, 'XIAO_3V3'), (3, 'I2C_SDA'), (4, 'I2C_SCL')):
    seg(P('J6', k), P('J7', k), n, 0.4 if k == 2 else 0.254)
path([P('J7', 2), (63.5, P('J7', 2)[1]), (63.5, 21.6), (56.65, 21.6), (56.65, 41.5), (XP['12'][0], 41.5), (XP['12'][0], 43.0)], 'XIAO_3V3', 0.3, 'B.Cu')
via((XP['12'][0], 43.0), 'XIAO_3V3'); seg((XP['12'][0], 43.0), BOT('12'), 'XIAO_3V3', 0.4)
path([P('J7', 3), (63.05, P('J7', 3)[1]), (63.05, 21.1), (56.2, 21.1), (56.2, 44.4), (XP['9'][0], 44.4), (XP['9'][0], 45.6)], 'I2C_SDA', 0.254, 'B.Cu')
via((XP['9'][0], 45.6), 'I2C_SDA'); seg((XP['9'][0], 45.6), BOT('9'), 'I2C_SDA')
path([P('J7', 4), (62.6, P('J7', 4)[1]), (62.6, 20.6), (55.75, 20.6), (55.75, 45.0), (XP['8'][0] - 0.6, 45.0), (XP['8'][0], 45.6)], 'I2C_SCL', 0.254, 'B.Cu')
via((XP['8'][0], 45.6), 'I2C_SCL'); seg((XP['8'][0], 45.6), BOT('8'), 'I2C_SCL')
# ---- XIAO power / sense pads to vias
via((XP['13'][0], 45.5), 'GND'); seg((XP['13'][0], 45.5), BOT('13'), 'GND', 0.5)
via((XP['14'][0], 45.5), 'VUSB'); seg((XP['14'][0], 45.5), BOT('14'), 'VUSB', 0.4)
via((XP['10'][0], 45.6), 'USB_SENSE'); seg((XP['10'][0], 45.6), BOT('10'), 'USB_SENSE')
via((65.55, 35.45), 'VIN'); seg((65.55, 35.45), XP['23'], 'VIN', 0.5)
via((70.0, 35.45), 'GND'); seg((70.0, 35.45), XP['24'], 'GND', 0.5)
via((XP['25'][0], XP['25'][1] - 0.6), 'GND')     # in pad 25, clear of the B.Cu XIAO_3V3 run at y 41.5
via((XP['1'][0], 34.4), 'VBAT_SENSE'); seg((XP['1'][0], 34.4), (XP['1'][0], 32.8), 'VBAT_SENSE')

# ---- USB-present divider (bottom, under the XIAO): R39 VUSB->USB_SENSE, R40 USB_SENSE->GND
newfp('R32', 'R40', '150k', (63.96, 43.6), 90, 'B.Cu', {'1': 'USB_SENSE', '2': 'GND'}, {'MPN': 'Yageo AC0603FR-07150KL'})
newfp('R32', 'R39', '100k', (66.3, 44.45), 180, 'B.Cu', {'1': 'VUSB', '2': 'USB_SENSE'}, {'MPN': 'Yageo AC0603FR-07100KL'})
seg((XP['10'][0], 45.6), P('R40', 1), 'USB_SENSE', 0.254, 'B.Cu')
seg(P('R40', 1), P('R39', 2), 'USB_SENSE', 0.254, 'B.Cu')
path([P('R39', 1), (73.17, 44.45), (XP['14'][0], 45.4)], 'VUSB', 0.3, 'B.Cu')

# ---- battery divider (bottom): R41 VIN->VBAT_SENSE, R42 VBAT_SENSE->GND, C50 VBAT_SENSE->GND
newfp('C15', 'C50', '0.1uF', (72.7, 34.4), 180, 'B.Cu', {'1': 'VBAT_SENSE', '2': 'GND'}, {'MPN': 'TDK CGA3E2X7R1H104K080AD'})
newfp('R32', 'R42', '220k', (72.7, 36.45), 180, 'B.Cu', {'1': 'VBAT_SENSE', '2': 'GND'}, {'MPN': 'Yageo AC0603FR-07220KL'})
newfp('R32', 'R41', '220k', (72.7, 33.0), 0, 'B.Cu', {'1': 'VIN', '2': 'VBAT_SENSE'}, {'MPN': 'Yageo AC0603FR-07220KL'})
vbs = (XP['1'][0], 34.4)
seg(vbs, P('C50', 1), 'VBAT_SENSE', 0.254, 'B.Cu')
path([vbs, P('R42', 1)], 'VBAT_SENSE', 0.254, 'B.Cu')
path([vbs, P('R41', 2)], 'VBAT_SENSE', 0.254, 'B.Cu')
via((70.6, 33.9), 'VIN'); seg((70.6, 33.9), P('R41', 1), 'VIN', 0.3, 'B.Cu')
path([P('C50', 2), P('R42', 2), (70.0, 35.45)], 'GND', 0.3, 'B.Cu')

# ---- interlock (top-right corner, between C5 and C3): Q1 2N7002 (KiCad SOT-23), R37 gate pull-down, R38 AEN pull-up
newfp('SOT-23.kicad_mod', 'Q1', '2N7002', (75.0, 3.4), 0, 'F.Cu', {'1': 'VUSB', '2': 'GND', '3': 'AEN'}, {'MPN': 'Nexperia 2N7002,215'})
newfp('R30', 'R37', '100k', (72.55, 3.4), 270, 'F.Cu', {'1': 'VUSB', '2': 'GND'}, {'MPN': 'Yageo AC0603FR-07100KL'})
newfp('R30', 'R38', '100k', (74.9, 6.15), 0, 'F.Cu', {'1': 'VIN', '2': 'AEN'}, {'MPN': 'Yageo AC0603FR-07100KL'})
log('Q1 pads', P('Q1', 1), P('Q1', 2), P('Q1', 3), 'R37', P('R37', 1), P('R37', 2), 'R38', P('R38', 1), P('R38', 2))
V5 = (73.3, 1.35)
seg(P('R37', 1), P('Q1', 1), 'VUSB'); via(V5, 'VUSB'); seg(V5, P('Q1', 1), 'VUSB')
seg(P('R37', 2), P('Q1', 2), 'GND', 0.3)
AV = (75.1, 5.0)
path([P('Q1', 3), (76.0, 5.0), P('R38', 2)], 'AEN'); via(AV, 'AEN'); seg((76.0, 5.0), AV, 'AEN')
via((73.0, 6.15), 'VIN'); seg(P('R38', 1), (73.0, 6.15), 'VIN', 0.3)
# VUSB from the XIAO 5V pad up the right edge on B.Cu (x 76.3) to the gate
path([V5, (75.3, 1.35), (76.3, 2.35), (76.3, 43.3), (XP['14'][0], 45.5)], 'VUSB', 0.3, 'B.Cu')
# AEN on B.Cu to the LM27762 EN vias (E1, E2) and on to U3 EN (E3)
E1, E2, E3 = (66.25, 10.25), (67.10, 13.60), (67.0, 18.2)
path([AV, (70.0, 5.0), (66.25, 8.75), E1], 'AEN', 0.254, 'B.Cu')
via(E3, 'AEN')
path([E1, E2], 'AEN', 0.254, 'B.Cu')
path([E2, (66.2, 14.5), (66.2, 16.6), (67.0, 17.4), E3], 'AEN', 0.254, 'B.Cu')
path([P('U3', 3), (66.75, 18.2), E3], 'AEN')

# ---- old TP6 copper (reference: TP6 at 75.5,23.75 with a via at 75.5,19.5) is where SW1 now sits
for s_ in list(kids(B, 'segment')):
    if nn(s_) == 'VIN' and any(near(pt(s_, k), q) for k in ('start', 'end') for q in ((75.5, 23.75), (75.5, 19.5))):
        B.remove(s_); log('delete old TP6 segment', pt(s_, 'start'), pt(s_, 'end'))
del_via((75.5, 19.5), 'VIN')

# ---- U3 strip (TPS7A2033, C9 out, C10 in)
path([P('U3', 5), P('C9', 1)], 'DVDD', 0.5)
path([P('C9', 1), (59.5, 20.6), (59.5, 18.5)], 'DVDD', 0.5)
path([P('C9', 2), P('U3', 4)], 'GND', 0.4)
path([P('U3', 4), P('U3', 2)], 'GND', 0.3)
via((67.2, 19.6), 'GND'); path([P('U3', 2), (67.2, 19.6), P('C10', 2)], 'GND', 0.4)
path([P('U3', 1), P('C10', 1)], 'VIN', 0.4)
via((69.6, 20.05), 'VIN'); seg(P('C10', 1), (69.6, 20.05), 'VIN', 0.4)

# ---- battery at the right-hand end: J1 (moved in edit_pcb.py) -> SW1 (C&K PCM12SMTR, actuator over the right edge)
#      -> In2 VIN plane. D6 / C49 (bottom) on J1 pin 2. TP6 (VIN) beside the U3 VIN via.
newfp('SW_SPDT_PCM12.kicad_mod', 'SW1', 'PCM12SMTR', (74.65, 17.9), 90, 'F.Cu', {'1': 'VBAT', '2': 'VIN'},
      {'MPN': 'C&K PCM12SMTR', 'LCSC': 'C221841'})
log('SW1 pads', P('SW1', 1), P('SW1', 2), P('SW1', 3), 'J1', P('J1', 1), P('J1', 2), 'D6', P('D6', 1), P('D6', 2), 'C49', P('C49', 1), P('C49', 2))
path([P('J1', 2), (72.2, 24.35), (72.2, 21.2), (72.75, 20.65), P('SW1', 1)], 'VBAT', 0.6)
seg(P('J1', 2), P('C49', 1), 'VBAT', 0.6, 'B.Cu')
seg(P('C49', 1), P('D6', 1), 'VBAT', 0.5, 'B.Cu')
via((71.9, 17.15), 'VIN'); via((71.9, 16.2), 'VIN')
seg(P('SW1', 2), (71.9, 17.15), 'VIN', 0.6); seg((71.9, 17.15), (71.9, 16.2), 'VIN', 0.6)
tp6 = fp('TP6')
kid(tp6, 'at')[1:3] = [Sym(AX(67.6)), Sym(AY(23.0))]
seg(P('C10', 1), (67.6, 23.0), 'VIN', 0.4)
log('TP6 (VIN) moved to 67.6,23.0 on C10 pin 1 (U3 input)')

# ================================================================== stitching vias that now clash with new copper
def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


newpads = []
for r in ('U6', 'J6', 'J7', 'R36', 'R37', 'R38', 'R39', 'R40', 'R41', 'R42', 'C50', 'Q1', 'TP6', 'U3', 'C9', 'C10', 'SW1', 'J1', 'D6', 'C49'):
    f = fp(r)
    fx, fy, fr = fp_at(f)
    for p in kids(f, 'pad'):
        a = kid(p, 'at'); sz = kid(p, 'size')
        dx, dy = rot(float(a[1]), float(a[2]), fr)
        newpads.append((fx + dx, fy + dy, math.hypot(float(sz[1]), float(sz[2])) / 2 + 0.15, nn(p)))   # half-diagonal; + room for the 0.45 mm SMD-to-hole rule
removed = 0
for v in list(kids(B, 'via')):
    if nn(v) != 'GND':
        continue
    c = pt(v, 'at'); r = float(val(v, 'size')) / 2
    if any(x[0] == 'via' and near(c, x[1], 0.01) for x in NEW):
        continue
    attached = any(near(pt(s, 'start'), c, r) or near(pt(s, 'end'), c, r) for s in kids(B, 'segment') if nn(s) == 'GND')
    if attached:
        continue
    clash = any(x[0] == 'seg' and x[5] != 'GND' and seg_dist(c, x[2], x[3]) < r + x[4] / 2 + 0.25 for x in NEW)
    clash = clash or any(x[0] == 'via' and x[3] != 'GND' and math.hypot(c[0] - x[1][0], c[1] - x[1][1]) < r + x[2] / 2 + 0.3 for x in NEW)
    clash = clash or any(math.hypot(c[0] - px, c[1] - py) < r + pr + 0.3 for px, py, pr, pn in newpads)
    clash = clash or c[0] > W - 0.9
    if clash:
        B.remove(v); removed += 1; log('delete GND stitching via (clashes with new copper)', '%.2f,%.2f' % c)
log('deleted %d GND stitching vias' % removed)

# ================================================================== silkscreen
for t in list(kids(B, 'gr_text')):
    a = kid(t, 'at'); x = float(a[1]) - X0
    if t[1] in ('VIN', '3v3', '+', '-') and x > 70 or t[1] == 'GND-RX-TX':
        B.remove(t); log('delete silkscreen text', t[1])
    if t[1] in ('GND', 'AVSS', 'AVDD', 'DVDD') and 55 < x < 57:
        a[1] = Sym(AX(52.2 if t[1] == 'GND' else 52.7))   # right-aligned, clear of the test-point pad (and TP1's silk ring)
        fnt = kid(kid(t, 'effects'), 'font'); kid(fnt, 'size')[1:] = [Sym('0.8'), Sym('0.8')]
        kid(fnt, 'thickness')[1] = Sym('0.15')
        kid(kid(t, 'effects'), 'justify')[1:] = [Sym('right'), Sym('bottom')]
        log('silkscreen', t[1], 'label moved left of its test point (J6 is now on its right)')
    if t[1] == 'REF SRB2':
        t[1] = 'REF  nc'; log('silkscreen REF SRB2 -> REF nc (header SRB2 pin no longer goes to the ADS1299)')
for t in list(kids(B, 'gr_text_box')):
    B.remove(t); log('delete bottom text box', t[1].strip())


def text(s, x, y, layer, size=1.0, mirror=False):
    j = ['justify', Sym('left'), Sym('bottom')] + ([Sym('mirror')] if mirror else [])
    B.append(['gr_text', s, ['at', Sym(AX(x)), Sym(AY(y)), Sym('0')], ['layer', layer], ['uuid', U()],
              ['effects', ['font', ['size', Sym(F(size)), Sym(F(size))], ['thickness', Sym('0.15')]], j]])


text('I2C: GND 3V3 SDA SCL', 55.6, 1.95, 'F.SilkS', 0.8)
text('Neuryo rev B 2026-11-08', 75.2, 38.8, 'B.SilkS', 0.8, True)
text('Low-Cost-EEG: X. Asghar', 75.2, 40.0, 'B.SilkS', 0.8, True)
text('Univ. of Bath, GPL-3.0', 75.2, 41.2, 'B.SilkS', 0.8, True)

# ================================================================== teardrops: follow a renamed track's net, drop those whose track is gone
for z in list(kids(B, 'zone')):
    if not kid(z, 'attr'):
        continue
    zp = [(float(p[1]) - X0, float(p[2]) - Y0) for p in kid(kid(z, 'polygon'), 'pts')[1:] if p[0] == 'xy']
    lay = val(z, 'layer')
    hit = {}
    for s_ in kids(B, 'segment'):
        if val(s_, 'layer') != lay:
            continue
        w = float(val(s_, 'width'))
        k = sum(1 for q in zp if seg_dist(q, pt(s_, 'start'), pt(s_, 'end')) < w / 2 + 0.05)
        if k:
            hit[nn(s_)] = hit.get(nn(s_), 0) + k
    if nn(z) in hit:
        continue
    if len(hit) == 1:
        new_net = list(hit)[0]
        log('teardrop', nn(z), '->', new_net, lay, '%.2f,%.2f' % zp[0]); kid(z, 'net')[1:] = [new_net]
        if kid(z, 'net_name'):
            kid(z, 'net_name')[1] = new_net
    else:
        B.remove(z); log('delete orphan teardrop', nn(z), lay, '%.2f,%.2f' % zp[0], hit)

# ================================================================== fields of new/changed parts copied from the schematic (parity)
if len(sys.argv) > 3:
    S = parse(open(sys.argv[3]).read())
    SY = {}
    for y in kids(S, 'symbol'):
        for p_ in kids(y, 'property'):
            if p_[1] == 'Reference':
                SY[p_[2]] = y
    for r in ('R36', 'R37', 'R38', 'R39', 'R40', 'R41', 'R42', 'C50', 'Q1', 'U6', 'J6', 'J7', 'SW1'):
        f = fp(r)
        for p_ in kids(SY[r], 'property'):
            if p_[1] in ('Reference', 'Value', 'Footprint'):
                continue
            cur = [q for q in kids(f, 'property') if q[1] == p_[1]]
            if cur:
                cur[0][2] = p_[2]
            else:
                f.insert(f.index(kids(f, 'property')[-1]) + 1,
                         ['property', p_[1], p_[2], ['at', '0', '0', '0'], ['layer', 'F.Fab'], ['hide', Sym('yes')], ['uuid', U()],
                          ['effects', ['font', ['size', '1', '1'], ['thickness', '0.15']]]])
    log('fields of the added parts copied from the schematic')

# ================================================================== reference designators of new parts that would overlap other silk
from silkplace import place_refs
top = [ref(f) for f in kids(B, 'footprint') if val(f, 'layer') == 'F.Cu' and fp_at(f)[0] > 55
       and not kid([p_ for p_ in kids(f, 'property') if p_[1] == 'Reference'][0], 'hide')] + ['R36']
place_refs(B, 'F', top, W, H, 0.8, log)
place_refs(B, 'B', ['C49', 'D6', 'R41', 'C50', 'R42', 'R40', 'R39'], W, H, 0.8, log)

# ================================================================== stack-up: JLCPCB 4-layer 1.6 mm, JLC7628
# jlcpcb.com/impedance, JLC04161H-7628: 35 um outer Cu, 7628 prepreg 0.2104 mm (er 4.4), 15.2 um inner Cu, core 1.065 mm (er 4.6),
# 7628 prepreg 0.2104 mm (er 4.4), 35 um outer Cu (sum 1.59 mm). The reference's file carried Altium's 0.59 mm template.
st = kid(kid(B, 'setup'), 'stackup')
L = {l[1]: l for l in kids(st, 'layer')}
def setthk(name, t):
    e = kid(L[name], 'thickness')
    e[1] = Sym(t)
for n, t in (('F.Cu', '0.035'), ('B.Cu', '0.035'), ('In1.Cu', '0.0152'), ('In2.Cu', '0.0152'), ('dielectric 1', '0.2104'),
             ('dielectric 2', '1.065'), ('dielectric 3', '0.2104')):
    setthk(n, t)
for n, typ, mat, er in (('dielectric 1', 'prepreg', 'FR4 7628', '4.4'), ('dielectric 2', 'core', 'FR4', '4.6'), ('dielectric 3', 'prepreg', 'FR4 7628', '4.4')):
    kid(L[n], 'type')[1] = typ; kid(L[n], 'material')[1] = mat; kid(L[n], 'epsilon_r')[1] = Sym(er)
kid(st, 'copper_finish')[1] = 'ENIG'
kid(kid(B, 'general'), 'thickness')[1] = Sym('1.6')
log('stack-up: JLC04161H-7628, 1.6 mm (35/15.2/15.2/35 um Cu, 0.2104 prepreg, 1.065 core), ENIG')

open(dst, 'w').write(dump(numify(B)) + '\n')
open(dst + '.log', 'w').write('\n'.join(LOG) + '\n')
print('\n'.join(l for l in LOG if 'stitching via (' not in l))
