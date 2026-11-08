"""Rev B board from the imported Low-Cost-EEG board.
usage: python3 edit_pcb.py in.kicad_pcb out.kicad_pcb
All coordinates below are relative to the reference board's top-left corner (X0, Y0) = (98.5011, 80.0036)."""
import sys, copy, math, uuid, json
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


def log(*a):
    LOG.append(' '.join(str(x) for x in a))


def nn(e):
    n = kid(e, 'net')
    return (n[2] if len(n) > 2 else n[1]) if n else ''


def ref(fp):
    for p in kids(fp, 'property'):
        if p[1] == 'Reference':
            return p[2]


def fps(r=None):
    return [f for f in kids(B, 'footprint') if r is None or ref(f) == r]


def fp_at(fp):
    a = kid(fp, 'at')
    return float(a[1]) - X0, float(a[2]) - Y0, (float(a[3]) if len(a) > 3 else 0.0)


def rot(x, y, deg):
    r = math.radians(deg)
    return x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r)


def pad_list(fp):
    fx, fy, fr = fp_at(fp)
    out = []
    for p in kids(fp, 'pad'):
        a = kid(p, 'at')
        dx, dy = rot(float(a[1]), float(a[2]), fr)
        sz = kid(p, 'size')
        out.append(dict(num=str(p[1]), x=fx + dx, y=fy + dy, w=float(sz[1]), h=float(sz[2]), ang=float(a[3]) if len(a) > 3 else 0.0,
                        layers=[str(l) for l in kid(p, 'layers')[1:]], net=nn(p), el=p))
    return out


def pad(r, num):
    for p in pad_list(fps(r)[0]):
        if p['num'] == str(num):
            return p
    raise KeyError((r, num))


# ------------------------------------------------------------------ 1. parts removed (ESP32-S3 module side)
DEL = 'U5 C11 C12 C13 R7 R8 SW2 SW3 U2 C6 C7 J2 C48 D7 R5 R6 J5 TP5'.split()
moved_or_deleted_nets = set()
FREED = []   # (x, y) of deleted pads, so dangling copper ending there is trimmed
for f in list(kids(B, 'footprint')):
    r = ref(f)
    fx, fy, fr = fp_at(f)
    if r in DEL or (r == '' and fx > 90):     # the two right-hand mounting holes (x = 95)
        for p in pad_list(f):
            moved_or_deleted_nets.add(p['net']); FREED.append(dict(p))
        B.remove(f); log('delete footprint', r or 'mounting hole at x=%.0f y=%.0f' % (fx, fy))

# copper polygons that belonged to U2 (x>78, y>17) and the ESP32 thermal pad (67.4,39.35); U3's polygons are re-laid below
for g in list(kids(B, 'gr_poly')):
    pts = [(float(p[1]) - X0, float(p[2]) - Y0) for p in kid(g, 'pts')[1:]]
    if val(g, 'layer') == 'F.Cu':
        B.remove(g); log('delete copper polygon', nn(g), '%.1f,%.1f' % pts[0])

# ------------------------------------------------------------------ 2. moved parts
def move(r, nx, ny, nrot=None, layer=None):
    f = fps(r)[0]
    for p in pad_list(f):
        moved_or_deleted_nets.add(p['net']); FREED.append(dict(p))
    a = kid(f, 'at')
    old = float(a[3]) if len(a) > 3 else 0.0
    a[1], a[2] = Sym(AX(nx)), Sym(AY(ny))
    if nrot is not None and nrot != old:
        d = nrot - old
        while len(a) < 4:
            a.append(Sym('0'))
        a[3] = Sym('%g' % nrot)
        for p in kids(f, 'pad') + kids(f, 'property'):
            pa = kid(p, 'at')
            if len(pa) > 3:
                pa[3] = Sym('%g' % ((float(pa[3]) + d) % 360))
            else:
                pa.append(Sym('%g' % (d % 360)))
    log('move', r, 'to %.2f,%.2f rot %s' % (nx, ny, nrot if nrot is not None else old))


# U3 (TPS7A2033) with C9 (out) and C10 (in): same order and spacing as the reference, moved into the strip under the
# LM27762 block (no room for its 5.5 mm tall copper polygons on a 77 mm board).
DX3, DY3 = -19.55, 7.95
for r in ('U3', 'C9', 'C10'):
    x, y, a = fp_at(fps(r)[0]); move(r, x + DX3, y + DY3)
move('SW1', 51.8, 43.3)                    # battery on/off (top-actuated slide), bottom-left where the UART header and boot button were
move('J1', 45.0, 46.1, 0)                  # battery JST-PH at the bottom edge, opening down
move('D6', 47.6, 46.2)                     # VBAT TVS (bottom side) beside J1
move('C49', 49.0, 42.0)                    # VBAT 4.7 uF (bottom side) beside SW1

# ------------------------------------------------------------------ 3. LM27762 EN+ (pin 12) and EN- (pin 8) off VIN -> AEN
def segs():
    return kids(B, 'segment')


def vias():
    return kids(B, 'via')


def pt(e, k):
    a = kid(e, k)
    return float(a[1]) - X0, float(a[2]) - Y0


def near(p, q, tol=0.02):
    return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol


def set_net(e, name):
    kid(e, 'net')[1:] = [name]


AEN_COPPER = [((66.25, 10.25), (66.34, 10.25)), ((66.34, 10.25), (66.59, 10.50)), ((66.59, 10.50), (67.30, 10.50)),
              ((67.10, 13.60), (67.10, 13.53)), ((67.10, 13.53), (67.30, 13.33)), ((67.30, 13.33), (67.30, 12.50))]
for s in segs():
    a, b = pt(s, 'start'), pt(s, 'end')
    for p, q in AEN_COPPER:
        if (near(a, p) and near(b, q)) or (near(a, q) and near(b, p)):
            set_net(s, 'AEN'); log('segment %s-%s VIN -> AEN' % (p, q))
for v in vias():
    if near(pt(v, 'at'), (66.25, 10.25)) or near(pt(v, 'at'), (67.10, 13.60)):
        set_net(v, 'AEN'); log('via %s VIN -> AEN' % (pt(v, 'at'),))
for r, num in (('U1', 8), ('U1', 12), ('U3', 3)):
    set_net(pad(r, num)['el'], 'AEN')

# ------------------------------------------------------------------ 4. other net changes on kept parts
for p in kids(fps('SW1')[0], 'pad'):
    if str(p[1]) == '3':
        p.remove(kid(p, 'net'))
# change 1: R27/C31 node moves from SRB1 to SRB2; header SRB2 pin + D5 IO4 become SRB2_HDR
for r, num, new in (('R27', 2, 'SRB2'), ('C31', 1, 'SRB2'), ('J3J', 2, 'SRB2_HDR'), ('D5', 5, 'SRB2_HDR')):
    set_net(pad(r, num)['el'], new)
for p in kids(fps('U4')[0], 'pad'):
    if str(p[1]) == '17':
        p.remove(kid(p, 'net'))
# change 5: R10 value
for p in kids(fps('R10')[0], 'property'):
    if p[1] == 'Value':
        p[2] = '51k'

# ------------------------------------------------------------------ 5. trim copper left dangling (affected nets only)
PROTECT = {'DRDY', 'CS', 'MOSI', 'SCLK', 'MISO', 'ADS_START', 'SRB1', 'SRB2'}


def zone_polys():
    out = []
    for z in kids(B, 'zone'):
        if kid(z, 'attr'):
            continue
        pts = [(float(p[1]) - X0, float(p[2]) - Y0) for p in kid(kid(z, 'polygon'), 'pts')[1:] if p[0] == 'xy']
        lay = val(z, 'layer')
        lays = [lay] if lay else [str(l) for l in kid(z, 'layers')[1:]]
        out.append((nn(z), lays, pts))
    return out


def in_poly(p, poly):
    x, y = p; c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def on_pad(p, pd, layer):
    lay_ok = any(l == layer or l == '*.Cu' or (l.startswith('*') and layer.endswith('.Cu')) for l in pd['layers'])
    if not lay_ok:
        return False
    dx, dy = p[0] - pd['x'], p[1] - pd['y']
    rx, ry = rot(dx, dy, -pd['ang'])
    return abs(rx) <= pd['w'] / 2 + 0.01 and abs(ry) <= pd['h'] / 2 + 0.01


def prune(nets):
    allpads = [p for f in kids(B, 'footprint') for p in pad_list(f)]
    padsby = {}
    for p in allpads:
        padsby.setdefault(p['net'], []).append(p)
    Z = zone_polys()
    removed = 0
    while True:
        S = [s for s in segs() if nn(s) in nets]
        V = [v for v in vias() if nn(v) in nets]
        Sby, Vby = {}, {}
        for s in S:
            Sby.setdefault(nn(s), []).append((s, val(s, 'layer'), pt(s, 'start'), pt(s, 'end'), float(val(s, 'width'))))
        for v in V:
            Vby.setdefault(nn(v), []).append((v, pt(v, 'at'), float(val(v, 'size')) / 2))
        kill = []
        for n, L in Sby.items():
            for s, lay, a, b, w in L:
                for e in (a, b):
                    if e[0] > 76.5 or any(on_pad(e, p, lay) for p in FREED) and not any(on_pad(e, p, lay) for p in padsby.get(n, [])):
                        kill.append(s); break
                    ok = any(on_pad(e, p, lay) for p in padsby.get(n, []))
                    ok = ok or any(math.hypot(e[0] - c[0], e[1] - c[1]) <= r + 0.01 for v, c, r in Vby.get(n, []))
                    ok = ok or any(o is not s and ol == lay and seg_dist(e, oa, ob) <= ow / 2 + 0.01 for o, ol, oa, ob, ow in L)
                    ok = ok or any(zn == n and lay in zl and in_poly(e, zp) for zn, zl, zp in Z)
                    if not ok:
                        kill.append(s); break
        for n, L in Vby.items():
            for v, c, r in L:
                if c[0] > 76.4:
                    kill.append(v); continue
                hits = sum(1 for s, lay, a, b, w in Sby.get(n, []) if min(math.hypot(c[0] - a[0], c[1] - a[1]), math.hypot(c[0] - b[0], c[1] - b[1])) <= r + 0.01)
                ok = hits >= 2 or any(on_pad(c, p, l) for p in padsby.get(n, []) for l in ('F.Cu', 'B.Cu'))
                ok = ok or any(zn == n and in_poly(c, zp) for zn, zl, zp in Z)
                if not ok:
                    kill.append(v)
        if not kill:
            return removed
        for k in kill:
            B.remove(k); removed += 1
            log('trim %s %s %s' % (k[0], nn(k), (pt(k, 'start'), pt(k, 'end')) if k[0] == 'segment' else pt(k, 'at')))


# zones: the In2 3v3 plane (under the ESP32) and the In2 VIN plane become one VIN plane; old VIN polygon kept as is
for z in kids(B, 'zone'):
    if not kid(z, 'attr') and nn(z) == '3v3' and val(z, 'layer') == 'In2.Cu':
        set_net(z, 'VIN'); log('In2 zone 3v3 (under the old module) -> VIN, same outline')
        pts = kid(kid(z, 'polygon'), 'pts')
        # extend its top edge up to y=20.5 on the right so it overlaps the old VIN polygon (x 73.75-77)
        new = [(54.25, 50.0), (78.0, 50.0), (78.0, 20.5), (73.75, 20.5), (73.75, 31.75), (54.25, 31.75)]
        kid(z, 'polygon')[1] = ['pts'] + [[Sym('xy'), Sym(AX(x)), Sym(AY(y))] for x, y in new]
for z in kids(B, 'zone'):
    for fp_ in kids(z, 'filled_polygon'):
        z.remove(fp_)

affected = (moved_or_deleted_nets | {'VIN', 'GND', 'VBAT', 'DVDD', '3v3', 'VBUS', 'ADS_RESET', 'PWDN'}) - PROTECT - {''}
n = prune(affected)
log('trimmed %d dangling segments/vias on nets: %s' % (n, ' '.join(sorted(affected))))

# ------------------------------------------------------------------ 6. teardrops whose pad/via is gone
allpads = [p for f in kids(B, 'footprint') for p in pad_list(f)]
for z in list(kids(B, 'zone')):
    if not kid(z, 'attr'):
        continue
    pts = [(float(p[1]) - X0, float(p[2]) - Y0) for p in kid(kid(z, 'polygon'), 'pts')[1:] if p[0] == 'xy']
    n_ = nn(z)
    lay = val(z, 'layer')
    keep = any(p['net'] == n_ and any(on_pad(q, p, lay) or math.hypot(q[0] - p['x'], q[1] - p['y']) < max(p['w'], p['h']) for q in pts) for p in allpads)
    keep = keep or any(nn(v) == n_ and any(math.hypot(q[0] - pt(v, 'at')[0], q[1] - pt(v, 'at')[1]) < float(val(v, 'size')) for q in pts) for v in vias())
    keep = keep and any(nn(s) == n_ and any(seg_dist(q, pt(s, 'start'), pt(s, 'end')) < 0.6 for q in pts) for s in segs())
    if not keep:
        B.remove(z); log('delete teardrop', n_, '%.1f,%.1f' % pts[0])

open(dst, 'w').write(dump(numify(B)) + '\n')
open(dst + '.log', 'w').write('\n'.join(LOG) + '\n')
print('\n'.join(l for l in LOG if not l.startswith('trim') and not l.startswith('delete teardrop')))
print('trim lines:', sum(1 for l in LOG if l.startswith('trim')), ' teardrops deleted:', sum(1 for l in LOG if l.startswith('delete teardrop')))
