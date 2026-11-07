"""Incremental routing of the few ground pads that are boxed in by signal tracks.

The routed board is exported again with its existing tracks. Each boxed-in ground pad is
moved, together with a nearby ground pad that already has a via, onto a temporary net so
Freerouting routes a short link between them. The links are then put back on GND.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import gen_pcb as GP, route as RT

GROUPS = {"GND_T1": [("U9", "31"), ("U9", "33")],
          "GND_T2": [("U9", "41"), ("R13", "2")],
          "GND_T3": [("U4", "2"), ("U4", "5")]}
DSN2 = os.path.join(RT.K, "neuryo_fix.dsn")
SES2 = os.path.join(RT.K, "neuryo_fix.ses")

b = GP.build()
RT.strip_fills(b)
assert pcbnew.ImportSpecctraSES(b, RT.SES)
for name, pads in GROUPS.items():
    ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni)
    for ref, num in pads:
        [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0].SetNet(ni)
b.Save(os.path.join(RT.K, "neuryo_fix.kicad_pcb"))
b = pcbnew.LoadBoard(os.path.join(RT.K, "neuryo_fix.kicad_pcb"))
assert pcbnew.ExportSpecctraDSN(b, DSN2)
DSN_ORIG = RT.DSN
RT.DSN = DSN2
RT.patch_dsn()
RT.DSN = DSN_ORIG
if os.path.exists(SES2):
    os.remove(SES2)
r = subprocess.run(["timeout", "900", "java", "-jar", os.path.join(RT.TOOLS, "freerouting.jar"),
                    "-de", DSN2, "-do", SES2, "-mp", "20", "--gui.enabled=false"], capture_output=True, text=True)
print("router exit", r.returncode, "session", os.path.exists(SES2))
assert os.path.exists(SES2)
assert pcbnew.ImportSpecctraSES(b, SES2)
gnd = b.FindNet("GND")
for t in b.GetTracks():
    if t.GetNetname().startswith("GND_T"):
        t.SetNet(gnd)
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname().startswith("GND_T"):
            p.SetNet(gnd)
for name in GROUPS:
    ni = b.FindNet(name)
    if ni:
        b.Remove(ni)
b.Save(RT.PCB)
print("saved routed board with ground links")
