"""Build the Neuryo PCB (placement, nets, outline, zones) with the KiCad 8 pcbnew API."""
import os, sys, uuid
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import design as D
import placement as PL

OUT = os.path.join(os.path.dirname(__file__), "..", "kicad")
FPLIB = "/usr/share/kicad/footprints/"
OX, OY = 50.0, 50.0           # board origin on the KiCad page
mm = pcbnew.FromMM

def V(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))

def sym_uuid(ref):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "neuryo/" + ref))

# Power class (0.4 mm). The ADS1299 rails (+2V5, -2V5, +3V3_D) stay at 0.25 mm: a 0.4 mm track
# cannot reach the 0.5 mm-pitch TQFP pins without breaking clearance; they also use the In2 pours.
POWER_NETS = {"VBUS", "VBAT", "BAT_N", "Q1_D", "+3V3_MCU", "3V3_MCU_LDO",
              "-3V3_RAW", "INV_CP", "INV_CN"}


def build():
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(4)
    ds.m_TrackMinWidth = mm(0.127)
    ds.m_MinClearance = mm(0.127)
    ds.m_ViasMinSize = mm(0.45)
    ds.m_MinThroughDrill = mm(0.2)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleToHoleMin = mm(0.25)
    ds.SetBoardThickness(mm(1.6))
    for lid, name in ((pcbnew.In1_Cu, "In1.GND"), (pcbnew.In2_Cu, "In2.PWR")):
        b.SetLayerName(lid, name)
    b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED)

    # net classes
    ns = ds.m_NetSettings
    dflt = ns.m_DefaultNetClass
    dflt.SetTrackWidth(mm(0.15)); dflt.SetClearance(mm(0.13))
    dflt.SetViaDiameter(mm(0.5)); dflt.SetViaDrill(mm(0.25))
    pwr = pcbnew.NETCLASS("Power")
    pwr.SetTrackWidth(mm(0.4)); pwr.SetClearance(mm(0.13))
    pwr.SetViaDiameter(mm(0.7)); pwr.SetViaDrill(mm(0.35))
    ns.m_NetClasses["Power"] = pwr

    # nets
    nets = {}
    for n in sorted(D.all_nets()):
        ni = pcbnew.NETINFO_ITEM(b, n)
        b.Add(ni)
        nets[n] = ni
    for n in POWER_NETS:
        nets[n].SetNetClass(pwr)

    # footprints
    for p in D.PARTS:
        lib, name = p["fp"].split(":")
        fp = pcbnew.FootprintLoad(FPLIB + lib + ".pretty", name)
        assert fp is not None, p["fp"]
        fp.SetReference(p["ref"])
        fp.SetValue(p["value"])
        fp.SetFPIDAsString(p["fp"])
        fp.SetPath(pcbnew.KIID_PATH("/" + sym_uuid(p["ref"])))
        if p["lcsc"]:
            fld = pcbnew.PCB_FIELD(fp, fp.GetFieldCount(), "LCSC")
            fld.SetText(p["lcsc"]); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab)
            fp.AddField(fld)
        if not p["assemble"]:
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        x, y, rot, side = PL.P[p["ref"]]
        fp.SetPosition(V(x, y))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num in p["nets"] and p["nets"][num]:
                pad.SetNet(nets[p["nets"][num]])
            elif num == "" or num == "MP":
                pass
        # silkscreen reference: shown for ICs, connectors, LEDs, switch and test points;
        # passive references go to the fabrication layer (assembly drawing) to keep the silk readable
        r = fp.Reference()
        r.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); r.SetTextThickness(mm(0.12))
        if p["sym"] in ("R", "C", "MH"):
            r.SetLayer(pcbnew.F_Fab)
        b.Add(fp)

    # outline with 2 mm corner radius
    W, H, R = PL.BOARD_W, PL.BOARD_H, 2.0
    def seg(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(x1, y1)); s.SetEnd(V(x2, y2)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)
    def arc(cx, cy, sx, sy, ang):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(V(cx, cy)); s.SetStart(V(sx, sy)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)
    seg(R, 0, W - R, 0); seg(W, R, W, H - R); seg(W - R, H, R, H); seg(0, H - R, 0, R)
    arc(W - R, R, W - R, 0, 90); arc(W - R, H - R, W, H - R, 90)
    arc(R, H - R, R, H, 90); arc(R, R, 0, R, 90)

    def zone(net, layer, pts, prio=0, name=None):
        z = pcbnew.ZONE(b)
        z.SetLayer(layer)
        if net:
            z.SetNet(nets[net])
        ol = z.Outline(); ol.NewOutline()
        for (x, y) in pts:
            ol.Append(mm(OX + x), mm(OY + y))
        z.SetAssignedPriority(prio)
        z.SetLocalClearance(mm(0.25))
        z.SetMinThickness(mm(0.2))
        z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        if name:
            z.SetZoneName(name)
        b.Add(z)
        return z

    full = [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)]
    zone("GND", pcbnew.In1_Cu, full, 0, "GND plane")
    zone("GND", pcbnew.F_Cu, full, 0, "GND fill top")
    zone("GND", pcbnew.B_Cu, full, 0, "GND fill bottom")
    # In2 power pours
    zone("-2V5", pcbnew.In2_Cu, [(24, 3), (48, 3), (48, 33), (24, 33)], 2, "AVSS pour")
    # +3V3_MCU is routed as 0.4 mm tracks (a pour here was cut into islands by the I2C/SPI routes)
    zone("VBAT", pcbnew.In2_Cu, [(0.5, 39), (34, 39), (34, 79.5), (0.5, 79.5)], 2, "VBAT pour")
    zone("+3V3_D", pcbnew.In2_Cu, [(53, 0.5), (99.5, 0.5), (99.5, 20), (53, 20)], 2, "3V3 D pour")
    zone("GND", pcbnew.In2_Cu, full, 1, "GND fill In2")

    # antenna keep-out (devkit antenna overhangs the right edge)
    ko = pcbnew.ZONE(b)
    ko.SetIsRuleArea(True)
    ko.SetDoNotAllowCopperPour(True); ko.SetDoNotAllowTracks(True); ko.SetDoNotAllowVias(True)
    ko.SetLayerSet(pcbnew.LSET.AllCuMask())
    ol = ko.Outline(); ol.NewOutline()
    for (x, y) in [(96.2, 40.5), (100, 40.5), (100, 73), (96.2, 73)]:
        ol.Append(mm(OX + x), mm(OY + y))
    ko.SetZoneName("ESP32 antenna keep-out")
    b.Add(ko)

    # silkscreen notes
    def text(s, x, y, size=1.0, layer=pcbnew.F_SilkS, bold=False, rot=0):
        t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * (0.2 if bold else 0.15)))
        t.SetTextAngleDegrees(rot)
        if layer == pcbnew.B_SilkS:
            t.SetMirrored(True)
        b.Add(t)
    text("NEURYO EEG  rev A", 75.0, 26.0, 1.5, bold=True)
    text("8-ch ADS1299 | ESP32-S3", 75.0, 28.6, 1.0)
    text("ELECTRODES", 4.8, 33.2, 0.9, bold=True)
    text("BIAS", 9.0, 4.3, 0.8)
    text("8", 1.4, 7.5, 0.8); text("1", 1.4, 25.3, 0.8); text("SRB", 1.0, 28.0, 0.8); text("GND", 1.2, 30.4, 0.8)
    text("N  P", 4.8, 3.2, 0.8)
    text("PWR", 4.0, 70.6, 0.8, bold=True)
    text("USB-C: CHARGE ONLY", 13.0, 41.0, 0.8)
    text("BATT +", 7.0, 70.6, 0.8)
    text("PPG1", 47.0, 79.0, 0.8); text("PPG2", 61.0, 79.0, 0.8); text("IMU", 75.0, 79.0, 0.8)
    text("ESP32-S3-DevKitC-1  (antenna this end ->)", 66.0, 56.5, 1.0)
    text("USB end", 44.0, 59.0, 0.8)
    text("Battery only while electrodes are on a person.", 50.0, 76.0, 0.9, layer=pcbnew.B_SilkS)
    text("Never connect USB while worn. Research prototype, not a medical device.", 50.0, 74.0, 0.9, layer=pcbnew.B_SilkS)
    text("Derived from OpenBCI Cyton (CC BY-SA 4.0)", 50.0, 72.0, 0.9, layer=pcbnew.B_SilkS)
    text("J4 pins: odd = N (electrodes), even = P", 30.0, 10.0, 0.9, layer=pcbnew.B_SilkS)
    text("SRB2 = reference, BIAS = bias electrode", 30.0, 12.0, 0.9, layer=pcbnew.B_SilkS)
    return b


if __name__ == "__main__":
    b = build()
    path = os.path.join(OUT, "neuryo.kicad_pcb")
    b.Save(path)
    # sanity: socket pin positions
    for ref in ("J5", "J6", "J4"):
        fp = b.FindFootprintByReference(ref)
        pads = sorted(fp.Pads(), key=lambda p: int(p.GetNumber()))
        def pos(p): return (round(pcbnew.ToMM(p.GetPosition().x) - OX, 2), round(pcbnew.ToMM(p.GetPosition().y) - OY, 2))
        print(ref, "pad1", pos(pads[0]), "pad2", pos(pads[1]), "last", pos(pads[-1]))
    print("saved", path)
