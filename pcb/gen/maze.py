"""Small grid maze router used for the last few ground pads the via search cannot reach.
Finds a path on F.Cu from a pad to a spot where a via fits (or to existing ground copper)."""
import heapq, math
import pcbnew
import gnd_stitch as GS

mm = pcbnew.FromMM


def route_pad(b, sp, pad, gnd, window=4.0, step=0.05, width=0.15):
    pc = pad.GetPosition()
    n = int(window / step)
    half_w = mm(width / 2)
    r_via = mm(GS.VIA_D / 2)
    all_layers = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
    g = gnd.GetNetCode()
    # same-net copper on F.Cu (targets)
    targets = [(s, bb) for (net, L, s, bb) in sp.items if net == g and L == pcbnew.F_Cu]

    def P(i, j):
        return pcbnew.VECTOR2I(int(pc.x + mm(i * step)), int(pc.y + mm(j * step)))

    cache = {}
    def free(i, j):
        if (i, j) in cache:
            return cache[(i, j)]
        p = P(i, j)
        c = pcbnew.SHAPE_CIRCLE(p, int(half_w))
        bb = pcbnew.BOX2I(pcbnew.VECTOR2I(p.x - mm(0.6), p.y - mm(0.6)), pcbnew.VECTOR2I(mm(1.2), mm(1.2)))
        ok = sp.free(c, [pcbnew.F_Cu], g, mm(GS.CLR), bb)
        cache[(i, j)] = ok
        return ok

    def goal(i, j):
        p = P(i, j)
        d = math.hypot(p.x - pc.x, p.y - pc.y)
        if d < mm(0.7):
            return None
        # existing ground copper (not this pad)
        c = pcbnew.SHAPE_CIRCLE(p, int(half_w))
        for s, bb in targets:
            if bb.Contains(p) and s.Collide(c, 0) and not pad.HitTest(p):
                return "copper"
        if GS.in_keepout(b, p.x, p.y):
            return None
        vs = GS.via_shape(p.x, p.y, r_via)
        vb = pcbnew.BOX2I(pcbnew.VECTOR2I(p.x - mm(1.5), p.y - mm(1.5)), pcbnew.VECTOR2I(mm(3), mm(3)))
        if sp.free(vs, all_layers, g, mm(GS.CLR), vb) and sp.hole_ok(p.x, p.y, mm(GS.VIA_DRILL / 2), mm(0.35)):
            return "via"
        return None

    start = (0, 0)
    pq = [(0.0, start)]
    came = {start: None}
    cost = {start: 0.0}
    found = None
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    while pq:
        _, cur = heapq.heappop(pq)
        i, j = cur
        if cur != start and (abs(i) % 4 == 0 and abs(j) % 4 == 0):
            kind = goal(i, j)
            if kind:
                found = (cur, kind)
                break
        for di, dj in moves:
            nb = (i + di, j + dj)
            if abs(nb[0]) > n or abs(nb[1]) > n:
                continue
            on_pad = pad.HitTest(P(*nb))
            if not on_pad and not free(*nb):
                continue
            c = cost[cur] + (1.414 if di and dj else 1.0)
            if c < cost.get(nb, 1e18):
                cost[nb] = c
                came[nb] = cur
                heapq.heappush(pq, (c, nb))
    if not found:
        return False
    cell, kind = found
    path = []
    while cell is not None:
        path.append(cell); cell = came[cell]
    path.reverse()
    # simplify collinear runs
    pts = [path[0]]
    for k in range(1, len(path) - 1):
        a, m, c = pts[-1], path[k], path[k + 1]
        if (m[0] - a[0]) * (c[1] - m[1]) != (m[1] - a[1]) * (c[0] - m[0]):
            pts.append(m)
    pts.append(path[-1])
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(mm(width))
        t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t); sp.add(t, [pcbnew.F_Cu])
    if kind == "via":
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(*pts[-1])); v.SetWidth(mm(GS.VIA_D)); v.SetDrill(mm(GS.VIA_DRILL))
        v.SetNet(gnd); b.Add(v); sp.add(v, all_layers)
    return True
