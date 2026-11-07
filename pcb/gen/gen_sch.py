"""Generate the KiCad 7 symbol library and schematic from design.py."""
import uuid, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import design as D

OUT = os.path.join(os.path.dirname(__file__), "..", "kicad")
os.makedirs(OUT, exist_ok=True)
G = 1.27  # grid
ROOT_UUID = "5b0a1c2e-7d3f-4e8a-9b21-0e6f2a4c8d10"

def U():
    return str(uuid.uuid4())

def sym_uuid(ref):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "neuryo/" + ref))

def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def snap(v):
    return round(v / G) * G

FONT = "(effects (font (size 1.27 1.27)))"
FONT_HIDE = "(effects (font (size 1.27 1.27)) hide)"

# ------------------------------------------------------------------ symbol geometry
def sym_geometry(name):
    """Return (graphics sexpr list, pins list [(num,name,type,x,y,angle,length)], props)"""
    s = D.SYMBOLS[name]
    gfx, pins = [], []
    if "pins" in s:
        L = [p for p in s["pins"] if p[3] == "L"]
        R = [p for p in s["pins"] if p[3] == "R"]
        n = max(len(L), len(R))
        W = s["width"]
        top = (n - 1) * 2.54 / 2
        H2 = top + 2.54
        gfx.append(f"(rectangle (start {f(-W/2)} {f(H2)}) (end {f(W/2)} {f(-H2)}) (stroke (width 0.254) (type default)) (fill (type background)))")
        for i, p in enumerate(L):
            pins.append((p[0], p[1], p[2], -W/2 - 2.54, top - i*2.54, 0, 2.54))
        for i, p in enumerate(R):
            pins.append((p[0], p[1], p[2], W/2 + 2.54, top - i*2.54, 180, 2.54))
        return gfx, pins, dict(ref_y=H2 + 1.27, val_y=-H2 - 1.27, names=True)
    if "conn" in s or "conn2" in s:
        two = "conn2" in s
        n = s.get("conn2", s.get("conn"))
        top = (n - 1) * 2.54 / 2
        H2 = top + 1.27 + 1.27
        if two:
            gfx.append(f"(rectangle (start -2.54 {f(H2)}) (end 2.54 {f(-H2)}) (stroke (width 0.254) (type default)) (fill (type background)))")
            for i in range(n):
                pins.append((str(2*i+1), "", "passive", -5.08, top - i*2.54, 0, 2.54))
                pins.append((str(2*i+2), "", "passive", 5.08, top - i*2.54, 180, 2.54))
        else:
            gfx.append(f"(rectangle (start -1.27 {f(H2)}) (end 1.27 {f(-H2)}) (stroke (width 0.254) (type default)) (fill (type background)))")
            for i in range(n):
                pins.append((str(i+1), "", "passive", -3.81, top - i*2.54, 0, 2.54))
        return gfx, pins, dict(ref_y=H2 + 1.27, val_y=-H2 - 1.27, names=False)
    if s.get("flag"):
        gfx.append("(polyline (pts (xy 0 0) (xy 0 1.27) (xy -1.016 1.905) (xy 0 2.54) (xy 1.016 1.905) (xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none)))")
        pins.append(("1", "pwr", "power_out", 0, 0, 90, 0))
        return gfx, pins, dict(ref_y=3.81, val_y=3.81, names=False, power=True)
    k = s["two"]
    if k in ("R", "C", "C_POL"):
        if k == "R":
            gfx.append("(rectangle (start -2.032 0.762) (end 2.032 -0.762) (stroke (width 0.254) (type default)) (fill (type none)))")
        else:
            gfx.append("(polyline (pts (xy -0.508 1.524) (xy -0.508 -1.524)) (stroke (width 0.3048) (type default)) (fill (type none)))")
            gfx.append("(polyline (pts (xy 0.508 1.524) (xy 0.508 -1.524)) (stroke (width 0.3048) (type default)) (fill (type none)))")
        pins += [("1", "~", "passive", -3.81, 0, 0, 1.778 if k == "R" else 3.302),
                 ("2", "~", "passive", 3.81, 0, 180, 1.778 if k == "R" else 3.302)]
        return gfx, pins, dict(ref_y=2.54, val_y=-2.54, names=False)
    if k == "LED":
        gfx.append("(polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))")
        gfx.append("(polyline (pts (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))")
        pins += [("1", "K", "passive", -3.81, 0, 0, 2.54), ("2", "A", "passive", 3.81, 0, 180, 2.54)]
        return gfx, pins, dict(ref_y=2.54, val_y=-2.54, names=False)
    if k in ("TP", "MH"):
        gfx.append("(circle (center 0 1.27) (radius 0.762) (stroke (width 0.254) (type default)) (fill (type none)))")
        pins.append(("1", "1", "passive", 0, -1.27, 90, 1.778 if k == "TP" else 1.778))
        return gfx, pins, dict(ref_y=3.302, val_y=3.302, names=False)
    raise ValueError(name)


def sym_def(name, prefix=True):
    gfx, pins, pr = sym_geometry(name)
    full = f"neuryo:{name}" if prefix else name
    desc = D.SYMBOLS[name].get("desc", name)
    power = "(power) " if pr.get("power") else ""
    ref = "#FLG" if pr.get("power") else {"R": "R", "C": "C", "C_POL": "C", "LED": "D", "TP": "TP", "MH": "H"}.get(D.SYMBOLS[name].get("two"), "U")
    pn = "" if pr["names"] else "(pin_names hide) "
    bom = "(in_bom no) (on_board no)" if pr.get("power") else "(in_bom yes) (on_board yes)"
    out = [f'(symbol "{full}" {power}{pn}{bom}',
           f'  (property "Reference" "{ref}" (at 0 {f(pr["ref_y"])} 0) {FONT})',
           f'  (property "Value" "{name}" (at 0 {f(pr["val_y"])} 0) {FONT})',
           f'  (property "Footprint" "" (at 0 0 0) {FONT_HIDE})',
           f'  (property "Datasheet" "" (at 0 0 0) {FONT_HIDE})',
           f'  (property "ki_description" "{desc}" (at 0 0 0) {FONT_HIDE})',
           f'  (symbol "{name}_0_1"'] + ["    " + g for g in gfx] + ["  )", f'  (symbol "{name}_1_1"']
    for num, pname, typ, x, y, ang, ln in pins:
        hide = " hide" if typ == "power_out" and pr.get("power") else ""
        out.append(f'    (pin {typ} line (at {f(x)} {f(y)} {ang}) (length {f(ln)}){hide} (name "{pname}" {FONT}) (number "{num}" {FONT}))')
    out += ["  )", ")"]
    return "\n".join(out)


def write_lib():
    with open(os.path.join(OUT, "neuryo.kicad_sym"), "w") as fh:
        fh.write('(kicad_symbol_lib (version 20220914) (generator neuryo_gen)\n')
        for name in D.SYMBOLS:
            fh.write(sym_def(name, prefix=False) + "\n")
        fh.write(")\n")

# ------------------------------------------------------------------ schematic placement
SECTIONS = [  # (name, x, y, w, h) on an A1 sheet (841 x 594 mm)
    ("Charger", 20, 25, 260, 120),
    ("Battery", 20, 155, 260, 95),
    ("Power", 20, 260, 260, 150),
    ("Analog supply", 20, 420, 260, 150),
    ("ADS1299", 290, 25, 270, 300),
    ("Electrode inputs", 290, 335, 270, 235),
    ("MCU", 570, 25, 255, 300),
    ("Sensors", 570, 335, 255, 110),
    ("Test", 570, 455, 255, 115),
]
TITLES = {
    "Charger": "1  USB-C charging (TP4056, 580 mA)",
    "Battery": "2  LiPo cell and protection (DW01A + FS8205A)",
    "Power": "3  Power switch and 3.3 V rails (MCU rail is reverse-blocked)",
    "Analog supply": "4  +2.5 V / -2.5 V analog supplies (OpenBCI Cyton circuit)",
    "ADS1299": "5  ADS1299 analog front end",
    "Electrode inputs": "6  Electrode inputs: ESD clamp, 2.2k series, 1 nF C0G to GND",
    "MCU": "7  ESP32-S3-DevKitC-1 sockets and SPI series resistors",
    "Sensors": "8  Sensor ports (I2C)",
    "Test": "9  Test points and mounting holes",
}

def label_len(net):
    return len(net) * 1.05 + 2.0

COLUMNS = [(12, 180, ["Charger", "Battery", "Power", "Analog supply"]),
           (200, 200, ["ADS1299", "Electrode inputs"]),
           (408, 172, ["MCU", "Sensors", "Test"])]
TOP, GAP = 14, 6


def flow(parts, sx, sy, sw):
    """Place parts left to right inside width sw; return placements and used height."""
    out = []
    x, y = sx + 6, sy + 12
    row_h = 0
    for p in parts:
        gfx, pins, pr = sym_geometry(p["sym"])
        xs = [pn[3] for pn in pins]; ys = [pn[4] for pn in pins]
        lmax = max([label_len(n or "") for n in p["nets"].values()] + [4])
        left = -min(xs + [-3]) + (lmax if any(pn[3] < 0 for pn in pins) else 2)
        right = max(xs + [3]) + (lmax if any(pn[3] > 0 for pn in pins) else 2)
        top = max(ys + [0]) + 5
        bot = -min(ys + [0]) + 5
        w = left + right + 3
        h = top + bot
        if x + w > sx + sw - 2 and x > sx + 6:
            x = sx + 6; y += row_h; row_h = 0
        out.append((p, snap(x + left), snap(y + top)))
        x += w; row_h = max(row_h, h)
    return out, (y + row_h) - sy + 2


def place_all():
    global SECTIONS
    placed, SECTIONS = [], []
    for cx, cw, names in COLUMNS:
        y = TOP
        for name in names:
            parts = [p for p in D.PARTS if p["section"] == name]
            pl, h = flow(parts, cx, y, cw)
            if name == "Test":
                h += 14          # room for the PWR_FLAG row
            placed += pl
            SECTIONS.append((name, cx, y, cw, h))
            y += h + GAP
    return placed


def gen_sch():
    placed = place_all()
    used = sorted({p["sym"] for p in D.PARTS} | {"PWR_FLAG"})
    lines = ['(kicad_sch (version 20230121) (generator eeschema)', f'  (uuid {ROOT_UUID})', '  (paper "A2")',
             '  (title_block (title "Neuryo EEG board") (date "2026-10-30") (rev "A") (company "Neuryo")',
             '    (comment 1 "8-ch ADS1299 EEG + ESP32-S3 devkit. Derived from OpenBCI Cyton (CC BY-SA 4.0)")',
             '    (comment 2 "Research prototype, not a medical device. Battery only while electrodes are on a person.")',
             '    (comment 3 "Generated from gen/design.py: edit the design file, then regenerate")',
             '  )', '  (lib_symbols']
    for s in used:
        lines.append("    " + sym_def(s).replace("\n", "\n    "))
    lines.append("  )")
    # section boxes and titles
    for name, sx, sy, sw, sh in SECTIONS:
        lines.append(f'  (rectangle (start {f(sx)} {f(sy)}) (end {f(sx+sw)} {f(sy+sh)}) (stroke (width 0.3) (type dash)) (fill (type none)) (uuid {U()}))')
        lines.append(f'  (text "{TITLES[name]}" (at {f(sx+3)} {f(sy+6)} 0) (effects (font (size 3 3) bold) (justify left bottom)) (uuid {U()}))')
    notes = ["Safety: battery only while electrodes are on a person. USB-C is for charging with nobody connected.",
             "To flash firmware: PWR switch ON, nobody connected to the electrodes.",
             "Electrode convention (Cyton): electrodes on N inputs, reference on SRB2, BIAS to the bias electrode."]
    ny = max(sy + sh for _, _, sy, _, sh in SECTIONS) + 6
    for i, t in enumerate(notes):
        lines.append(f'  (text "{t}" (at 12 {f(ny + i*4.5)} 0) (effects (font (size 2.2 2.2)) (justify left bottom)) (uuid {U()}))')
    pinmap = {}
    for p, cx, cy in placed:
        gfx, pins, pr = sym_geometry(p["sym"])
        lines.append(f'  (symbol (lib_id "neuryo:{p["sym"]}") (at {f(cx)} {f(cy)} 0) (unit 1)')
        lines.append(f'    (in_bom {"yes" if p["assemble"] or p["sym"].startswith("CONN") else "no"}) (on_board yes) (dnp {"yes" if p["dnp"] else "no"}) (uuid {sym_uuid(p["ref"])})')
        lines.append(f'    (property "Reference" "{p["ref"]}" (at {f(cx)} {f(cy - pr["ref_y"])} 0) (effects (font (size 1.27 1.27))))')
        val = p["value"].replace('"', "'")
        lines.append(f'    (property "Value" "{val}" (at {f(cx)} {f(cy - pr["val_y"])} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Footprint" "{p["fp"]}" (at {f(cx)} {f(cy)} 0) {FONT_HIDE})')
        lines.append(f'    (property "Datasheet" "" (at {f(cx)} {f(cy)} 0) {FONT_HIDE})')
        lines.append(f'    (property "LCSC" "{p["lcsc"]}" (at {f(cx)} {f(cy)} 0) {FONT_HIDE})')
        lines.append(f'    (property "MPN" "{p["mpn"]}" (at {f(cx)} {f(cy)} 0) {FONT_HIDE})')
        for num, *_ in pins:
            lines.append(f'    (pin "{num}" (uuid {U()}))')
        lines.append(f'    (instances (project "neuryo" (path "/{ROOT_UUID}" (reference "{p["ref"]}") (unit 1))))')
        lines.append("  )")
        for num, pname, typ, x, y, ang, ln in pins:
            ax, ay = cx + x, cy - y
            net = p["nets"].get(num, None)
            if net is None:
                if typ == "no_connect":
                    continue
                lines.append(f'  (no_connect (at {f(ax)} {f(ay)}) (uuid {U()}))')
                continue
            pinmap.setdefault(net, []).append((p["ref"], num))
            # label direction: away from the body
            if ang == 0:      # pin on left side, connection point at left
                la, just = 180, "right"
            elif ang == 180:
                la, just = 0, "left"
            elif ang == 90:   # pointing up into body from below
                la, just = 270, "right"
            else:
                la, just = 90, "left"
            lines.append(f'  (label "{net}" (at {f(ax)} {f(ay)} {la}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {U()}))')
    # power flags
    _, tx, ty, tw, th = [t for t in SECTIONS if t[0] == "Test"][0]
    fx, fy = tx + 12, ty + th - 6
    for i, net in enumerate(D.FLAGS):
        x, y = snap(fx + i * 22), snap(fy)
        lines.append(f'  (symbol (lib_id "neuryo:PWR_FLAG") (at {f(x)} {f(y)} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid {U()})')
        lines.append(f'    (property "Reference" "#FLG0{i+1}" (at {f(x)} {f(y-5)} 0) {FONT_HIDE})')
        lines.append(f'    (property "Value" "PWR_FLAG" (at {f(x)} {f(y-4)} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Footprint" "" (at {f(x)} {f(y)} 0) {FONT_HIDE})')
        lines.append(f'    (property "Datasheet" "" (at {f(x)} {f(y)} 0) {FONT_HIDE})')
        lines.append(f'    (pin "1" (uuid {U()}))')
        lines.append(f'    (instances (project "neuryo" (path "/{ROOT_UUID}" (reference "#FLG0{i+1}") (unit 1))))')
        lines.append("  )")
        lines.append(f'  (label "{net}" (at {f(x)} {f(y)} 270) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify right bottom)) (uuid {U()}))')
    lines.append('  (sheet_instances (path "/" (page "1")))')
    lines.append(")")
    with open(os.path.join(OUT, "neuryo.kicad_sch"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return placed


if __name__ == "__main__":
    write_lib()
    placed = gen_sch()
    print("placed", len(placed), "symbols")
