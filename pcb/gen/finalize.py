"""Rebuild the board, import the routed session, add ground vias and fills, then clean up
dangling vias/tracks reported by DRC until none are left."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import gen_pcb as GP, route as RT, gnd_stitch as GS

def drc():
    rpt = os.path.join(RT.K, "drc.rpt")
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-error", "--severity-warning", "-o", rpt, RT.PCB],
                   capture_output=True)
    return open(rpt).read()

def coords(rep, kind):
    out = []
    for blk in re.split(r"\n(?=\[)", rep):
        if blk.startswith(f"[{kind}]"):
            m = re.search(r"@\(([\d.]+) mm, ([\d.]+) mm\)", blk)
            if m:
                out.append((float(m.group(1)), float(m.group(2))))
    return out

if "--from-pcb" in sys.argv:
    b = pcbnew.LoadBoard(RT.PCB)          # already routed (fix_route.py)
else:
    b = GP.build()
    RT.strip_fills(b)
    assert pcbnew.ImportSpecctraSES(b, RT.SES)
if "--from-pcb" in sys.argv:
    GS.stitch(b, pads=False, grid=True)
else:
    GS.join_bias(b)
    GS.stitch(b)
b.Save(RT.PCB)
b = pcbnew.LoadBoard(RT.PCB)
RT.finish(b)
# vias into any ground-fill island on F.Cu/B.Cu that has no connection of its own
b = pcbnew.LoadBoard(RT.PCB)
added = GS.island_vias(b)
if added:
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(RT.PCB)
print("island vias", added)
for it in range(3):
    rep = drc()
    dv = coords(rep, "via_dangling"); dt = coords(rep, "track_dangling")
    if not dv and not dt:
        break
    b = pcbnew.LoadBoard(RT.PCB)
    removed = 0
    for t in list(b.GetTracks()):
        p = t.GetPosition() if t.GetClass() == "PCB_VIA" else t.GetStart()
        pts = [(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))]
        if t.GetClass() != "PCB_VIA":
            pts.append((pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)))
        targets = dv if t.GetClass() == "PCB_VIA" else dt
        if any(abs(x - X) < 0.01 and abs(y - Y) < 0.01 for (x, y) in pts for (X, Y) in targets):
            print("  remove", t.GetClass(), t.GetNetname(), [round(v - 50, 2) for v in pts[0]])
            b.Remove(t); removed += 1
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(RT.PCB)
    print(f"cleanup pass {it+1}: removed {removed}")
rep = drc()
print(re.findall(r"\*\* Found .*\*\*", rep))
