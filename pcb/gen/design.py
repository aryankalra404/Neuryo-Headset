"""Neuryo EEG board rev A: single source of truth for parts, pins and nets.

Every pin number below was checked against the manufacturer datasheet
(see docs/DESIGN.md and ref/ds/). Generators for the schematic, PCB and
fab files all read from this file.
"""

# ---------------------------------------------------------------- symbols
# pin tuple: (number, name, electrical type, side)  side: L or R (box symbols)
# electrical types: input output bidirectional passive power_in power_out no_connect
SYMBOLS = {
    "ADS1299": {
        "width": 30.48, "desc": "TI ADS1299 8-ch 24-bit biopotential AFE",
        "pins": [
            # left: analog inputs and SRB
            ("16", "IN1P", "input", "L"), ("15", "IN1N", "input", "L"),
            ("14", "IN2P", "input", "L"), ("13", "IN2N", "input", "L"),
            ("12", "IN3P", "input", "L"), ("11", "IN3N", "input", "L"),
            ("10", "IN4P", "input", "L"), ("9", "IN4N", "input", "L"),
            ("8", "IN5P", "input", "L"), ("7", "IN5N", "input", "L"),
            ("6", "IN6P", "input", "L"), ("5", "IN6N", "input", "L"),
            ("4", "IN7P", "input", "L"), ("3", "IN7N", "input", "L"),
            ("2", "IN8P", "input", "L"), ("1", "IN8N", "input", "L"),
            ("17", "SRB1", "passive", "L"), ("18", "SRB2", "passive", "L"),
            ("60", "BIASREF", "input", "L"), ("61", "BIASINV", "input", "L"),
            ("62", "BIASIN", "input", "L"), ("63", "BIASOUT", "output", "L"),
            ("24", "VREFP", "passive", "L"), ("25", "VREFN", "passive", "L"),
            ("28", "VCAP1", "passive", "L"), ("30", "VCAP2", "passive", "L"),
            ("55", "VCAP3", "passive", "L"), ("26", "VCAP4", "passive", "L"),
            ("27", "NC", "no_connect", "L"), ("29", "NC", "no_connect", "L"),
            ("64", "RESERVED", "no_connect", "L"),
            # right: supplies and digital
            ("19", "AVDD", "power_in", "R"), ("21", "AVDD", "power_in", "R"),
            ("22", "AVDD", "power_in", "R"), ("56", "AVDD", "power_in", "R"),
            ("59", "AVDD", "power_in", "R"), ("54", "AVDD1", "power_in", "R"),
            ("20", "AVSS", "power_in", "R"), ("23", "AVSS", "power_in", "R"),
            ("32", "AVSS", "power_in", "R"), ("57", "AVSS", "power_in", "R"),
            ("58", "AVSS", "power_in", "R"), ("53", "AVSS1", "power_in", "R"),
            ("48", "DVDD", "power_in", "R"), ("50", "DVDD", "power_in", "R"),
            ("33", "DGND", "power_in", "R"), ("49", "DGND", "power_in", "R"),
            ("51", "DGND", "power_in", "R"), ("31", "RESV1", "input", "R"),
            ("40", "SCLK", "input", "R"), ("34", "DIN", "input", "R"),
            ("43", "DOUT", "output", "R"), ("39", "~{CS}", "input", "R"),
            ("47", "~{DRDY}", "output", "R"), ("38", "START", "input", "R"),
            ("36", "~{RESET}", "input", "R"), ("35", "~{PWDN}", "input", "R"),
            ("52", "CLKSEL", "input", "R"), ("37", "CLK", "bidirectional", "R"),
            ("41", "DAISY_IN", "input", "R"), ("42", "GPIO1", "bidirectional", "R"),
            ("44", "GPIO2", "bidirectional", "R"), ("45", "GPIO3", "bidirectional", "R"),
            ("46", "GPIO4", "bidirectional", "R"),
        ]},
    "TLV75533": {"width": 12.7, "desc": "TI TLV75533PDBV 3.3 V 500 mA LDO", "pins": [
        ("1", "IN", "power_in", "L"), ("3", "EN", "input", "L"), ("2", "GND", "power_in", "L"),
        ("5", "OUT", "power_out", "R"), ("4", "NC", "no_connect", "R")]},
    "TLV70025": {"width": 12.7, "desc": "TI TLV70025DDC 2.5 V 200 mA LDO", "pins": [
        ("1", "IN", "power_in", "L"), ("3", "EN", "input", "L"), ("2", "GND", "power_in", "L"),
        ("5", "OUT", "power_out", "R"), ("4", "NC", "no_connect", "R")]},
    "TPS72325": {"width": 12.7, "desc": "TI TPS72325DBV -2.5 V 200 mA negative LDO", "pins": [
        ("2", "IN", "power_in", "L"), ("3", "EN", "input", "L"), ("1", "GND", "power_in", "L"),
        ("5", "OUT", "power_out", "R"), ("4", "NR", "passive", "R")]},
    "LM2664": {"width": 12.7, "desc": "TI LM2664 switched-capacitor voltage inverter", "pins": [
        ("5", "V+", "power_in", "L"), ("4", "SD", "input", "L"), ("1", "GND", "power_in", "L"),
        ("6", "CAP+", "passive", "R"), ("3", "CAP-", "passive", "R"), ("2", "OUT", "power_out", "R")]},
    "SIP32431": {"width": 12.7, "desc": "Vishay SiP32431DR3 1 A load switch, reverse blocking", "pins": [
        ("4", "IN", "power_in", "L"), ("3", "ON/OFF", "input", "L"), ("2", "GND", "power_in", "L"),
        ("5", "GND", "power_in", "L"), ("1", "OUT", "power_out", "R"), ("6", "NC", "no_connect", "R")]},
    "TP4056": {"width": 15.24, "desc": "TP4056 1 A Li-ion linear charger", "pins": [
        ("4", "VCC", "power_in", "L"), ("8", "CE", "input", "L"), ("1", "TEMP", "input", "L"),
        ("2", "PROG", "passive", "L"), ("3", "GND", "power_in", "L"), ("9", "EP", "power_in", "L"),
        ("5", "BAT", "power_out", "R"), ("7", "~{CHRG}", "open_collector", "R"),
        ("6", "~{STDBY}", "open_collector", "R")]},
    "DW01A": {"width": 12.7, "desc": "DW01A single-cell Li-ion protection", "pins": [
        ("5", "VCC", "power_in", "L"), ("6", "GND", "power_in", "L"), ("2", "CS", "input", "L"),
        ("1", "OD", "output", "R"), ("3", "OC", "output", "R"), ("4", "TD", "no_connect", "R")]},
    "FS8205A": {"width": 12.7, "desc": "FS8205A dual N-MOSFET, common drain", "pins": [
        ("1", "S1", "passive", "L"), ("6", "G1", "input", "L"),
        ("3", "S2", "passive", "R"), ("4", "G2", "input", "R"),
        ("2", "D", "passive", "R"), ("5", "D", "passive", "R")]},
    "TPD4E1B06": {"width": 10.16, "desc": "TI TPD4E1B06 4-ch ESD protection", "pins": [
        ("1", "IO1", "passive", "L"), ("2", "IO2", "passive", "L"),
        ("4", "IO3", "passive", "L"), ("5", "IO4", "passive", "L"),
        ("3", "GND", "passive", "R"), ("6", "NC", "no_connect", "R")]},
    "USB_C_PWR": {"width": 12.7, "desc": "USB-C receptacle 16P (HRO TYPE-C-31-M-12), power only", "pins": [
        ("A4", "VBUS", "passive", "L"), ("A9", "VBUS", "passive", "L"),
        ("B4", "VBUS", "passive", "L"), ("B9", "VBUS", "passive", "L"),
        ("A5", "CC1", "passive", "L"), ("B5", "CC2", "passive", "L"),
        ("A6", "DP1", "passive", "R"), ("B6", "DP2", "passive", "R"),
        ("A7", "DN1", "passive", "R"), ("B7", "DN2", "passive", "R"),
        ("A8", "SBU1", "passive", "R"), ("B8", "SBU2", "passive", "R"),
        ("A1", "GND", "passive", "L"), ("A12", "GND", "passive", "L"),
        ("B1", "GND", "passive", "L"), ("B12", "GND", "passive", "L"),
        ("S1", "SHIELD", "passive", "R")]},
    "SW_SPDT": {"width": 7.62, "desc": "Slide switch SPDT", "pins": [
        ("1", "A", "passive", "L"), ("3", "B", "passive", "L"), ("2", "C", "passive", "R")]},
    "PWR_FLAG": {"flag": True},
    # two-pin and connector symbols are generated (see gen_symbols.py)
}

def conn_symbol(n):  # single-row connector
    return {"conn": n}

def conn2_symbol(n):  # dual-row connector, odd/even
    return {"conn2": n}

for n in (2, 5, 22):
    SYMBOLS[f"CONN_1x{n:02d}"] = conn_symbol(n)
SYMBOLS["CONN_2x11"] = conn2_symbol(11)
for k in ("R", "C", "C_POL", "LED", "TP", "MH"):
    SYMBOLS[k] = {"two": k}

# ---------------------------------------------------------------- footprints
FP = {
    "R0603": "Resistor_SMD:R_0603_1608Metric",
    "C0603": "Capacitor_SMD:C_0603_1608Metric",
    "C0805": "Capacitor_SMD:C_0805_2012Metric",
    "C1206": "Capacitor_SMD:C_1206_3216Metric",
    "LED0805": "LED_SMD:LED_0805_2012Metric",
    "SOT23-5": "Package_TO_SOT_SMD:SOT-23-5",
    "SOT23-6": "Package_TO_SOT_SMD:SOT-23-6",
    "SC70-6": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
    "TQFP64": "Package_QFP:TQFP-64_10x10mm_P0.5mm",
    "ESOP8": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm",
    "USBC": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
    "JSTPH2": "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
    "PCM12": "Button_Switch_SMD:SW_SPDT_PCM12",
    "SOCK1x22": "Connector_PinSocket_2.54mm:PinSocket_1x22_P2.54mm_Vertical",
    "HDR2x11": "Connector_PinHeader_2.54mm:PinHeader_2x11_P2.54mm_Vertical",
    "HDR1x05": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
    "TP": "TestPoint:TestPoint_Pad_D1.5mm",
    "MH": "MountingHole:MountingHole_3.2mm_M3_Pad_Via",
}

# value -> (LCSC, MPN) for passives
LCSC_R = {"0": "C21189", "100": "C22775", "1k": "C21190", "2k": "C22975", "2.2k": "C4190",
          "4.7k": "C23162", "5.1k": "C23186", "10k": "C25804", "100k": "C25803", "1M": "C22935"}
LCSC_C = {("100nF", "0603"): "C14663", ("1uF", "0603"): "C15849", ("2.2uF", "0603"): "C23630",
          ("4.7uF", "0603"): "C19666", ("10uF", "0603"): "C19702", ("10uF", "0805"): "C15850",
          ("100uF", "1206"): "C15008", ("10nF", "0603"): "C57112", ("1nF C0G", "0603"): "C163508"}

PARTS = []

def part(ref, sym, value, fp, nets, lcsc="", mpn="", section="", dnp=False, assemble=True):
    PARTS.append(dict(ref=ref, sym=sym, value=value, fp=FP.get(fp, fp), nets=dict(nets),
                      lcsc=lcsc, mpn=mpn, section=section, dnp=dnp, assemble=assemble))

_rc = {"R": 0, "C": 0, "TP": 0}
def R(value, a, b, section, ref=None):
    _rc["R"] += 1
    part(ref or f"R{_rc['R']}", "R", value, "R0603", {"1": a, "2": b}, LCSC_R[value], "", section)

def C(value, a, b, section, size="0603", ref=None):
    _rc["C"] += 1
    part(ref or f"C{_rc['C']}", "C", value, f"C{size}", {"1": a, "2": b}, LCSC_C[(value, size)], "", section)

def TP(net, section):
    _rc["TP"] += 1
    part(f"TP{_rc['TP']}", "TP", net, "TP", {"1": net}, section=section, assemble=False)

GND = "GND"

# ================================================================ 1. USB-C and charger
S = "Charger"
part("J1", "USB_C_PWR", "USB-C (charge only)", "USBC",
     {"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2",
      "A6": None, "B6": None, "A7": None, "B7": None, "A8": None, "B8": None,
      "A1": GND, "A12": GND, "B1": GND, "B12": GND, "S1": GND},
     "C165948", "HRO TYPE-C-31-M-12", S)
R("5.1k", "CC1", GND, S)
R("5.1k", "CC2", GND, S)
C("10uF", "VBUS", GND, S, "0805")
part("U1", "TP4056", "TP4056", "ESOP8",
     {"4": "VBUS", "8": "VBUS", "1": GND, "2": "PROG", "3": GND, "9": GND,
      "5": "VBAT", "7": "CHRG_N", "6": "STDBY_N"}, "C16581", "TP4056-42-ESOP8", S)
R("2k", "PROG", GND, S)                      # 580 mA charge current
R("1k", "VBUS", "LED_CHRG", S)
part("D1", "LED", "Red: charging", "LED0805", {"1": "CHRG_N", "2": "LED_CHRG"}, "C84256", "NCD0805R1", S)
R("1k", "VBUS", "LED_STDBY", S)
part("D2", "LED", "Green: charged", "LED0805", {"1": "STDBY_N", "2": "LED_STDBY"}, "C2297", "KT-0805G", S)
C("10uF", "VBAT", GND, S, "0805")

# ================================================================ 2. Battery and protection
S = "Battery"
part("J2", "CONN_1x02", "LiPo 1S (JST-PH, pin 1 = +)", "JSTPH2",
     {"1": "VBAT", "2": "BAT_N", "MP": None}, "C295747", "S2B-PH-SM4-TB(LF)(SN)", S)
part("U2", "DW01A", "DW01A", "SOT23-6",
     {"5": "DW_VCC", "6": "BAT_N", "2": "DW_CS", "1": "DW_OD", "3": "DW_OC", "4": None},
     "C351410", "DW01A", S)
R("100", "VBAT", "DW_VCC", S)
C("100nF", "DW_VCC", "BAT_N", S)
R("1k", "DW_CS", GND, S)
part("Q1", "FS8205A", "FS8205A", "SOT23-6",
     {"1": "BAT_N", "6": "DW_OD", "3": GND, "4": "DW_OC", "2": "Q1_D", "5": "Q1_D"},
     "C908265", "FS8205A", S)

# ================================================================ 3. Power switch and 3.3 V rails
S = "Power"
part("SW1", "SW_SPDT", "PWR (ON = VBAT)", "PCM12", {"1": "VBAT", "3": GND, "2": "EN_SYS"},
     "C221841", "PCM12SMTR", S)
R("100k", "EN_SYS", GND, S)
part("U3", "TLV75533", "TLV75533 (MCU 3.3 V)", "SOT23-5",
     {"1": "VBAT", "3": "EN_SYS", "2": GND, "5": "3V3_MCU_LDO", "4": None}, "C404027", "TLV75533PDBVR", S)
C("10uF", "VBAT", GND, S, "0805")
C("10uF", "3V3_MCU_LDO", GND, S)
part("U4", "SIP32431", "SiP32431 (reverse-blocking switch)", "SC70-6",
     {"4": "3V3_MCU_LDO", "3": "3V3_MCU_LDO", "2": GND, "5": GND, "1": "+3V3_MCU", "6": None},
     "C141606", "SIP32431DR3-T1GE3", S)
C("10uF", "+3V3_MCU", GND, S)
C("100nF", "+3V3_MCU", GND, S)
part("U5", "TLV75533", "TLV75533 (ADS 3.3 V)", "SOT23-5",
     {"1": "VBAT", "3": "EN_SYS", "2": GND, "5": "+3V3_D", "4": None}, "C404027", "TLV75533PDBVR", S)
C("1uF", "VBAT", GND, S)
C("10uF", "+3V3_D", GND, S)
R("1M", "VBAT", "VBAT_SENSE", S)
R("1M", "VBAT_SENSE", GND, S)
C("100nF", "VBAT_SENSE", GND, S)

# ================================================================ 4. +/-2.5 V analog supplies (Cyton)
S = "Analog supply"
part("U6", "LM2664", "LM2664 inverter", "SOT23-6",
     {"5": "+3V3_D", "4": "+3V3_D", "1": GND, "6": "INV_CP", "3": "INV_CN", "2": "-3V3_RAW"},
     "C108573", "LM2664M6X/NOPB", S)
C("1uF", "+3V3_D", GND, S)
C("10uF", "INV_CP", "INV_CN", S)             # flying capacitor (Cyton C31)
C("10uF", "-3V3_RAW", GND, S)                # Cyton C33
part("U7", "TPS72325", "TPS72325 (-2.5 V)", "SOT23-5",
     {"2": "-3V3_RAW", "3": "-3V3_RAW", "1": GND, "5": "-2V5", "4": "NR_NEG"},
     "C69932", "TPS72325DBVR", S)
C("2.2uF", "-3V3_RAW", GND, S)               # Cyton C36
C("10nF", "NR_NEG", GND, S)                  # Cyton C30
C("2.2uF", "-2V5", GND, S)                   # Cyton C32
C("10uF", "-2V5", GND, S)                    # Cyton C29
part("U8", "TLV70025", "TLV70025 (+2.5 V)", "SOT23-5",
     {"1": "+3V3_D", "3": "+3V3_D", "2": GND, "5": "+2V5", "4": None},
     "C19619", "TLV70025DDCR", S)
C("2.2uF", "+3V3_D", GND, S)                 # Cyton C38
C("2.2uF", "+2V5", GND, S)                   # Cyton C35
C("10uF", "+2V5", GND, S)                    # Cyton C37

# ================================================================ 5. ADS1299
S = "ADS1299"
# DAISY_IN (41) is tied to GPIO1 (42) and held low by GPIO1's 10k pull-down (no daisy chain)
ads = {
    "16": "IN1P_F", "15": "IN1N_F", "14": "IN2P_F", "13": "IN2N_F", "12": "IN3P_F", "11": "IN3N_F",
    "10": "IN4P_F", "9": "IN4N_F", "8": "IN5P_F", "7": "IN5N_F", "6": "IN6P_F", "5": "IN6N_F",
    "4": "IN7P_F", "3": "IN7N_F", "2": "IN8P_F", "1": "IN8N_F",
    "17": "SRB1_F", "18": "SRB2_F",
    "60": GND, "61": "BIASINV", "62": "BIASOUT", "63": "BIASOUT",
    "24": "VREFP", "25": "-2V5", "28": "VCAP1", "30": "VCAP2", "55": "VCAP3", "26": "VCAP4",
    "27": None, "29": None, "64": None,
    "19": "+2V5", "21": "+2V5", "22": "+2V5", "56": "+2V5", "59": "+2V5", "54": "+2V5",
    "20": "-2V5", "23": "-2V5", "32": "-2V5", "57": "-2V5", "58": "-2V5", "53": "-2V5",
    "48": "+3V3_D", "50": "+3V3_D", "33": GND, "49": GND, "51": GND, "31": GND,
    "40": "ADS_SCLK", "34": "ADS_DIN", "43": "ADS_DOUT", "39": "ADS_CS", "47": "ADS_DRDY",
    "38": "ADS_START", "36": "ADS_RESET", "35": "ADS_PWDN", "52": "ADS_CLKSEL", "37": "ADS_CLK",
    "41": "ADS_GPIO1", "42": "ADS_GPIO1", "44": "ADS_GPIO2", "45": "ADS_GPIO3", "46": "ADS_GPIO4",
}
part("U9", "ADS1299", "ADS1299IPAGR", "TQFP64", ads, "C476817", "ADS1299IPAGR", S)
# reference and internal regulator caps (datasheet fig. 78)
C("10uF", "VREFP", "-2V5", S, "0805")
C("100nF", "VREFP", "-2V5", S)
C("100uF", "VCAP1", "-2V5", S, "1206")
C("1uF", "VCAP2", "-2V5", S)
C("1uF", "VCAP3", "-2V5", S)
C("100nF", "VCAP3", "-2V5", S)
C("1uF", "VCAP4", "-2V5", S)
# supply decoupling: AVDD groups (19/21/22, 54, 56/59), AVSS to GND, DVDD
for _ in range(3):
    C("1uF", "+2V5", GND, S); C("100nF", "+2V5", GND, S)
for _ in range(3):
    C("1uF", "-2V5", GND, S); C("100nF", "-2V5", GND, S)
for _ in range(2):
    C("1uF", "+3V3_D", GND, S); C("100nF", "+3V3_D", GND, S)
# bias drive feedback (datasheet typical 1 MOhm, Cyton 1 nF)
R("1M", "BIASINV", "BIASOUT", S)
C("1nF C0G", "BIASINV", "BIASOUT", S)
# static configuration
R("10k", "ADS_CLKSEL", "+3V3_D", S)          # internal oscillator
for g in ("ADS_GPIO1", "ADS_GPIO2", "ADS_GPIO3", "ADS_GPIO4"):
    R("10k", g, GND, S)
R("10k", "ADS_RESET", "+3V3_D", S)
R("10k", "ADS_PWDN", "+3V3_D", S)
R("10k", "ADS_CS", "+3V3_D", S)
R("10k", "ADS_START", GND, S)

# ================================================================ 6. Electrode input protection and filters
S = "Electrode inputs"
lines = []
for ch in range(1, 9):
    lines += [f"IN{ch}N", f"IN{ch}P"]
lines += ["SRB2", "SRB1"]
for ln in lines:
    R("2.2k", f"E_{ln}", f"{ln}_F", S)
    C("1nF C0G", f"{ln}_F", GND, S)
R("2.2k", "BIASOUT", "E_BIAS", S)
tvs_groups = [["E_IN8N", "E_IN8P", "E_IN7N", "E_IN7P"], ["E_IN6N", "E_IN6P", "E_IN5N", "E_IN5P"],
              ["E_IN4N", "E_IN4P", "E_IN3N", "E_IN3P"], ["E_IN2N", "E_IN2P", "E_IN1N", "E_IN1P"],
              ["E_SRB2", "E_SRB1", "E_BIAS", None]]
for i, g in enumerate(tvs_groups):
    part(f"D{3+i}", "TPD4E1B06", "TPD4E1B06", "SC70-6",
         {"1": g[0], "2": g[1], "4": g[2], "5": g[3], "3": GND, "6": None},
         "C840093", "TPD4E1B06DCKR", S)
hdr = {"1": "E_BIAS", "2": "E_BIAS", "19": "E_SRB2", "20": "E_SRB1", "21": GND, "22": GND}
for row, ch in enumerate(range(8, 0, -1), start=1):   # Cyton order: IN8 at the top, IN1 at the bottom
    hdr[str(2 * row + 1)] = f"E_IN{ch}N"
    hdr[str(2 * row + 2)] = f"E_IN{ch}P"
part("J4", "CONN_2x11", "Electrodes (odd = N, even = P)", "HDR2x11", hdr, section=S, assemble=False)

# ================================================================ 7. ESP32-S3-DevKitC-1 sockets
S = "MCU"
j5 = {str(i): None for i in range(1, 23)}
j5.update({"1": "+3V3_MCU", "2": "+3V3_MCU", "4": "M_PWDN", "5": "I2C1_SDA", "6": "I2C1_SCL",
           "7": "PPG2_INT", "9": "PPG1_INT", "10": "IMU_INT", "11": "I2C0_SCL", "12": "I2C0_SDA",
           "15": "ADS_DRDY", "16": "M_CS", "17": "M_DIN", "18": "M_SCLK", "19": "M_DOUT",
           "20": "M_START", "22": GND})
part("J5", "CONN_1x22", "DevKitC-1 J1 (3V3 side)", "SOCK1x22", j5, section=S, assemble=False)
j6 = {str(i): None for i in range(1, 23)}
j6.update({"1": GND, "4": "VBAT_SENSE", "18": "M_RESET", "21": GND, "22": GND})
part("J6", "CONN_1x22", "DevKitC-1 J3 (GND side)", "SOCK1x22", j6, section=S, assemble=False)
# series resistors MCU <-> ADS (signal integrity, limit current if one side is unpowered)
for m, a in (("M_SCLK", "ADS_SCLK"), ("M_DIN", "ADS_DIN"), ("M_CS", "ADS_CS"), ("M_START", "ADS_START"),
             ("M_RESET", "ADS_RESET"), ("M_PWDN", "ADS_PWDN"), ("M_DOUT", "ADS_DOUT")):
    R("100", m, a, S)

# ================================================================ 8. Sensor ports
S = "Sensors"
R("4.7k", "I2C0_SDA", "+3V3_MCU", S); R("4.7k", "I2C0_SCL", "+3V3_MCU", S)
R("4.7k", "I2C1_SDA", "+3V3_MCU", S); R("4.7k", "I2C1_SCL", "+3V3_MCU", S)
part("J7", "CONN_1x05", "PPG 1 (MAX30102, forehead)", "HDR1x05",
     {"1": "+3V3_MCU", "2": GND, "3": "I2C0_SDA", "4": "I2C0_SCL", "5": "PPG1_INT"}, section=S, assemble=False)
part("J8", "CONN_1x05", "PPG 2 (MAX30102, earlobe)", "HDR1x05",
     {"1": "+3V3_MCU", "2": GND, "3": "I2C1_SDA", "4": "I2C1_SCL", "5": "PPG2_INT"}, section=S, assemble=False)
part("J9", "CONN_1x05", "IMU (MPU6050)", "HDR1x05",
     {"1": "+3V3_MCU", "2": GND, "3": "I2C0_SDA", "4": "I2C0_SCL", "5": "IMU_INT"}, section=S, assemble=False)
C("100nF", "+3V3_MCU", GND, S)

# ================================================================ 9. Test points and mounting
S = "Test"
for n in ("VBAT", "+3V3_MCU", "+3V3_D", "+2V5", "-2V5", "ADS_DRDY", "ADS_CLK", GND, GND):
    TP(n, S)
for i in range(1, 5):
    part(f"H{i}", "MH", "M3", "MH", {"1": GND}, section=S, assemble=False)

# power flags: nets driven only by passive pins
FLAGS = ["VBUS", GND, "BAT_N", "DW_VCC"]


def all_nets():
    nets = {}
    for p in PARTS:
        for pin, n in p["nets"].items():
            if n:
                nets.setdefault(n, []).append((p["ref"], pin))
    return nets


if __name__ == "__main__":
    nets = all_nets()
    print(len(PARTS), "parts,", len(nets), "nets")
    for n, m in sorted(nets.items()):
        if len(m) < 2:
            print("SINGLE-PIN NET:", n, m)
