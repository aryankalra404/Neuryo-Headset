"""Last three ground connections the router could not reach (found by maze search):
U9-41 DAISY_IN joins GPIO1 (pin 42) per design.py; U9-31 and U4-2 get small 0.45/0.2 mm vias."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import route as RT, gnd_stitch as GS

mm = pcbnew.FromMM
b = pcbnew.LoadBoard(RT.PCB)
gnd = b.FindNet("GND")

def pad(ref, num):
    return [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0]

# remove zero-length leftovers on the three pads
for t in list(b.GetTracks()):
    if t.GetClass() == "PCB_TRACK" and t.GetStart() == t.GetEnd():
        b.Remove(t)

p41, p42 = pad("U9", "41"), pad("U9", "42")
p41.SetNet(p42.GetNet())
t = pcbnew.PCB_TRACK(b); t.SetStart(p41.GetPosition()); t.SetEnd(p42.GetPosition())
t.SetWidth(mm(0.15)); t.SetLayer(pcbnew.F_Cu); t.SetNet(p42.GetNet()); b.Add(t)

for (ref, num, dx, dy) in (("U9", "31", 0.0, 0.75), ("U4", "2", 0.35, 0.1)):
    p = pad(ref, num)
    c = p.GetPosition()
    end = pcbnew.VECTOR2I(c.x + mm(dx), c.y + mm(dy))
    v = pcbnew.PCB_VIA(b); v.SetPosition(end); v.SetWidth(mm(0.45)); v.SetDrill(mm(0.2)); v.SetNet(gnd); b.Add(v)
    s = pcbnew.PCB_TRACK(b); s.SetStart(c); s.SetEnd(end); s.SetWidth(mm(0.15)); s.SetLayer(pcbnew.F_Cu)
    s.SetNet(gnd); b.Add(s)

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(RT.PCB)
print("patched")
