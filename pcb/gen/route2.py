"""Fan-out-first routing flow.

1. Build the placed board and give every SMD ground pad its own via (nothing is routed yet,
   so every pad has room).
2. Export DSN from a copy without those ground stubs, adding them as keep-outs, so
   Freerouting routes the signals around them. GND itself is not routed (plane + fills).
3. Import the session into the board that keeps the ground stubs, then finalize.
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import gen_pcb as GP, route as RT, gnd_stitch as GS

PCB = RT.PCB
FAN = os.path.join(RT.K, "neuryo_fanout.kicad_pcb")
ToMM = pcbnew.ToMM
LAYERS = ["F.Cu", "In1.GND", "In2.PWR", "B.Cu"]


def um(v):
    return round(ToMM(v) * 1000, 1)


def main(timeout_s=1500):
    b = GP.build()
    RT.strip_fills(b)
    before = {t.m_Uuid.AsString() for t in b.GetTracks()}
    GS.stitch(b, grid=False)
    added = [t for t in b.GetTracks() if t.m_Uuid.AsString() not in before]
    print("fan-out items", len(added))
    b.Save(FAN)
    # DSN from a copy without the fan-out items
    c = pcbnew.LoadBoard(FAN)
    for t in list(c.GetTracks()):
        if t.GetNetname() == "GND":
            c.Remove(t)
    tmp = os.path.join(RT.K, "neuryo_dsn_src.kicad_pcb")
    c.Save(tmp)
    c = pcbnew.LoadBoard(tmp)
    assert pcbnew.ExportSpecctraDSN(c, RT.DSN)
    RT.patch_dsn()
    keep = []
    for t in added:
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            d = um(t.GetWidth()) + 2 * 130
            for L in LAYERS:
                keep.append(f'    (keepout "" (circle {L} {d} {um(p.x)} {-um(p.y)}))')
        else:
            s, e = t.GetStart(), t.GetEnd()
            w = um(t.GetWidth()) + 2 * 130
            keep.append(f'    (keepout "" (path F.Cu {w} {um(s.x)} {-um(s.y)} {um(e.x)} {-um(e.y)}))')
    s = open(RT.DSN).read()
    i = s.index("    (via ")
    s = s[:i] + "\n".join(keep) + "\n" + s[i:]
    open(RT.DSN, "w").write(s)
    if os.path.exists(RT.SES):
        os.remove(RT.SES)
    r = subprocess.run(["timeout", str(timeout_s), "java", "-jar", os.path.join(RT.TOOLS, "freerouting.jar"),
                        "-de", RT.DSN, "-do", RT.SES, "-mp", "40", "--gui.enabled=false"],
                       capture_output=True, text=True)
    print("router exit", r.returncode, "session", os.path.exists(RT.SES))
    assert os.path.exists(RT.SES)
    b = pcbnew.LoadBoard(FAN)
    assert pcbnew.ImportSpecctraSES(b, RT.SES)
    GS.join_bias(b)
    b.Save(PCB)
    print("routed board saved")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1500)
