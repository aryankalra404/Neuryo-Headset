"""Autoroute with Freerouting, then restore ground fills and fill all zones.

Steps: strip the full-area GND fills (they would block routing), export Specctra DSN,
move power nets into the Power class (0.4 mm), route with Freerouting, import the
session, add the fills back, fill zones and save.
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import gen_pcb as GP

K = os.path.join(os.path.dirname(__file__), "..", "kicad")
TOOLS = os.path.join(os.path.dirname(__file__), "..", "tools")
PCB = os.path.join(K, "neuryo.kicad_pcb")
DSN = os.path.join(K, "neuryo.dsn")
SES = os.path.join(K, "neuryo.ses")
FILLS = ("GND fill top", "GND fill bottom", "GND fill In2")


def strip_fills(b):
    for z in list(b.Zones()):
        if z.GetZoneName() in FILLS:
            b.Remove(z)


def patch_dsn():
    s = open(DSN).read()
    m = re.search(r"\(class kicad_default (.*?)\(circuit", s, re.S)
    names = m.group(1).split()
    pwr = [n for n in names if n in GP.POWER_NETS and n != "GND"]
    rest = [n for n in names if n not in pwr]
    s = s.replace(m.group(0), "(class kicad_default " + " ".join(rest) + "\n      (circuit")
    s = s.replace("(class Power\n", "(class Power " + " ".join(pwr) + "\n")
    # GND is not routed by Freerouting: it goes to the In1 plane and the copper fills;
    # stitching vias for SMD ground pads are added afterwards (gnd_stitch.py)
    s = re.sub(r"\n\s*\(net GND\n\s*\(pins[^)]*\)\n\s*\)", "", s)
    s = re.sub(r"\n\s*\(plane GND \(polygon[^)]*\)\)", "", s)
    s = re.sub(r"(\(class kicad_default[^(]*?) GND ", r"\1 ", s)
    # J4 pins 1 and 2 are both BIAS; the router refuses to join two pads of the same
    # connector, so pin 2 is joined to pin 1 with a short track afterwards (join_bias)
    s = s.replace("(pins D7-4 R39-2 J4-1 J4-2)", "(pins D7-4 R39-2 J4-1)")
    open(DSN, "w").write(s)
    return pwr


def main(passes=40):
    b = GP.build()
    strip_fills(b)
    b.Save(PCB)
    b = pcbnew.LoadBoard(PCB)
    assert pcbnew.ExportSpecctraDSN(b, DSN)
    print("power class:", patch_dsn())
    if os.path.exists(SES):
        os.remove(SES)
    cmd = ["java", "-jar", os.path.join(TOOLS, "freerouting.jar"), "-de", DSN, "-do", SES,
           "-mp", str(passes), f"--router.max_passes={passes}", "--gui.enabled=false"]
    print(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3000)
    log = (r.stdout + r.stderr).splitlines()
    open(os.path.join(K, "freerouting.log"), "w").write("\n".join(log))
    print("\n".join(l for l in log if "JAVA_TOOL" not in l)[-3000:])
    assert os.path.exists(SES), "no session file"
    b = pcbnew.LoadBoard(PCB)
    assert pcbnew.ImportSpecctraSES(b, SES)
    finish(b)


def finish(b):
    # restore the ground fills and fill every zone
    W, H = GP.PL.BOARD_W, GP.PL.BOARD_H
    full = [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)]
    gnd = b.FindNet("GND")
    for name, layer, prio in (("GND fill top", pcbnew.F_Cu, 0), ("GND fill bottom", pcbnew.B_Cu, 0),
                              ("GND fill In2", pcbnew.In2_Cu, 1)):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd)
        ol = z.Outline(); ol.NewOutline()
        for (x, y) in full:
            ol.Append(pcbnew.FromMM(GP.OX + x), pcbnew.FromMM(GP.OY + y))
        z.SetAssignedPriority(prio); z.SetLocalClearance(pcbnew.FromMM(0.2))
        z.SetMinThickness(pcbnew.FromMM(0.15)); z.SetZoneName(name)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(pcbnew.FromMM(0.3)); z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.4))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        b.Add(z)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetLayer() == pcbnew.In2_Cu:
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            z.SetLocalClearance(pcbnew.FromMM(0.2)); z.SetMinThickness(pcbnew.FromMM(0.15))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(PCB)
    print("saved", PCB)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
