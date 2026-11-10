"""Rev B board, 4th pass (review of 10 Nov 2026, REVB-4TH-PASS-PLAN.md).
usage: python3 edit_pcb4.py in.kicad_pcb out.kicad_pcb STEPS [lib_dir [schematic, for step H]]
STEPS: letters of the plan's steps to apply, in order (e.g. A, AB, ABC ... ABCDEF).
lib_dir: folder with Neuryo_RevB.pretty; with step A the XIAO library footprint there is edited too.
H copies the MPN/LCSC fields of the schematic onto the footprints (needs the schematic as 5th argument).
Coordinates: mm from the board's top-left corner, y down (file = these + X0/Y0), as edit_pcb2.py."""
import sys, copy, math, uuid, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sx import *

X0, Y0 = 98.5011, 80.0036
src, dst, STEPS = sys.argv[1], sys.argv[2], sys.argv[3]
LIB = sys.argv[4] if len(sys.argv) > 4 else None
B = parse(open(src).read())
LOG = []
U = lambda: str(uuid.uuid4())
F = lambda v: '%.4f' % v
AX = lambda x: F(x + X0)
AY = lambda y: F(y + Y0)


def log(*a):
    LOG.append(' '.join(str(x) for x in a))


def nn(e):
    n = kid(e, 'net')
    return n[-1] if n else ''


def ref(f):
    for p in kids(f, 'property'):
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


def pad(r, n):
    return [p for p in kids(fp(r), 'pad') if str(p[1]) == str(n)][0]


def pt(e, k):
    a = kid(e, k)
    return float(a[1]) - X0, float(a[2]) - Y0


def near(p, q, tol=0.03):
    return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol


def seg(a, b, net, w=0.254, layer='F.Cu'):
    e = ['segment', ['start', Sym(AX(a[0])), Sym(AY(a[1]))], ['end', Sym(AX(b[0])), Sym(AY(b[1]))], ['width', Sym(F(w))],
         ['layer', layer], ['net', net], ['uuid', U()]]
    B.insert(B.index(kids(B, 'segment')[-1]) + 1, e)
    log('add segment', net, layer, '(%.2f,%.2f)-(%.2f,%.2f)' % (a + b), 'w%.3f' % w)
    return e


def path(pts, net, w=0.254, layer='F.Cu'):
    for a, b in zip(pts, pts[1:]):
        seg(a, b, net, w, layer)


def via(c, net, size=0.6, drill=0.3):
    e = ['via', ['at', Sym(AX(c[0])), Sym(AY(c[1]))], ['size', Sym(F(size))], ['drill', Sym(F(drill))], ['layers', 'F.Cu', 'B.Cu'],
         ['tenting', ['front', Sym('yes')], ['back', Sym('yes')]], ['net', net], ['uuid', U()]]
    B.insert(B.index(kids(B, 'via')[-1]) + 1, e)
    log('add via', net, '(%.2f,%.2f)' % c)
    return e


def find_seg(a, b, net=None, layer=None):
    for s in kids(B, 'segment'):
        p, q = pt(s, 'start'), pt(s, 'end')
        if ((near(p, a) and near(q, b)) or (near(p, b) and near(q, a))) and (net is None or nn(s) == net) \
                and (layer is None or val(s, 'layer') == layer):
            return s
    raise KeyError(('segment', a, b, net))


def del_seg(a, b, net=None, layer=None):
    s = find_seg(a, b, net, layer)
    B.remove(s)
    log('delete segment', nn(s), val(s, 'layer'), '(%.2f,%.2f)-(%.2f,%.2f)' % (a + b))
    return s


def split_seg(a, b, m, net, layer):
    """replace segment a-b by a-m and m-b (same width, net, layer); m must lie on it"""
    s = del_seg(a, b, net, layer)
    w = float(val(s, 'width'))
    seg(a, m, net, w, layer); seg(m, b, net, w, layer)


def set_seg_net(a, b, net, layer=None):
    s = find_seg(a, b, None, layer)
    log('segment net', nn(s), '->', net, '(%.2f,%.2f)-(%.2f,%.2f)' % (a + b))
    kid(s, 'net')[1:] = [net]


def set_via_net(c, net):
    for v in kids(B, 'via'):
        if near(pt(v, 'at'), c):
            log('via net', nn(v), '->', net, '(%.2f,%.2f)' % c)
            kid(v, 'net')[1:] = [net]
            return
    raise KeyError(('via', c))


def set_pad_net(r, n, net):
    p = pad(r, n)
    for e in kids(p, 'net'):
        p.remove(e)
    if net:
        p.insert(p.index(kid(p, 'layers')) + 1, ['net', net])
    log('pad net', '%s.%s' % (r, n), '->', net or '(none)')


def clone(src_ref, refd, value, at, rot_, nets, fields):
    """copy an existing footprint (same side) to a new reference, position and rotation"""
    f = copy.deepcopy(fp(src_ref))
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
    for p in list(kids(f, 'property')):
        if p[1] == 'Reference':
            p[2] = refd
        elif p[1] == 'Value':
            p[2] = value
        elif p[1] not in ('Datasheet', 'Description'):
            f.remove(p)
    for k, v in fields.items():
        cur = [q for q in kids(f, 'property') if q[1] == k]
        if cur:
            cur[0][2] = v
        else:
            f.insert(f.index(kids(f, 'property')[-1]) + 1,
                     ['property', k, v, ['at', '0', '0', '0'], ['layer', 'F.Fab'], ['hide', Sym('yes')], ['uuid', U()],
                      ['effects', ['font', ['size', '1', '1'], ['thickness', '0.15']]]])
    for p in kids(f, 'pad'):
        for e in kids(p, 'net'):
            p.remove(e)
        n = nets.get(str(p[1]))
        if n:
            p.insert(p.index(kid(p, 'layers')) + 1, ['net', n])
    B.insert(B.index(kids(B, 'footprint')[-1]) + 1, f)
    log('add footprint', refd, value, 'at %.2f,%.2f rot %g %s (clone of %s)' % (at[0], at[1], rot_, val(f, 'layer'), src_ref))
    return f


def place_r(src_ref, refd, value, at, rot_, n1, n2, toward1, fields):
    """0603 with pad 1 (net n1) on the side nearer the point toward1"""
    clone(src_ref, refd, value, at, rot_, {'1': n1, '2': n2}, fields)
    p1, p2 = P(refd, 1), P(refd, 2)
    if math.dist(p1, toward1) > math.dist(p2, toward1):
        B.remove(fp(refd)); LOG.pop()
        clone(src_ref, refd, value, at, (rot_ + 180) % 360, {'1': n1, '2': n2}, fields)
    log('  %s pad1 %s (%.2f,%.2f)  pad2 %s (%.2f,%.2f)' % ((refd, n1) + P(refd, 1) + (n2,) + P(refd, 2)))
    return P(refd, 1), P(refd, 2)


def text(s_, x, y, layer, size=0.8, justify=None):
    j = list(justify or [])
    if layer.startswith('B.'):
        j.append(Sym('mirror'))
    eff = ['effects', ['font', ['size', Sym(F(size)), Sym(F(size))], ['thickness', Sym('0.15')]]]
    if j:
        eff.append(['justify'] + [Sym(x_) for x_ in j])
    B.append(['gr_text', s_, ['at', Sym(AX(x)), Sym(AY(y)), Sym('0')], ['layer', layer], ['uuid', U()], eff])
    log('add text', repr(s_), layer, '(%.2f,%.2f)' % (x, y), ' '.join(j) or 'centred')


def testpad(refd, net, at, side, fields):
    """1.0 mm round SMD test pad: mask open, no paste (Neuryo_RevB:TP_SMD_D1.0), on side 'F' or 'B'"""
    L = lambda l: (side + '.' + l)
    mir = [Sym('mirror')] if side == 'B' else []
    f = ['footprint', 'Neuryo_RevB:TP_SMD_D1.0', ['layer', L('Cu')], ['uuid', U()], ['at', Sym(AX(at[0])), Sym(AY(at[1]))]]
    for k, v, lay, hide in (('Reference', refd, L('Fab'), False), ('Value', 'TP', L('Fab'), True),
                            ('Datasheet', '', L('Fab'), True), ('Description', 'Test pad 1.0 mm, no paste', L('Fab'), True)):
        e = ['property', k, v, ['at', '0', '-1.2' if k == 'Reference' else '0', '0'], ['layer', lay]]
        if hide:
            e.append(['hide', Sym('yes')])
        e += [['uuid', U()], ['effects', ['font', ['size', '0.5', '0.5'], ['thickness', '0.08']]] + ([['justify'] + mir] if mir else [])]
        f.append(e)
    for k, v in fields.items():
        f.append(['property', k, v, ['at', '0', '0', '0'], ['layer', L('Fab')], ['hide', Sym('yes')], ['uuid', U()],
                  ['effects', ['font', ['size', '1', '1'], ['thickness', '0.15']]]])
    f.append(['attr', Sym('smd'), Sym('exclude_from_pos_files'), Sym('exclude_from_bom')])
    f.append(['fp_circle', ['center', '0', '0'], ['end', '0.75', '0'], ['stroke', ['width', '0.05'], ['type', Sym('solid')]],
              ['fill', Sym('no')], ['layer', L('CrtYd')], ['uuid', U()]])
    f.append(['pad', '1', Sym('smd'), Sym('circle'), ['at', '0', '0'], ['size', '1', '1'], ['layers', L('Cu'), L('Mask')],
              ['net', net], ['uuid', U()]])
    f.append(['embedded_fonts', Sym('no')])
    B.insert(B.index(kids(B, 'footprint')[-1]) + 1, f)
    log('add test pad', refd, net, '(%.2f,%.2f)' % at, side + '.Cu')
    return f


R_FIELDS = lambda v, mpn, lcsc, desc: {'MPN': mpn, 'LCSC': lcsc, 'Description': desc}

# ================================================================== A: XIAO battery pads through-hole, no paste on XIAO pads
if 'A' in STEPS:
    def fix_xiao(f, where):
        for p in kids(f, 'pad'):
            n = str(p[1])
            lay = kid(p, 'layers')
            if n in ('23', '24'):
                p[2] = Sym('thru_hole')
                lay[1:] = ['*.Cu', '*.Mask']
                if not kid(p, 'drill'):
                    p.insert(p.index(lay), ['drill', Sym('0.7')])
                for k in ('solder_paste_margin',):
                    for e in kids(p, k):
                        p.remove(e)
                log(where, 'pad', n, 'thru_hole, drill 0.7, *.Cu *.Mask')
            elif n in [str(k) for k in range(1, 15)] + ['25']:
                lay[1:] = [l for l in lay[1:] if l != 'F.Paste']
            elif n in [str(k) for k in range(15, 23)]:
                lay[1:] = ['F.Cu']
        log(where, 'pads 1-14 and 25: F.Paste removed (F.Cu F.Mask); pads 15-22 F.Cu only')
    fix_xiao(fp('U6'), 'U6')
    if LIB:
        mp = os.path.join(LIB, 'Neuryo_RevB.pretty', 'XIAO-ESP32-S3-SMD.kicad_mod')
        M = parse(open(mp).read())
        fix_xiao(M, 'library XIAO-ESP32-S3-SMD')
        open(mp, 'w').write(dump(numify(M)) + '\n')

# ================================================================== B: interlock labels (silkscreen only)
# There is no free 11 mm strip on the top silkscreen around Q1 (top-right corner: I2C label, R3/R4/C5, R37/Q1/R38, C3/C2),
# so "Q1: USB interlock" goes on the bottom silkscreen directly behind Q1; the bench warning goes below R39/R40, under the
# attribution block (the strip straight under the block is taken by R39/R40 and their labels).
if 'B' in STEPS:
    text('Q1: USB interlock', 70.3, 2.3, 'B.SilkS')
    text('No Q1 = bench only,', 69.5, 46.6, 'B.SilkS')     # below R39/R40, beside the attribution block
    text('never on a person', 69.5, 47.8, 'B.SilkS')

# ================================================================== C: 330 ohm in series on SCLK, MOSI, CS (pad 1 on the XIAO side)
R330 = R_FIELDS('330', 'UNI-ROYAL 0603WAF3300T5E', 'C23138', 'RES 330R 1% 1/10W 0603')
if 'C' in STEPS:
    # SCLK: vertical F.Cu run (63.96, 26.43) -> (63.96, 30.90) into XIAO pad 5 (D4)
    del_seg((63.96, 26.43), (63.96, 30.90), 'SCLK')
    a1, a2 = place_r('R30', 'R43', '330', (63.96, 28.2), 90, 'SCLK_X', 'SCLK', (63.96, 31.0), R330)
    seg((63.96, 26.43), a2, 'SCLK'); seg(a1, (63.96, 30.90), 'SCLK_X')
    set_pad_net('U6', 5, 'SCLK_X')
    # MOSI: F.Cu run at y 28.25 to the via at (60.00, 28.25); the via, the B.Cu run and the last F.Cu bends become MOSI_X
    del_seg((45.33, 28.25), (60.00, 28.25), 'MOSI')
    b1, b2 = place_r('R30', 'R44', '330', (57.75, 28.25), 0, 'MOSI_X', 'MOSI', (60.0, 28.25), R330)
    seg((45.33, 28.25), b2, 'MOSI'); seg(b1, (60.00, 28.25), 'MOSI_X')
    set_via_net((60.00, 28.25), 'MOSI_X'); set_via_net((67.25, 28.25), 'MOSI_X')
    set_seg_net((60.00, 28.25), (67.25, 28.25), 'MOSI_X', 'B.Cu')
    set_seg_net((67.25, 28.25), (66.50, 29.00), 'MOSI_X', 'F.Cu'); set_seg_net((66.50, 29.00), (66.50, 30.90), 'MOSI_X', 'F.Cu')
    set_pad_net('U6', 4, 'MOSI_X')
    # CS: no room for an in-line 0603 between DRDY (y 21.75) and MISO (y 23.72); R28 stays on the ADS1299 side.
    # The diagonal F.Cu run (62.67,22.60)-(69.04,28.97) drops to B.Cu between two vias on its own line; R45 on the bottom,
    # along the same line (135 deg: a bottom-side part's rotation is mirrored).
    VA, VB = (63.80, 23.73), (67.20, 27.13)
    del_seg((62.67, 22.60), (69.04, 28.97), 'CS')
    seg((62.67, 22.60), VA, 'CS'); via(VA, 'CS')
    c1, c2 = place_r('R39', 'R45', '330', (65.50, 25.43), 135, 'CS_X', 'CS', VB, R330)
    seg(VA, c2, 'CS', 0.254, 'B.Cu'); seg(c1, VB, 'CS_X', 0.254, 'B.Cu')
    via(VB, 'CS_X'); seg(VB, (69.04, 28.97), 'CS_X')
    set_seg_net((69.04, 28.97), (69.04, 30.90), 'CS_X', 'F.Cu')
    set_pad_net('U6', 3, 'CS_X')

# ================================================================== D: I2C pull-ups 4.7k to XIAO_3V3 (bottom)
R4K7 = R_FIELDS('4.7k', 'UNI-ROYAL 0603WAF4701T5E', 'C23162', 'RES 4.7k 1% 1/10W 0603')
if 'D' in STEPS:
    # R46 SDA: between the B.Cu XIAO_3V3 run (y 41.5) and the I2C_SDA run (y 44.4), under the XIAO body
    split_seg((56.65, 41.50), (69.04, 41.50), (60.20, 41.50), 'XIAO_3V3', 'B.Cu')
    split_seg((56.20, 44.40), (61.42, 44.40), (60.20, 44.40), 'I2C_SDA', 'B.Cu')
    d1, d2 = place_r('R40', 'R46', '4.7k', (60.20, 42.95), 90, 'I2C_SDA', 'XIAO_3V3', (60.2, 44.4), R4K7)
    seg((60.20, 41.50), d2, 'XIAO_3V3', 0.3, 'B.Cu'); seg(d1, (60.20, 44.40), 'I2C_SDA', 0.254, 'B.Cu')
    # R47 SCL: bottom side between the J6 and J7 columns (x 58.3 / 61.3): 3V3 row y 7.14, SCL row y 12.22
    e1, e2 = place_r('R40', 'R47', '4.7k', (59.80, 9.68), 90, 'I2C_SCL', 'XIAO_3V3', (59.8, 12.22), R4K7)
    path([e2, (59.80, 7.14), P('J6', 2)], 'XIAO_3V3', 0.3, 'B.Cu')
    path([e1, (59.80, 12.22), P('J6', 4)], 'I2C_SCL', 0.254, 'B.Cu')
    # its two silk body lines would run over the J6/J7 SDA pads (0.1 mm in): drop them on R47 only (the label stays)
    for g in list(kids(fp('R47'), 'fp_line')):
        if val(g, 'layer') == 'B.SilkS':
            fp('R47').remove(g)
    log('R47: B.SilkS body lines removed (would overlap the J6.3/J7.3 pads)')

# ================================================================== E: XIAO D10 (GPIO9) -> ADS1299 RESET
if 'E' in STEPS:
    VR, VX = (54.30, 26.10), (66.50, 45.75)
    seg((48.75, 26.10), VR, 'ADS_RESET')          # the reference's own RESET corridor; the only edit at x < 56
    via(VR, 'ADS_RESET')
    path([VR, (54.30, 46.90), (66.50, 46.90), VX], 'ADS_RESET', 0.254, 'B.Cu')
    via(VX, 'ADS_RESET'); seg(VX, (66.50, 47.10), 'ADS_RESET')
    set_pad_net('U6', 11, 'ADS_RESET')

# ================================================================== F: test pads (no paste) on MISO, DRDY, AEN
if 'F' in STEPS:
    TPF = {'MPN': '(copper test pad, not assembled)'}
    m = (61.50, 25.25)        # on the B.Cu MISO run between its two vias
    split_seg((60.50, 24.25), (62.50, 26.25), m, 'MISO', 'B.Cu')
    testpad('TP7', 'MISO', m, 'B', TPF)
    text('MISO', 61.5, 26.75, 'B.SilkS', 0.8)
    d = (65.83, 24.50)        # on the F.Cu DRDY diagonal, where CS no longer runs beside it (step C)
    split_seg((63.08, 21.75), (71.58, 30.25), d, 'DRDY', 'F.Cu')
    testpad('TP8', 'DRDY', d, 'F', TPF)
    text('DRDY', 63.6, 24.5, 'F.SilkS', 0.8)
    e = (68.50, 6.50)         # on the B.Cu AEN diagonal (70,5)-(66.25,8.75)
    split_seg((70.00, 5.00), (66.25, 8.75), e, 'AEN', 'B.Cu')
    testpad('TP9', 'AEN', e, 'B', TPF)
    text('AEN', 70.6, 7.3, 'B.SilkS', 0.8)

# ================================================================== H: part-number fields copied from the schematic (schematic parity)
if 'H' in STEPS:
    S = parse(open(sys.argv[5]).read())
    for y in kids(S, 'symbol'):
        props = {p[1]: p[2] for p in kids(y, 'property')}
        r = props.get('Reference', '')
        if r.startswith('#') or 'LCSC' not in props or not [f for f in kids(B, 'footprint') if ref(f) == r]:
            continue
        f = fp(r)
        for k in ('MPN', 'LCSC'):
            cur = [q for q in kids(f, 'property') if q[1] == k]
            if cur and cur[0][2] == props[k]:
                continue
            if cur:
                cur[0][2] = props[k]
            else:
                f.insert(f.index(kids(f, 'property')[-1]) + 1,
                         ['property', k, props[k], ['at', '0', '0', '0'], ['layer', 'F.Fab'], ['hide', Sym('yes')], ['uuid', U()],
                          ['effects', ['font', ['size', '1', '1'], ['thickness', '0.15']]]])
            log('field', r, k, '->', props[k])

# ================================================================== reference designators of the new parts (silkscreen)
new = [r for r in ('R43', 'R44', 'R45', 'R46', 'R47') if [f for f in kids(B, 'footprint') if ref(f) == r]]
if new:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from silkplace import place_refs
    top = [r for r in new if val(fp(r), 'layer') == 'F.Cu']
    bot = [r for r in new if val(fp(r), 'layer') == 'B.Cu']
    if top:
        place_refs(B, 'F', top, 77.0, 50.0, 0.8, log)
    if bot:
        place_refs(B, 'B', bot, 77.0, 50.0, 0.8, log)

open(dst, 'w').write(dump(numify(B)) + '\n')
open(dst + '.log', 'w').write('\n'.join(LOG) + '\n')
print('\n'.join(LOG))
