"""Render one or more copper layers of a kicad_pcb to PNG (for checking edits).
usage: python3 render.py board.kicad_pcb out.png LAYER[,LAYER] [x0 y0 x1 y1] (board coords relative to origin)"""
import sys, math, colorsys, hashlib
sys.path.insert(0, '/home/claude/kw')
from sx import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle, FancyBboxPatch
from matplotlib.transforms import Affine2D

X0, Y0 = 98.5011, 80.0036


def col(net):
    if net in ('GND', ''):
        return (0.55, 0.55, 0.55)
    h = int(hashlib.md5(net.encode()).hexdigest()[:6], 16) / 0xFFFFFF
    return colorsys.hsv_to_rgb(h, 0.75, 0.9)


def netname(e):
    n = kid(e, 'net')
    if n is None:
        return ''
    return n[2] if len(n) > 2 else n[1]


def main():
    pcb = parse(open(sys.argv[1]).read())
    out = sys.argv[2]
    layers = sys.argv[3].split(',')
    box = [float(v) for v in sys.argv[4:8]] if len(sys.argv) >= 8 else None
    labels = '--nolabels' not in sys.argv
    fig, ax = plt.subplots(figsize=(22, 13), dpi=110)
    ax.set_facecolor('black')
    for z in kids(pcb, 'zone'):
        zl = val(z, 'layer')
        if zl not in layers:
            continue
        nn = netname(z)
        for fpol in kids(z, 'filled_polygon'):
            if val(fpol, 'layer') not in layers:
                continue
            xy = [(float(p[1]) - X0, float(p[2]) - Y0) for p in kid(fpol, 'pts') if p[0] == 'xy']
            ax.add_patch(Polygon(xy, closed=True, fc=col(nn) + (0.35,), ec='none'))
        pol = kid(z, 'polygon')
        xy = [(float(p[1]) - X0, float(p[2]) - Y0) for p in kid(pol, 'pts') if p[0] == 'xy']
        if not kid(z, 'attr'):
            ax.add_patch(Polygon(xy, closed=True, fc='none', ec=col(nn), lw=1.2, ls='--'))
            cx = sum(a for a, b in xy) / len(xy); cy = sum(b for a, b in xy) / len(xy)
            if labels:
                ax.text(cx, cy, nn + ' zone', color=col(nn), fontsize=9, ha='center')
    for t in kids(pcb, 'segment'):
        if val(t, 'layer') not in layers:
            continue
        s, e = kid(t, 'start'), kid(t, 'end')
        w = float(val(t, 'width'))
        ax.plot([float(s[1]) - X0, float(e[1]) - X0], [float(s[2]) - Y0, float(e[2]) - Y0], color=col(netname(t)),
                lw=w * 72 / 25.4 * (fig.dpi / 72) * 0.0, solid_capstyle='round')
        ax.lines[-1].set_linewidth(max(0.5, w * 9))
    for t in kids(pcb, 'arc'):
        if val(t, 'layer') not in layers:
            continue
        pts = [kid(t, k) for k in ('start', 'mid', 'end')]
        ax.plot([float(p[1]) - X0 for p in pts], [float(p[2]) - Y0 for p in pts], color=col(netname(t)), lw=max(0.5, float(val(t, 'width')) * 9))
    for v in kids(pcb, 'via'):
        a = kid(v, 'at')
        ax.add_patch(Circle((float(a[1]) - X0, float(a[2]) - Y0), float(val(v, 'size')) / 2, fc=col(netname(v)), ec='white', lw=0.3))
    for fp in kids(pcb, 'footprint'):
        fa = kid(fp, 'at'); fx, fy = float(fa[1]) - X0, float(fa[2]) - Y0
        frot = float(fa[3]) if len(fa) > 3 else 0.0
        ref = [p[2] for p in kids(fp, 'property') if p[1] == 'Reference'][0]
        shown = False
        for pad in kids(fp, 'pad'):
            pl = kid(pad, 'layers')[1:]
            if not any(l in layers or l == '*.Cu' or (l == 'F&B.Cu') for l in pl):
                continue
            pa = kid(pad, 'at'); px, py = float(pa[1]), float(pa[2]); prot = float(pa[3]) if len(pa) > 3 else frot
            r = math.radians(-frot)
            gx = fx + px * math.cos(r) - py * math.sin(r); gy = fy + px * math.sin(r) + py * math.cos(r)
            sz = kid(pad, 'size'); w, h = float(sz[1]), float(sz[2])
            c = col(netname(pad))
            if pad[3] == 'circle':
                ax.add_patch(Circle((gx, gy), w / 2, fc=c, ec='white', lw=0.3, alpha=0.9))
            else:
                rect = Rectangle((gx - w / 2, gy - h / 2), w, h, fc=c, ec='white', lw=0.3, alpha=0.9)
                rect.set_transform(Affine2D().rotate_deg_around(gx, gy, -prot) + ax.transData)
                ax.add_patch(rect)
            shown = True
        if shown and labels:
            ax.text(fx, fy, ref, color='white', fontsize=7, ha='center', va='center', weight='bold')
    for g in kids(pcb, 'gr_line') + kids(pcb, 'gr_arc'):
        if val(g, 'layer') == 'Edge.Cuts':
            pts = [kid(g, k) for k in ('start', 'mid', 'end') if kid(g, k)]
            ax.plot([float(p[1]) - X0 for p in pts], [float(p[2]) - Y0 for p in pts], color='yellow', lw=1)
    ax.set_aspect('equal')
    if box:
        ax.set_xlim(box[0], box[2]); ax.set_ylim(box[3], box[1])
    else:
        ax.set_xlim(-3, 103); ax.set_ylim(53, -3)
    ax.grid(True, color='#333', lw=0.5)
    ax.set_xticks(range(int(ax.get_xlim()[0]), int(ax.get_xlim()[1]) + 1, 5))
    ax.set_title(sys.argv[1].split('/')[-1] + '  ' + ','.join(layers))
    fig.tight_layout(); fig.savefig(out, facecolor='white')


main()
