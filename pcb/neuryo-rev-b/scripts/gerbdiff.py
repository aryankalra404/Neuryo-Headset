"""Gerber comparison of rev B's analog half against the upstream Low-Cost-EEG Gerbers (REVB-4TH-PASS-PLAN section 3).

The plan's snippet uses gerbonara + cairosvg; neither could be installed on the build machine (no package downloads), so
this is a small RS-274X rasterizer with numpy/PIL/scipy that covers what both Gerber sets use: C/R/O/P apertures, aperture
macros (primitives 1, 4, 5, 20, 21, with $n arithmetic), D01/D02/D03, regions (G36/G37), LPD/LPC and G75 arcs (G02/G03).
The comparison itself follows the plan: same windows, 40 px/mm, XOR, binary opening x2, labelled regions.

usage: python3 gerbdiff.py <upstream Gerber dir> <rev B fab dir> [--save out_dir]
       python3 gerbdiff.py --revb <older rev B fab dir> <newer rev B fab dir>   (whole 77 x 50 board, same layer list;
       regions are listed with the half they are in, so a pass can be checked for changes at x < 56)"""
import sys, os, re, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

PPM = 40


class Raster:
    def __init__(self, bounds, ppm=PPM):
        (self.x0, self.y0), (x1, y1) = bounds
        self.y1 = y1
        self.ppm = ppm
        self.w, self.h = int(round((x1 - self.x0) * ppm)), int(round((y1 - self.y0) * ppm))
        self.im = Image.new('1', (self.w, self.h), 0)
        self.d = ImageDraw.Draw(self.im)

    def P(self, x, y):
        return ((x - self.x0) * self.ppm, (self.y1 - y) * self.ppm)

    def poly(self, pts, v):
        if len(pts) >= 3:
            self.d.polygon([self.P(*p) for p in pts], fill=v)

    def circle(self, c, dia, v):
        x, y = self.P(*c); r = dia / 2 * self.ppm
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=v)

    def line(self, a, b, width, v):
        if width <= 0:
            return
        (ax, ay), (bx, by) = a, b
        L = math.hypot(bx - ax, by - ay)
        if L > 1e-9:
            nx, ny = -(by - ay) / L * width / 2, (bx - ax) / L * width / 2
            self.poly([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)], v)
        self.circle(a, width, v); self.circle(b, width, v)

    def array(self):
        return np.array(self.im, dtype=bool)


def rotp(p, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def ev(expr, args):
    e = re.sub(r'\$(\d+)', lambda m: repr(args[int(m.group(1)) - 1]) if int(m.group(1)) <= len(args) else '0', expr)
    e = e.replace('x', '*').replace('X', '*')
    return float(eval(e, {'__builtins__': {}}))


def macro_shapes(body, args):
    """-> list of (kind, data, exposure, rotation) in aperture coordinates"""
    out, args = [], list(args)
    for stmt in body:
        stmt = stmt.strip()
        if not stmt or stmt.startswith('0'):
            continue
        if stmt.startswith('$'):            # variable definition
            k, v = stmt[1:].split('=', 1); i = int(k)
            while len(args) < i:
                args.append(0.0)
            args[i - 1] = ev(v, args); continue
        f = [ev(t, args) for t in stmt.split(',')]
        code = int(f[0])
        if code == 1:
            exp, dia, cx, cy = f[1], f[2], f[3], f[4]; rot = f[5] if len(f) > 5 else 0
            out.append(('circle', (rotp((cx, cy), rot), dia), exp))
        elif code == 20:
            exp, w, xs, ys, xe, ye, rot = f[1:8]
            out.append(('line', (rotp((xs, ys), rot), rotp((xe, ye), rot), w), exp))
        elif code == 21:
            exp, w, h, cx, cy, rot = f[1:7]
            pts = [rotp((cx + dx, cy + dy), rot) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
            out.append(('poly', pts, exp))
        elif code == 4:
            exp, n = f[1], int(f[2])
            pts = [(f[3 + 2 * i], f[4 + 2 * i]) for i in range(n + 1)]
            rot = f[3 + 2 * (n + 1)]
            out.append(('poly', [rotp(p, rot) for p in pts], exp))
        elif code == 5:
            exp, n, cx, cy, dia, rot = f[1:7]
            pts = [rotp((cx + dia / 2 * math.cos(2 * math.pi * i / n), cy + dia / 2 * math.sin(2 * math.pi * i / n)), rot) for i in range(int(n))]
            out.append(('poly', pts, exp))
        else:
            raise ValueError('macro primitive %d not supported' % code)
    return out


def render(path, bounds, ppm=PPM):
    txt = open(path, errors='replace').read()
    R = Raster(bounds, ppm)
    fmt_dec, scale = 4, 1.0
    m = re.search(r'%FS[LTDA]*X(\d)(\d)Y\d\d\*%', txt)
    if m:
        fmt_dec = int(m.group(2))
    if '%MOIN*%' in txt:
        scale = 25.4
    macros, aps = {}, {}
    for mm in re.finditer(r'%AM([^*]+)\*(.*?)%', txt, re.S):
        macros[mm.group(1)] = [s for s in mm.group(2).replace('\n', '').split('*') if s.strip()]
    for ma in re.finditer(r'%ADD(\d+)([A-Za-z_][\w.]*?)(?:,([^*]*))?\*%', txt):
        aps[int(ma.group(1))] = (ma.group(2), [float(v) for v in ma.group(3).split('X')] if ma.group(3) else [])
    body = re.sub(r'%[^%]*%', '', txt)
    cur, pos, interp, region, rpts, pol = None, (0.0, 0.0), 1, False, [], 1
    pols = [(m_.start(), 1 if m_.group(1) == 'D' else 0) for m_ in re.finditer(r'%LP([DC])\*%', txt)]
    # walk statements in file order so polarity changes interleave correctly
    stmts = re.split(r'(%[^%]*%)', txt)
    for chunk in stmts:
        if chunk.startswith('%'):
            if chunk.startswith('%LP'):
                pol = 1 if 'LPD' in chunk else 0
            continue
        for st in chunk.replace('\n', '').split('*'):
            st = st.strip()
            if not st or st.startswith('G04'):
                continue
            g = re.match(r'^G0?([0-9]+)(.*)$', st)
            while g:
                code = int(g.group(1))
                if code == 1: interp = 1
                elif code == 2: interp = 2
                elif code == 3: interp = 3
                elif code == 36: region, rpts = True, []
                elif code == 37:
                    R.poly(rpts, pol); region, rpts = False, []
                st = g.group(2)
                g = re.match(r'^G0?([0-9]+)(.*)$', st)
            if not st:
                continue
            dsel = re.match(r'^D(\d+)$', st)
            if dsel and int(dsel.group(1)) >= 10:
                cur = int(dsel.group(1)); continue
            mo = re.match(r'^(?:X([+-]?\d+))?(?:Y([+-]?\d+))?(?:I([+-]?\d+))?(?:J([+-]?\d+))?D0?([123])$', st)
            if not mo:
                continue
            num = lambda s_: int(s_) / 10 ** fmt_dec * scale
            x = num(mo.group(1)) if mo.group(1) is not None else pos[0]
            y = num(mo.group(2)) if mo.group(2) is not None else pos[1]
            i = num(mo.group(3)) if mo.group(3) else 0.0
            j = num(mo.group(4)) if mo.group(4) else 0.0
            d = int(mo.group(5))
            new = (x, y)
            if d == 2:
                if region:
                    if len(rpts) >= 3:
                        R.poly(rpts, pol)
                    rpts = [new]
                pos = new; continue
            if d == 1:
                pts = [pos, new]
                if interp in (2, 3):
                    c = (pos[0] + i, pos[1] + j)
                    a0 = math.atan2(pos[1] - c[1], pos[0] - c[0]); a1 = math.atan2(new[1] - c[1], new[0] - c[0])
                    r = math.hypot(pos[0] - c[0], pos[1] - c[1])
                    if interp == 3:
                        while a1 <= a0: a1 += 2 * math.pi
                    else:
                        while a1 >= a0: a1 -= 2 * math.pi
                    n = max(8, int(abs(a1 - a0) * r * ppm / 2))
                    pts = [(c[0] + r * math.cos(a0 + (a1 - a0) * k / n), c[1] + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
                if region:
                    if not rpts:
                        rpts = [pos]
                    rpts += pts[1:]
                else:
                    t, p_ = aps[cur]
                    w = p_[0] if t == 'C' else (min(p_[0], p_[1]) if t in ('R', 'O') else 0.1)
                    for a, b in zip(pts, pts[1:]):
                        R.line(a, b, w, pol)
                pos = new; continue
            if d == 3:
                pos = new
                t, p_ = aps[cur]
                if t == 'C':
                    R.circle(pos, p_[0], pol)
                elif t == 'R':
                    w, h = p_[0], p_[1]
                    R.poly([(pos[0] - w / 2, pos[1] - h / 2), (pos[0] + w / 2, pos[1] - h / 2), (pos[0] + w / 2, pos[1] + h / 2), (pos[0] - w / 2, pos[1] + h / 2)], pol)
                elif t == 'O':
                    w, h = p_[0], p_[1]
                    if w > h:
                        R.line((pos[0] - (w - h) / 2, pos[1]), (pos[0] + (w - h) / 2, pos[1]), h, pol)
                    else:
                        R.line((pos[0], pos[1] - (h - w) / 2), (pos[0], pos[1] + (h - w) / 2), w, pol)
                elif t == 'P':
                    dia, n = p_[0], int(p_[1]); rot = p_[2] if len(p_) > 2 else 0
                    R.poly([(pos[0] + dia / 2 * math.cos(math.radians(rot) + 2 * math.pi * k / n), pos[1] + dia / 2 * math.sin(math.radians(rot) + 2 * math.pi * k / n)) for k in range(n)], pol)
                else:
                    for kind, data, exp in macro_shapes(macros[t], p_):
                        v = pol if exp else 1 - pol
                        if kind == 'circle':
                            R.circle((pos[0] + data[0][0], pos[1] + data[0][1]), data[1], v)
                        elif kind == 'line':
                            (a, b, w) = data
                            ax, ay, bx, by = pos[0] + a[0], pos[1] + a[1], pos[0] + b[0], pos[1] + b[1]
                            L = math.hypot(bx - ax, by - ay)
                            if L > 0:
                                nx, ny = -(by - ay) / L * w / 2, (bx - ax) / L * w / 2
                                R.poly([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)], v)
                        else:
                            R.poly([(pos[0] + x_, pos[1] + y_) for x_, y_ in data], v)
    return R.array()


PAIRS = [('GTL', 'Top Layer.gtl'), ('G1', 'GND Layer.g1'), ('G2', 'Power Layer.g2'), ('GBL', 'Bottom Layer.gbl'),
         ('GTS', 'Top Solder.gts'), ('GBS', 'Bottom Solder.gbs'), ('GTP', 'Top Paste.gtp'), ('GBP', 'Bottom Paste.gbp')]

def revb_vs_revb(a_dir, b_dir):
    for _, b in PAIRS:
        o = render(os.path.join(a_dir, 'Neuryo_RevB-' + b), ((98.5, -130), (175.5, -80)))
        r = render(os.path.join(b_dir, 'Neuryo_RevB-' + b), ((98.5, -130), (175.5, -80)))
        diff = ndi.binary_opening(o ^ r, iterations=2)
        lab, n = ndi.label(diff)
        regs = []
        for k, sl in enumerate(ndi.find_objects(lab), 1):
            ys, xs = sl
            area = (lab[sl] == k).sum() / PPM ** 2
            gone = (o[sl] & (lab[sl] == k)).sum() > (r[sl] & (lab[sl] == k)).sum()
            regs.append((xs.start / PPM, xs.stop / PPM, ys.start / PPM, ys.stop / PPM, area, 'removed' if gone else 'added'))
        left = [g for g in regs if g[0] < 56]
        print('%-22s regions: %d (x < 56: %d)' % (b, n, len(left)))
        for g in sorted(regs, key=lambda g: (g[0] >= 56, g[2], g[0])):
            print('     %s x %5.2f-%5.2f  y %5.2f-%5.2f  %.3f mm2  %s' % ((('<56' if g[0] < 56 else '   '),) + g))


if __name__ == '__main__':
    if sys.argv[1] == '--revb':
        revb_vs_revb(sys.argv[2], sys.argv[3]); sys.exit()
    up, rb = sys.argv[1], sys.argv[2]
    save = sys.argv[sys.argv.index('--save') + 1] if '--save' in sys.argv else None
    for a, b in PAIRS:
        o = render(os.path.join(up, 'ADS ESP EEG.' + a), ((0, 0), (56, 50)))
        r = render(os.path.join(rb, 'Neuryo_RevB-' + b), ((98.5, -130), (154.5, -80)))
        h, w = min(o.shape[0], r.shape[0]), min(o.shape[1], r.shape[1])
        diff = ndi.binary_opening(o[:h, :w] ^ r[:h, :w], iterations=2)
        lab, n = ndi.label(diff)
        print('%-4s different regions: %d' % (a, n))
        for k, sl in enumerate(ndi.find_objects(lab), 1):
            ys, xs = sl
            area = (lab[sl] == k).sum() / PPM ** 2
            only_up = (o[:h, :w][sl] & (lab[sl] == k)).sum() > (r[:h, :w][sl] & (lab[sl] == k)).sum()
            # board frame: mm from the top-left corner, y down (upstream Gerber y = 50 - board y)
            print('     x %5.2f-%5.2f  y %5.2f-%5.2f  %.3f mm2  %s' % (xs.start / PPM, xs.stop / PPM, ys.start / PPM, ys.stop / PPM, area,
                                                                 'copper/opening only upstream' if only_up else 'only on rev B'))
        if save:
            os.makedirs(save, exist_ok=True)
            im = np.zeros((h, w, 3), np.uint8); im[o[:h, :w] & r[:h, :w]] = (120, 120, 120)
            im[o[:h, :w] & ~r[:h, :w]] = (220, 40, 40); im[r[:h, :w] & ~o[:h, :w]] = (40, 90, 230)
            Image.fromarray(im).save(os.path.join(save, 'gerbdiff-%s.png' % a))
