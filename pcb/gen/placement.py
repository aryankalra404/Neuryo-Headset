"""Component placement for the Neuryo board (board-local mm, origin top-left, y down).

Board 100 x 80 mm. Zones:
  analog  : y 0..38   electrode header -> ESD -> RC filters -> ADS1299 -> analog supplies
  power   : x 0..35, y 38..80   USB-C, charger, battery, protection, switch, MCU LDO
  digital : x 36..100, y 38..80 ESP32-S3-DevKitC-1 on sockets, I2C pull-ups, sensor headers
"""
import design as D

BOARD_W, BOARD_H = 100.0, 80.0
P = {}  # ref -> (x, y, rot, side)


def at(ref, x, y, rot=0, side="F"):
    P[ref] = (x, y, rot, side)


def refs(pred):
    return [p["ref"] for p in D.PARTS if pred(p)]


def find(value=None, nets=None, sym=None, section=None):
    out = []
    for p in D.PARTS:
        if sym and p["sym"] != sym:
            continue
        if value and p["value"] != value:
            continue
        if section and p["section"] != section:
            continue
        if nets and sorted(n for n in p["nets"].values() if n) != sorted(nets):
            continue
        out.append(p["ref"])
    return out


def one(**kw):
    r = find(**kw)
    assert len(r) >= 1, kw
    return r


_used = set()
def take(**kw):
    for r in find(**kw):
        if r not in _used:
            _used.add(r)
            return r
    raise KeyError(kw)

# ---------------------------------------------------------------- analog: electrode header and inputs
at("J4", 3.5, 5.0, 0)                       # pin 1 top-left; rows go down 2.54 mm
at("D3", 10.0, 8.81); at("D4", 10.0, 13.89); at("D5", 10.0, 18.97); at("D6", 10.0, 24.05)
at("D7", 10.0, 29.6)

order = []
for ch in range(8, 0, -1):
    order += [f"IN{ch}N", f"IN{ch}P"]
order += ["SRB1", "SRB2"]
for i, ln in enumerate(order):
    y = 4.4 + i * 1.5
    at(take(value="2.2k", nets=[f"E_{ln}", f"{ln}_F"]), 14.4, y, 0)
    at(take(value="1nF C0G", nets=[f"{ln}_F", "GND"]), 19.0, y, 0)
at(take(value="2.2k", nets=["BIASOUT", "E_BIAS"]), 14.4, 1.9, 180)

# ---------------------------------------------------------------- ADS1299 and its local parts
AX, AY = 35.0, 17.5
at("U9", AX, AY, 0)
# bias feedback (pins 61-63, top-left)
at(take(value="1M", nets=["BIASINV", "BIASOUT"]), 25.4, 8.0, 0)
at(take(value="1nF C0G", nets=["BIASINV", "BIASOUT"]), 25.4, 9.6, 0)
# top row caps (pins 49-60)
top = [("1uF", ["+2V5", "GND"]), ("100nF", ["+2V5", "GND"]),
       ("1uF", ["-2V5", "GND"]), ("100nF", ["-2V5", "GND"]),
       ("1uF", ["VCAP3", "-2V5"]), ("100nF", ["VCAP3", "-2V5"]),
       ("1uF", ["+2V5", "GND"]), ("100nF", ["+2V5", "GND"]),
       ("1uF", ["-2V5", "GND"]), ("100nF", ["-2V5", "GND"]),
       ("1uF", ["+3V3_D", "GND"]), ("100nF", ["+3V3_D", "GND"])]
small = [t for t in top if t[0] == "100nF"]; big = [t for t in top if t[0] != "100nF"]
for i, (v, n) in enumerate(small):          # 100 nF row nearest the pins
    at(take(value=v, nets=n), 29.6 + i * 1.55, 9.2, 90)
for i, (v, n) in enumerate(big):
    at(take(value=v, nets=n), 29.6 + i * 1.55, 6.2, 90)
at(take(value="10k", nets=["ADS_CLKSEL", "+3V3_D"]), 44.4, 8.6, 90)
# bottom row caps (pins 17-32)
bot = [("1uF", ["+2V5", "GND"]), ("100nF", ["+2V5", "GND"]),
       ("1uF", ["-2V5", "GND"]), ("100nF", ["-2V5", "GND"]),
       ("100nF", ["VREFP", "-2V5"]), ("1uF", ["VCAP4", "-2V5"]), ("1uF", ["VCAP2", "-2V5"])]
for i, (v, n) in enumerate(bot):
    at(take(value=v, nets=n), 30.0 + i * 1.55, 25.8, 90)
at(take(value="10uF", nets=["VREFP", "-2V5"]), 32.0, 29.4, 90)
at(take(value="100uF", nets=["VCAP1", "-2V5"]), 37.2, 29.8, 90)
# right side: DVDD decoupling and static pull resistors (pins 33-48)
at(take(value="1uF", nets=["+3V3_D", "GND"]), 43.4, 11.4, 0)
at(take(value="100nF", nets=["+3V3_D", "GND"]), 43.4, 13.0, 0)
pulls = [("10k", ["ADS_RESET", "+3V3_D"]), ("10k", ["ADS_PWDN", "+3V3_D"]), ("10k", ["ADS_CS", "+3V3_D"]),
         ("10k", ["ADS_START", "GND"]), ("10k", ["ADS_GPIO1", "GND"]), ("10k", ["ADS_GPIO2", "GND"]),
         ("10k", ["ADS_GPIO3", "GND"]), ("10k", ["ADS_GPIO4", "GND"])]
for i, (v, n) in enumerate(pulls):
    at(take(value=v, nets=n), 45.4, 15.0 + i * 1.5, 0)
series = [["M_SCLK", "ADS_SCLK"], ["M_DIN", "ADS_DIN"], ["M_DOUT", "ADS_DOUT"], ["M_CS", "ADS_CS"],
          ["M_START", "ADS_START"], ["M_RESET", "ADS_RESET"], ["M_PWDN", "ADS_PWDN"]]
for i, n in enumerate(series):
    at(take(value="100", nets=n), 50.4, 24.0 + i * 1.5, 0)

# ---------------------------------------------------------------- analog supplies
at("U5", 82.0, 6.0, 0)                                           # +3V3_D LDO
at(take(value="1uF", nets=["VBAT", "GND"]), 78.6, 6.0, 90)
at(take(value="10uF", nets=["+3V3_D", "GND"]), 85.6, 6.0, 90)
at("U6", 66.0, 6.0, 0)                                           # LM2664
at(take(value="1uF", nets=["+3V3_D", "GND"]), 70.0, 6.0, 90)
at(take(value="10uF", nets=["INV_CP", "INV_CN"]), 66.0, 2.6, 0)
at(take(value="10uF", nets=["-3V3_RAW", "GND"]), 62.0, 6.0, 90)
at("U7", 62.0, 13.0, 0)                                          # TPS72325 -2.5 V
at(take(value="2.2uF", nets=["-3V3_RAW", "GND"]), 58.4, 11.0, 90)
at(take(value="10nF", nets=["NR_NEG", "GND"]), 65.8, 15.2, 90)
at(take(value="2.2uF", nets=["-2V5", "GND"]), 58.4, 15.0, 90)
at(take(value="10uF", nets=["-2V5", "GND"]), 56.8, 15.0, 90)
at("U8", 74.0, 13.0, 0)                                          # TLV70025 +2.5 V
at(take(value="2.2uF", nets=["+3V3_D", "GND"]), 70.4, 13.0, 90)
at(take(value="2.2uF", nets=["+2V5", "GND"]), 77.6, 13.0, 90)
at(take(value="10uF", nets=["+2V5", "GND"]), 79.2, 13.0, 90)

# ---------------------------------------------------------------- power region (left bottom)
at("J1", 4.4, 47.0, 270)                                         # USB-C, opening to the left edge
at(take(value="5.1k", nets=["CC1", "GND"]), 12.2, 43.2, 0)
at(take(value="5.1k", nets=["CC2", "GND"]), 12.2, 50.8, 0)
at(take(value="10uF", nets=["VBUS", "GND"]), 11.0, 47.0, 90)
at("U1", 18.0, 47.0, 0)
at(take(value="2k", nets=["PROG", "GND"]), 14.4, 52.6, 0)
at(take(value="10uF", nets=["VBAT", "GND"]), 23.4, 47.0, 90)
at("D1", 7.0, 54.4, 180); at(take(value="1k", nets=["VBUS", "LED_CHRG"]), 11.4, 54.4, 0)
at("D2", 7.0, 57.0, 180); at(take(value="1k", nets=["VBUS", "LED_STDBY"]), 11.4, 57.0, 0)
at("SW1", 4.0, 64.0, 270)
at(take(value="100k", nets=["EN_SYS", "GND"]), 9.8, 64.0, 90)
at("J2", 7.0, 75.0, 0)                                           # battery, cable exits bottom edge
at("U2", 16.0, 70.0, 0)
at(take(value="100", nets=["VBAT", "DW_VCC"]), 16.0, 66.4, 0)
at(take(value="100nF", nets=["DW_VCC", "BAT_N"]), 19.4, 66.4, 90)
at(take(value="1k", nets=["DW_CS", "GND"]), 16.0, 73.6, 0)
at("Q1", 21.6, 70.0, 0)
at("U3", 26.0, 56.0, 0)                                          # MCU 3.3 V LDO
at(take(value="10uF", nets=["VBAT", "GND"]), 22.4, 56.0, 90)
at(take(value="10uF", nets=["3V3_MCU_LDO", "GND"]), 29.4, 56.0, 90)
at("U4", 26.0, 61.0, 0)                                          # reverse-blocking switch
at(take(value="10uF", nets=["+3V3_MCU", "GND"]), 29.4, 61.0, 90)
at(take(value="100nF", nets=["+3V3_MCU", "GND"]), 31.0, 61.0, 90)
at(take(value="1M", nets=["VBAT", "VBAT_SENSE"]), 27.0, 66.6, 0)
at(take(value="1M", nets=["VBAT_SENSE", "GND"]), 27.0, 68.2, 0)
at(take(value="100nF", nets=["VBAT_SENSE", "GND"]), 30.6, 67.4, 90)

# ---------------------------------------------------------------- digital: devkit sockets, I2C, sensors
J5_Y, J6_Y, PIN1_X = 44.0, 69.4, 95.0
at("J5", PIN1_X, J5_Y, 270)                 # pins run toward -x (checked in gen_pcb)
at("J6", PIN1_X, J6_Y, 270)
for i, n in enumerate([["I2C0_SDA", "+3V3_MCU"], ["I2C0_SCL", "+3V3_MCU"], ["I2C1_SDA", "+3V3_MCU"], ["I2C1_SCL", "+3V3_MCU"]]):
    at(take(value="4.7k", nets=n), 70.0 + i * 3.0, 50.0, 90)
at(take(value="100nF", nets=["+3V3_MCU", "GND"]), 90.0, 49.0, 90)
at("J7", 42.0, 76.6, 90); at("J8", 56.0, 76.6, 90); at("J9", 70.0, 76.6, 90)

# ---------------------------------------------------------------- test points and holes
tps = {p["ref"]: p["value"] for p in D.PARTS if p["sym"] == "TP"}
tp_xy = {"VBAT": (24.0, 77.0), "+3V3_MCU": (33.0, 52.0), "+3V3_D": (88.5, 6.0), "+2V5": (82.0, 16.0),
         "-2V5": (54.0, 18.0), "ADS_DRDY": (47.0, 33.5), "ADS_CLK": (44.0, 33.5)}
gnd_xy = [(31.0, 77.0), (91.0, 16.0)]
for r, v in tps.items():
    if v == "GND":
        at(r, *gnd_xy.pop(0))
    else:
        at(r, *tp_xy[v])
at("H1", 96.4, 3.6); at("H2", 3.6, 36.2); at("H3", 96.4, 76.4); at("H4", 36.4, 76.4)

missing = [p["ref"] for p in D.PARTS if p["ref"] not in P]
if missing:
    raise SystemExit(f"unplaced parts: {missing}")
