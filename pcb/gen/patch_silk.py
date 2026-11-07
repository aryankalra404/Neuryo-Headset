"""Silkscreen clean-up on the finished board (same edits are mirrored in gen_pcb.py)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import route as RT, gen_pcb as GP

mm = pcbnew.FromMM
b = pcbnew.LoadBoard(RT.PCB)
def V(x, y): return pcbnew.VECTOR2I(mm(GP.OX + x), mm(GP.OY + y))
texts = [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT"]
drop = []
for d in texts:
    d = pcbnew.Cast_to_PCB_TEXT(d) if hasattr(pcbnew, "Cast_to_PCB_TEXT") else d
    s = d.GetText()
    if s in ("SRB", "GND", "N  P"):
        drop.append(d)
    elif s == "ELECTRODES":
        d.SetPosition(V(10.5, 32.3))
    elif s == "BATT +":
        d.SetText("BATT"); d.SetPosition(V(3.6, 78.3))
    elif s.startswith("Battery only"):
        d.SetPosition(V(66.0, 60.0))
    elif s.startswith("Never connect USB"):
        d.SetPosition(V(66.0, 62.0))
    elif s.startswith("Derived from OpenBCI"):
        d.SetPosition(V(66.0, 64.0))
for d in drop:
    b.Remove(d)
for ref in ("U9", "J1"):
    fp = b.FindFootprintByReference(ref)
    fp.Reference().SetPosition(fp.GetPosition())
for ref in ("D1", "D2"):
    b.FindFootprintByReference(ref).Reference().SetLayer(pcbnew.F_Fab)
for ref in ("J7", "J8", "J9"):
    fp = b.FindFootprintByReference(ref)
    p1 = [p for p in fp.Pads() if p.GetNumber() == "1"][0].GetPosition()
    fp.Reference().SetPosition(pcbnew.VECTOR2I(p1.x - mm(1.9), p1.y))
b.Save(RT.PCB)
print("silk patched")
