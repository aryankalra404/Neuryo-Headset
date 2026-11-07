"""Export JLCPCB fabrication and assembly files, PDFs and renders."""
import csv, os, subprocess, sys, zipfile, collections
sys.path.insert(0, os.path.dirname(__file__))
import design as D

ROOT = os.path.join(os.path.dirname(__file__), "..")
K = os.path.join(ROOT, "kicad")
PCB = os.path.join(K, "neuryo.kicad_pcb")
SCH = os.path.join(K, "neuryo.kicad_sch")
FAB = os.path.join(ROOT, "fab")
GER = os.path.join(FAB, "gerbers")
os.makedirs(GER, exist_ok=True)

def run(*a):
    r = subprocess.run(["kicad-cli", *a], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("kicad-cli failed: " + " ".join(a))

# gerbers and drill (JLCPCB settings)
for f in os.listdir(GER):
    os.remove(os.path.join(GER, f))
run("pcb", "export", "gerbers", "--output", GER + "/",
    "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
    "--subtract-soldermask", "--no-x2", "--use-drill-file-origin", PCB)
run("pcb", "export", "drill", "--output", GER + "/", "--format", "excellon", "--drill-origin", "absolute",
    "--excellon-units", "mm", "--excellon-zeros-format", "decimal", "--generate-map", "--map-format", "gerberx2",
    "--excellon-separate-th", PCB)
zp = os.path.join(FAB, "neuryo-revA-gerbers.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(GER)):
        z.write(os.path.join(GER, f), f)

# placement (CPL) for JLCPCB
pos = os.path.join(FAB, "pos-kicad.csv")
run("pcb", "export", "pos", "--output", pos, "--format", "csv", "--units", "mm", "--side", "front",
    "--exclude-dnp", PCB)
assembled = {p["ref"] for p in D.PARTS if p["assemble"] and not p["dnp"]}
with open(pos) as fh, open(os.path.join(FAB, "neuryo-revA-CPL.csv"), "w", newline="") as out:
    w = csv.writer(out)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    n = 0
    for row in csv.DictReader(fh):
        if row["Ref"] not in assembled:
            continue
        w.writerow([row["Ref"], row["PosX"] + "mm", row["PosY"] + "mm", "Top", row["Rot"]])
        n += 1
print("CPL rows", n)

# BOM for JLCPCB (assembled parts) and a full BOM (everything, incl. hand-soldered)
groups = collections.OrderedDict()
for p in D.PARTS:
    if not p["assemble"] or p["dnp"]:
        continue
    key = (p["mpn"] or p["value"], p["fp"], p["lcsc"])
    groups.setdefault(key, []).append(p["ref"])
def natkey(r):
    import re
    m = re.match(r"([A-Z]+)(\d+)", r)
    return (m.group(1), int(m.group(2)))
with open(os.path.join(FAB, "neuryo-revA-BOM-JLCPCB.csv"), "w", newline="") as out:
    w = csv.writer(out)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fp, lcsc), refs in sorted(groups.items(), key=lambda kv: natkey(sorted(kv[1], key=natkey)[0])):
        w.writerow([val, ",".join(sorted(refs, key=natkey)), fp.split(":")[1], lcsc])
hand = [p for p in D.PARTS if not p["assemble"] and p["sym"] not in ("TP", "MH")]
with open(os.path.join(FAB, "neuryo-revA-BOM-hand-soldered.csv"), "w", newline="") as out:
    w = csv.writer(out)
    w.writerow(["Designator", "Part", "Footprint", "Note"])
    notes = {"J4": "2x11 male header 2.54 mm (electrodes)", "J5": "1x22 female socket 2.54 mm (DevKitC-1)",
             "J6": "1x22 female socket 2.54 mm (DevKitC-1)", "J7": "1x5 male header 2.54 mm",
             "J8": "1x5 male header 2.54 mm", "J9": "1x5 male header 2.54 mm"}
    for p in hand:
        w.writerow([p["ref"], p["value"], p["fp"].split(":")[1], notes.get(p["ref"], "")])
print("BOM lines", len(groups))

# PDFs and renders
run("sch", "export", "pdf", "--output", os.path.join(FAB, "neuryo-revA-schematic.pdf"), SCH)
for name, layers in (("top", "F.Cu,F.Silkscreen,Edge.Cuts"), ("in1-gnd", "In1.Cu,Edge.Cuts"),
                     ("in2-power", "In2.Cu,Edge.Cuts"), ("bottom", "B.Cu,B.Silkscreen,Edge.Cuts"),
                     ("assembly-top", "F.Fab,F.Silkscreen,Edge.Cuts")):
    run("pcb", "export", "pdf", "--output", os.path.join(FAB, f"layer-{name}.pdf"), "--layers", layers,
        "--include-border-title", PCB)
run("pcb", "export", "step", "--output", os.path.join(FAB, "neuryo-revA.step"), "--subst-models", "--force", PCB)
print("exported to", FAB)
