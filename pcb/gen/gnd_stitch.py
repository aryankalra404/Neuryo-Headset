"""Import the routed session, give every SMD ground pad its own via to the In1 GND plane,
add ground stitching vias across the fills, fill zones and save."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import route as RT
import gen_pcb as GP

mm, ToMM = pcbnew.FromMM, pcbnew.ToMM
VIA_D, VIA_DRILL, CLR = 0.5, 0.25, 0.15


def via_shape(x, y, r):
    return pcbnew.SHAPE_CIRCLE(pcbnew.VECTOR2I(int(x), int(y)), int(r))


class Space:
    """Collision checks against copper of other nets on every layer."""
    def __init__(self, b, gnd):
        self.b, self.gnd = b, gnd
        self.items = []
        layers = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
        for fp in b.GetFootprints():
            for p in fp.Pads():
                for L in layers:
                    if p.IsOnLayer(L):
                        self.items.append((p.GetNetCode(), L, p.GetEffectiveShape(L), p.GetBoundingBox()))
        for t in b.GetTracks():
            for L in layers:
                if t.IsOnLayer(L):
                    self.items.append((t.GetNetCode(), L, t.GetEffectiveShape(L), t.GetBoundingBox()))
        self.edge = b.GetBoardEdgesBoundingBox()
        self.holes = []   # (x, y, radius) of every drilled hole, any net
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetDrillSize().x > 0:
                    self.holes.append((p.GetPosition().x, p.GetPosition().y, max(p.GetDrillSize().x, p.GetDrillSize().y) / 2))
        for t in b.GetTracks():
            if t.GetClass() == "PCB_VIA":
                self.holes.append((t.GetPosition().x, t.GetPosition().y, t.GetDrillValue() / 2))

    def hole_ok(self, x, y, r, gap):
        for hx, hy, hr in self.holes:
            if math.hypot(hx - x, hy - y) < hr + r + gap:
                return False
        return True

    def free(self, shape, layers, net, clearance, bbox):
        for n, L, s, bb in self.items:
            if L not in layers:
                continue
            if n == net and net > 0:
                continue
            if not bb.Intersects(bbox):
                continue
            if s.Collide(shape, int(clearance)):
                return False
        return True

    def add(self, item, layers):
        if item.GetClass() == "PCB_VIA":
            self.holes.append((item.GetPosition().x, item.GetPosition().y, item.GetDrillValue() / 2))
        for L in layers:
            self.items.append((item.GetNetCode(), L, item.GetEffectiveShape(L), item.GetBoundingBox()))


def in_keepout(b, x, y):
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias() and z.Outline().Contains(pcbnew.VECTOR2I(int(x), int(y))):
            return True
    return False


def grid_via(b, sp, pad, gnd, reach=3.5, step=0.1):
    """Search a fine grid around the pad for the closest free via spot reachable by a straight track."""
    pc = pad.GetPosition(); r = mm(VIA_D / 2)
    all_layers = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
    pts = []
    n = int(reach / step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            d = math.hypot(i, j) * step
            if 0.6 <= d <= reach:
                pts.append((d, pc.x + mm(i * step), pc.y + mm(j * step)))
    pts.sort()
    for d, x, y in pts:
        if in_keepout(b, x, y):
            continue
        vs = via_shape(x, y, r)
        vb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(x - mm(1.5)), int(y - mm(1.5))), pcbnew.VECTOR2I(mm(3), mm(3)))
        if not sp.free(vs, all_layers, gnd.GetNetCode(), mm(CLR), vb):
            continue
        if not sp.hole_ok(x, y, mm(VIA_DRILL / 2), mm(0.35)):
            continue
        end = pcbnew.VECTOR2I(int(x), int(y))
        seg = pcbnew.SHAPE_SEGMENT(pc, end, mm(0.2))
        sb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(min(pc.x, x) - mm(1)), int(min(pc.y, y) - mm(1))),
                          pcbnew.VECTOR2I(int(abs(pc.x - x) + mm(2)), int(abs(pc.y - y) + mm(2))))
        if not sp.free(seg, [pcbnew.F_Cu], gnd.GetNetCode(), mm(CLR), sb):
            continue
        v = pcbnew.PCB_VIA(b); v.SetPosition(end); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL))
        v.SetNet(gnd); b.Add(v)
        t = pcbnew.PCB_TRACK(b); t.SetStart(pc); t.SetEnd(end); t.SetWidth(mm(0.2)); t.SetLayer(pcbnew.F_Cu)
        t.SetNet(gnd); b.Add(t)
        sp.add(v, all_layers); sp.add(t, [pcbnew.F_Cu])
        return True
    return False


def link_to_nearest(b, sp, pad, gnd):
    """Join a ground pad to the nearest ground pad/via with a straight F.Cu track."""
    pc = pad.GetPosition()
    cands = []
    for fp in b.GetFootprints():
        for q in fp.Pads():
            if q.GetNetCode() == gnd.GetNetCode() and q is not pad and q.IsOnLayer(pcbnew.F_Cu):
                cands.append(q.GetPosition())
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA" and t.GetNetCode() == gnd.GetNetCode():
            cands.append(t.GetPosition())
    cands.sort(key=lambda q: math.hypot(q.x - pc.x, q.y - pc.y))
    cands = [q for q in cands if math.hypot(q.x - pc.x, q.y - pc.y) > mm(0.05)]
    for q in cands[:25]:
        if math.hypot(q.x - pc.x, q.y - pc.y) > mm(6):
            break
        seg = pcbnew.SHAPE_SEGMENT(pc, q, mm(0.2))
        bb = pcbnew.BOX2I(pcbnew.VECTOR2I(min(pc.x, q.x) - mm(1), min(pc.y, q.y) - mm(1)),
                          pcbnew.VECTOR2I(abs(pc.x - q.x) + mm(2), abs(pc.y - q.y) + mm(2)))
        if sp.free(seg, [pcbnew.F_Cu], gnd.GetNetCode(), mm(CLR), bb):
            t = pcbnew.PCB_TRACK(b); t.SetStart(pc); t.SetEnd(q); t.SetWidth(mm(0.2))
            t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t); sp.add(t, [pcbnew.F_Cu])
            return True
    return False


def stitch(b, pads=True, grid=True):
    gnd = b.FindNet("GND")
    sp = Space(b, gnd.GetNetCode())
    all_layers = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
    r = mm(VIA_D / 2)
    placed, failed = 0, []
    edge = b.GetBoardEdgesBoundingBox()
    for fp in (b.GetFootprints() if pads else []):
        c = fp.GetPosition()
        for p in fp.Pads():
            if p.GetNetCode() != gnd.GetNetCode() or p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            pc = p.GetPosition()
            sz = p.GetBoundingBox()
            half = max(sz.GetWidth(), sz.GetHeight()) / 2
            dx, dy = pc.x - c.x, pc.y - c.y
            base = math.atan2(dy, dx) if (dx or dy) else 0.0
            ok = False
            for k in range(16):
                ang = base + (k // 2 + (k % 2)) * (math.pi / 8) * (1 if k % 2 == 0 else -1)
                for extra in (0.0, 0.25, 0.5, 0.8, 1.2):
                    d = half + r + mm(0.12 + extra)
                    x, y = pc.x + d * math.cos(ang), pc.y + d * math.sin(ang)
                    if not (edge.GetLeft() + mm(0.8) < x < edge.GetRight() - mm(0.8) and
                            edge.GetTop() + mm(0.8) < y < edge.GetBottom() - mm(0.8)):
                        continue
                    if in_keepout(b, x, y):
                        continue
                    vs = via_shape(x, y, r)
                    vb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(x - r - mm(1)), int(y - r - mm(1))),
                                      pcbnew.VECTOR2I(int(2 * r + mm(2)), int(2 * r + mm(2))))
                    if not sp.free(vs, all_layers, gnd.GetNetCode(), mm(CLR), vb):
                        continue
                    if not sp.hole_ok(x, y, mm(VIA_DRILL / 2), mm(0.35)):
                        continue
                    seg = pcbnew.SHAPE_SEGMENT(pc, pcbnew.VECTOR2I(int(x), int(y)), mm(0.25))
                    sb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(min(pc.x, x) - mm(1)), int(min(pc.y, y) - mm(1))),
                                      pcbnew.VECTOR2I(int(abs(pc.x - x) + mm(2)), int(abs(pc.y - y) + mm(2))))
                    if not sp.free(seg, [pcbnew.F_Cu], gnd.GetNetCode(), mm(CLR), sb):
                        continue
                    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
                    v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNet(gnd); b.Add(v)
                    t = pcbnew.PCB_TRACK(b); t.SetStart(pc); t.SetEnd(pcbnew.VECTOR2I(int(x), int(y)))
                    t.SetWidth(mm(0.25)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t)
                    sp.add(v, all_layers); sp.add(t, [pcbnew.F_Cu])
                    placed += 1; ok = True
                    break
                if ok:
                    break
            if not ok:
                ok = grid_via(b, sp, p, gnd)
            if not ok:
                import maze
                ok = maze.route_pad(b, sp, p, gnd)
            if not ok:
                ok = link_to_nearest(b, sp, p, gnd)
            if not ok:
                failed.append(f"{fp.GetReference()}-{p.GetNumber()}")
    # stitching grid (ties the F.Cu/B.Cu fills to the plane)
    grid = 0
    W, H = GP.PL.BOARD_W, GP.PL.BOARD_H
    y = 2.0 if grid else H
    while y < H - 1.5:
        x = 2.0
        while x < W - 1.5:
            X, Y = mm(GP.OX + x), mm(GP.OY + y)
            if not in_keepout(b, X, Y):
                vs = via_shape(X, Y, r)
                vb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(X - mm(1.5)), int(Y - mm(1.5))), pcbnew.VECTOR2I(mm(3), mm(3)))
                if sp.free(vs, all_layers, -1, mm(0.3), vb) and sp.hole_ok(X, Y, mm(VIA_DRILL / 2), mm(0.6)):
                    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(X, Y))
                    v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNet(gnd); b.Add(v)
                    sp.add(v, all_layers); grid += 1
            x += 4.0
        y += 4.0
    print(f"ground pad vias {placed}, stitching vias {grid}, pads without via {failed}")
    return failed


def island_vias(b):
    """Put a via into every GND fill island on the outer layers that contains no via or THT pad."""
    gnd = b.FindNet("GND")
    sp = Space(b, gnd.GetNetCode())
    anchors = [t.GetPosition() for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == gnd.GetNetCode()]
    anchors += [p.GetPosition() for fp in b.GetFootprints() for p in fp.Pads()
                if p.GetNetCode() == gnd.GetNetCode() and p.GetDrillSize().x > 0]
    r = mm(VIA_D / 2); added = 0
    all_layers = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
    for z in b.Zones():
        if z.GetNetCode() != gnd.GetNetCode() or z.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu):
            continue
        polys = z.GetFilledPolysList(z.GetLayer())
        for i in range(polys.OutlineCount()):
            ol = polys.Outline(i)
            if any(polys.Contains(a, i) for a in anchors):
                continue
            bb = ol.BBox()
            done = False
            step = mm(0.25)
            y = bb.GetTop() + r
            while y < bb.GetBottom() - r and not done:
                x = bb.GetLeft() + r
                while x < bb.GetRight() - r and not done:
                    c = pcbnew.VECTOR2I(int(x), int(y))
                    inside = all(polys.Contains(pcbnew.VECTOR2I(int(x + dx), int(y + dy)), i)
                                 for dx, dy in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)))
                    if inside:
                        vs = via_shape(x, y, r)
                        vb = pcbnew.BOX2I(pcbnew.VECTOR2I(int(x - mm(1.5)), int(y - mm(1.5))), pcbnew.VECTOR2I(mm(3), mm(3)))
                        if sp.free(vs, all_layers, gnd.GetNetCode(), mm(CLR), vb) and sp.hole_ok(x, y, mm(VIA_DRILL / 2), mm(0.35)):
                            v = pcbnew.PCB_VIA(b); v.SetPosition(c); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL))
                            v.SetNet(gnd); b.Add(v); sp.add(v, all_layers); anchors.append(c); added += 1; done = True
                    x += step
                y += step
    return added


def join_bias(b):
    join_pair(b, "J4", "1", "2")   # both BIAS
    join_pair(b, "J5", "1", "2")   # both +3V3_MCU (devkit 3V3 pins)


def join_pair(b, ref, n1, n2):
    """Join two pads of one connector that carry the same net with a short track."""
    j = b.FindFootprintByReference(ref)
    p1 = [p for p in j.Pads() if p.GetNumber() == n1][0]
    p2 = [p for p in j.Pads() if p.GetNumber() == n2][0]
    sp = Space(b, 0)
    seg = pcbnew.SHAPE_SEGMENT(p1.GetPosition(), p2.GetPosition(), mm(0.3))
    bb = pcbnew.BOX2I(pcbnew.VECTOR2I(p1.GetPosition().x - mm(1), p1.GetPosition().y - mm(1)),
                      pcbnew.VECTOR2I(abs(p2.GetPosition().x - p1.GetPosition().x) + mm(2), mm(2)))
    for L in (pcbnew.B_Cu, pcbnew.F_Cu):
        if sp.free(seg, [L], p1.GetNetCode(), mm(CLR), bb):
            t = pcbnew.PCB_TRACK(b); t.SetStart(p1.GetPosition()); t.SetEnd(p2.GetPosition())
            t.SetWidth(mm(0.3)); t.SetLayer(L); t.SetNet(p1.GetNet()); b.Add(t)
            print(f"{ref} pins {n1}-{n2} joined on", b.GetLayerName(L))
            return True
    print(f"WARNING: could not join {ref} pins {n1} and {n2}")
    return False


if __name__ == "__main__":
    b = pcbnew.LoadBoard(RT.PCB)
    if len(sys.argv) > 1 and sys.argv[1] == "--import":
        assert pcbnew.ImportSpecctraSES(b, RT.SES)
    join_bias(b)
    stitch(b)
    RT.finish(b)
