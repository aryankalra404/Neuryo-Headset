"""Place reference designators of the given footprints where they clear pads, silk graphics, other text and the board edge.
Used by edit_pcb2.py (rev B's crowded right-hand end). Coordinates relative to (X0, Y0)."""
import math
from sx import *

X0, Y0 = 98.5011, 80.0036


def rot(x, y, deg):
    r = math.radians(deg)
    return x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r)


def ref_prop(f):
    for p in kids(f, 'property'):
        if p[1] == 'Reference':
            return p


def fp_at(f):
    a = kid(f, 'at')
    return float(a[1]) - X0, float(a[2]) - Y0, (float(a[3]) if len(a) > 3 else 0.0)


def text_box(cx, cy, s, size, ang):
    w, h = len(s) * size * 0.95 + 0.15, size * 1.25
    if round(ang) % 180 == 90:
        w, h = h, w
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def overlap(a, b, m=0.0):
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])


def obstacles(B, side, skip_refs):
    cu, silk = ('F.Cu', 'F.SilkS') if side == 'F' else ('B.Cu', 'B.SilkS')
    mask = side + '.Mask'
    pads, gfx, texts = [], [], []
    for f in kids(B, 'footprint'):
        fx, fy, fr = fp_at(f)
        for p in kids(f, 'pad'):
            lays = [str(l) for l in kid(p, 'layers')[1:]]
            if not (mask in lays or '*.Mask' in lays):
                continue
            a = kid(p, 'at'); sz = kid(p, 'size')
            dx, dy = rot(float(a[1]), float(a[2]), fr)
            pa = float(a[3]) if len(a) > 3 else 0.0
            w, h = float(sz[1]), float(sz[2])
            c, s_ = abs(math.cos(math.radians(pa))), abs(math.sin(math.radians(pa)))
            W, H = w * c + h * s_, w * s_ + h * c
            pads.append((fx + dx - W / 2, fy + dy - H / 2, fx + dx + W / 2, fy + dy + H / 2))
        for g in kids(f, 'fp_line') + kids(f, 'fp_arc') + kids(f, 'fp_rect') + kids(f, 'fp_poly') + kids(f, 'fp_circle'):
            if val(g, 'layer') != silk:
                continue
            if g[0] == 'fp_poly':
                pts = [(float(q[1]), float(q[2])) for q in kid(g, 'pts')[1:] if q[0] == 'xy']
            elif g[0] == 'fp_circle':
                cx, cy = float(kid(g, 'center')[1]), float(kid(g, 'center')[2])
                ex, ey = float(kid(g, 'end')[1]), float(kid(g, 'end')[2])
                r = math.hypot(ex - cx, ey - cy)
                pts = [(cx + r * math.cos(t / 8 * math.pi), cy + r * math.sin(t / 8 * math.pi)) for t in range(16)]
            else:
                pts = [(float(kid(g, k)[1]), float(kid(g, k)[2])) for k in ('start', 'mid', 'end') if kid(g, k)]
            P = [rot(x, y, fr) for x, y in pts]
            P = [(fx + x, fy + y) for x, y in P]
            for a_, b_ in zip(P, P[1:] + ([P[0]] if g[0] in ('fp_poly', 'fp_circle', 'fp_rect') else [])):
                if g[0] == 'fp_rect':
                    continue
                gfx.append((min(a_[0], b_[0]) - 0.08, min(a_[1], b_[1]) - 0.08, max(a_[0], b_[0]) + 0.08, max(a_[1], b_[1]) + 0.08))
            if g[0] == 'fp_rect':
                (x1, y1), (x2, y2) = P[0], P[-1]
                for a_, b_ in (((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))):
                    gfx.append((min(a_[0], b_[0]) - 0.08, min(a_[1], b_[1]) - 0.08, max(a_[0], b_[0]) + 0.08, max(a_[1], b_[1]) + 0.08))
        rp = ref_prop(f)
        if rp is not None and ref_prop(f)[2] not in skip_refs and val(rp, 'layer') == silk and not kid(rp, 'hide'):
            a = kid(rp, 'at'); dx, dy = rot(float(a[1]), float(a[2]), fr)
            sz = float(kid(kid(kid(rp, 'effects'), 'font'), 'size')[1])
            texts.append(text_box(fx + dx, fy + dy, rp[2], sz, float(a[3]) if len(a) > 3 else 0))
    for t in kids(B, 'gr_text'):
        if val(t, 'layer') != silk:
            continue
        a = kid(t, 'at'); x, y = float(a[1]) - X0, float(a[2]) - Y0
        sz = float(kid(kid(kid(t, 'effects'), 'font'), 'size')[1])
        j = kid(kid(t, 'effects'), 'justify')
        js = [str(v) for v in j[1:]] if j else []
        w = len(t[1]) * sz * 0.95; h = sz * 1.25
        x0 = x if 'left' in js else (x - w if 'right' in js else x - w / 2)
        if 'mirror' in js:
            x0 = x - w if 'left' in js else (x if 'right' in js else x - w / 2)
        y0 = y - h if 'bottom' in js else (y if 'top' in js else y - h / 2)
        texts.append((x0, y0, x0 + w, y0 + h))
    return pads, gfx, texts


def place_refs(B, side, refs, W, H, size=0.8, log=print):
    pads, gfx, texts = obstacles(B, side, set(refs))
    placed = []
    for r in refs:
        f = [g for g in kids(B, 'footprint') if ref_prop(g)[2] == r][0]
        fx, fy, fr = fp_at(f)
        own = []
        for p in kids(f, 'pad'):
            a = kid(p, 'at'); dx, dy = rot(float(a[1]), float(a[2]), fr); own.append((fx + dx, fy + dy))
        cx = sum(x for x, y in own) / len(own); cy = sum(y for x, y in own) / len(own)
        best = None
        for ang in (0, 90):
            for i in range(-30, 31):
                for k in range(-30, 31):
                    x, y = cx + i * 0.2, cy + k * 0.2
                    b = text_box(x, y, r, size, ang)
                    if b[0] < 0.4 or b[1] < 0.4 or b[2] > W - 0.4 or b[3] > H - 0.4:
                        continue
                    if any(overlap(b, o, 0.2) for o in pads) or any(overlap(b, o, 0.1) for o in gfx) or any(overlap(b, o, 0.15) for o in texts + placed):
                        continue
                    d = math.hypot(x - cx, y - cy) + (0.3 if ang else 0)
                    if best is None or d < best[0]:
                        best = (d, x, y, ang, b)
        if best is None:
            log('silk: no free spot for', r); continue
        d, x, y, ang, b = best
        placed.append(b)
        rp = ref_prop(f)
        lx, ly = rot(x - fx, y - fy, -fr)
        a = kid(rp, 'at'); a[1:] = [Sym('%.3f' % lx), Sym('%.3f' % ly), Sym('%g' % ang)]
        fnt = kid(kid(rp, 'effects'), 'font'); kid(fnt, 'size')[1:] = [Sym('%g' % size), Sym('%g' % size)]
        th = kid(fnt, 'thickness')
        if th:
            th[1] = Sym('0.12')
        else:
            fnt.append(['thickness', Sym('0.12')])
        log('silk: %s ref at %.2f,%.2f %d (%.1f mm from its pads)' % (r, x, y, ang, d))
