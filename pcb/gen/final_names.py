"""Final step: give PCB nets the schematic's names (root-sheet local labels are '/NAME')."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import route as RT

b = pcbnew.LoadBoard(RT.PCB)
n = 0
for ni in list(b.GetNetInfo().NetsByNetcode().values()):
    name = ni.GetNetname()
    if name and not name.startswith("/") and not name.startswith("unconnected"):
        ni.SetNetname("/" + name); n += 1
b.Save(RT.PCB)
pro = os.path.join(RT.K, "neuryo.kicad_pro")
d = json.load(open(pro))
for p in d["net_settings"]["netclass_patterns"]:
    if not p["pattern"].startswith("/"):
        p["pattern"] = "/" + p["pattern"]
json.dump(d, open(pro, "w"), indent=2)
print("renamed", n, "nets")

# unconnected pins: give each its own 'unconnected-(...)' net, as the schematic does
import re, subprocess
rpt = os.path.join(RT.K, "drc_parity.rpt")
subprocess.run(["kicad-cli", "pcb", "drc", "--schematic-parity", "-o", rpt, RT.PCB], capture_output=True)
want = re.findall(r"Pad missing net given by schematic \((unconnected-\(([A-Z]+\d+)(?:-[^()]*?)?-Pad(\w+)\))\)", open(rpt).read())
b = pcbnew.LoadBoard(RT.PCB)
for full, ref, num in want:
    ni = pcbnew.NETINFO_ITEM(b, full); b.Add(ni)
    for p in b.FindFootprintByReference(ref).Pads():
        if p.GetNumber() == num:
            p.SetNet(ni)
b.Save(RT.PCB)
print("unconnected pin nets", len(want))
