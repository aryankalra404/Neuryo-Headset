# Neuryo rev B: change list against Low-Cost-EEG (commit 3730d31)

Every difference between rev B and the reference board, why it was made, and where the reason comes from.
**Verified** = checked against an opened source (datasheet, wiki, the reference files) or by KiCad's own checks.
**Unverified** = not checked yet; listed again in [REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md).

Coordinates are in mm from the reference board's top-left corner (the same frame as the original Altium board).

## How the changes were made and checked

- **Import.** The reference Altium project (`low-cost-eeg/Hardware/PCB_Altium_Project`) was imported with KiCad 10.0.8 (File → Import Non-KiCad Project → Altium). The result is kept in [baseline-import/](baseline-import/).
- **Import checked.**
  - **Parts:** the imported schematic has the same 118 references as the reference BOM (`Production_Files/PCB Bill of Materials.xlsx`).
  - **Connections:** the imported board and the imported schematic give the same 78 multi-pin nets, pin for pin. The only difference is the ESP32 module's extra thermal-pad GND pads.
- **Design rules.** KiCad's importer only brought over Altium's generic 10 mil clearance, which produced 499 false DRC errors. The per-object clearance table was read from the PcbDoc rules and written to `*.kicad_dru`:
  - generic clearance: 10 mil
  - track to track: 0.1 mm
  - track to SMD pad: 0.1 mm
  - track to via: 0.2 mm
  - SMD pad to SMD pad: 0.15 mm
  - via to plane: 0.2 mm
  - via to hole: 0.2 mm
  - SMD pad to hole: 0.45 mm
  - board outline: 20 mil

  The Altium diff-pair rule covered only the USB pair, which rev B removes, so it was not translated.
- **Checks after every change.** All edits are scripted ([scripts/](scripts/)). After each step, KiCad's own `kicad-cli` ran:
  - ERC
  - DRC with schematic parity and refilled zones
  - netlist export

  Each netlist was compared pin by pin with the previous one ([review/netlist-diff-by-step.txt](review/netlist-diff-by-step.txt)). This check caught one accidental break in the first attempt: a clean-up step had cut the electrode-input wires. It was fixed before anything else was built on it.
- **Final result.**
  - **Schematic and board agree:** the rev B board and the rev B schematic give the same 75 multi-pin nets, pin for pin.
  - **DRC:** 0 unconnected items. The only DRC errors left are ones the unchanged import already has:
    - 11 malformed courtyards on the imported footprints
    - 1 zero-length track crossing at IN6P/IN5N (26.25, 22.25)
  - **ERC:** 1 error, left in deliberately. It is U1 PGOOD (open-drain, tied to GND as the LM27762 datasheet allows) meeting a PWR_FLAG on GND.
  - **Remaining warnings:** library links from the import, silkscreen, and wire stubs that were already in the reference.

## Schematic and netlist changes

The full list is in [review/netlist-diff-original-vs-revb.txt](review/netlist-diff-original-vs-revb.txt).

| # | Change | Why | Source | Status |
|---|---|---|---|---|
| R1 | **Removed the ESP32-S3 module side:** U5 (ESP32-S3-WROOM-1), U2 (TLV75733 3.3 V LDO) with C6/C7, J2 (USB-C) with R5/R6/C48/D7, SW2/SW3 (boot, reset) with R7/R8/C11, C12/C13, J5 (UART header), TP5 (3v3) | The Seeed XIAO ESP32-S3 replaces all of them (it has its own regulator, USB-C and buttons) | Reference schematic; [Seeed XIAO ESP32-S3 wiki](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) | Verified |
| R2 | **Change 1, reference on SRB2, filtered.** The R27 (2.2 k) / C31 (1 nF) node moves from ADS1299 pin 17 (SRB1) to pin 18 (SRB2). Pin 17 is left open. The header's SRB2 pin (J3J.2) and its ESD channel (D5 IO4) become net SRB2_HDR and no longer reach the ADS1299 | Upstream firmware uses SRB1 (MISC1 = 0x20). The Neuryo channel map needs SRB2 so channel 8 can be turned off SRB2 and run differential (ECG). The reference's SRB2 pin had no series resistor or filter | Reference schematic and `main.cpp`; ADS1299 datasheet (CHnSET SRB2 bit, MISC1 SRB1 bit) | Verified (netlist) |
| R3 | **Change 5, R10 (BIAS series) 2.2 k → 51 k**, Vishay MCT06030D5102BP500 (same series and footprint as the original) | Bias amplifier short-circuit current 1.1 mA against patient DC limits of 10 µA normal / 50 µA single fault. TI's own figures use 51 k protection resistors | ADS1299 datasheet; AAMI ES-1 limits as summarised by Fluke and MDDI (see pcb/README.md) | Part number from a [DigiKey listing](https://www.digikey.com.mx/en/products/detail/vishay/MCT06030D5102BP500/462825); availability unverified |
| R4 | **Change 4, START tied low:** new R36 10 k from ADS_START to GND. RESET (R30), PWDN (R31) and CLKSEL (R29) keep the reference's 10 k pull-ups to DVDD; they lose their MCU connection | The XIAO has no spare GPIOs. Datasheet: keep START low when using the START command; mode pins through ≥ 10 k. RESET is done with the RESET command | ADS1299 datasheet | Verified |
| R5 | **Change 2, analog off while USB is plugged in.** LM27762 EN+ (pin 12) and EN− (pin 8) and TPS7A20 EN (pin 3) move from VIN to a new net AEN. R38 100 k pulls AEN up to VIN. Q1 2N7002 pulls AEN to GND when the XIAO's 5 V pin is live (gate R37 100 k to GND). | Recording only on battery keeps the patient off mains-powered USB. The XIAO 5V pin has no voltage on battery. **LM27762:** EN pins active high, VIH 1.2 V, VIL 0.4 V, absolute max VIN, outputs actively discharged when disabled. **TPS7A20:** VEN(HI) 0.9 V, VEN(LOW) 0.3 V, internal 500 k pull-down (so AEN sits at about 0.83 × VIN until the regulator turns on), and the P version has active output discharge. **2N7002:** pin 1 G, 2 S, 3 D, VGS(th) 1–2.5 V, RDSon ≤ 5.3 Ω at 4.5 V. | [LM27762](https://www.ti.com/lit/ds/symlink/lm27762.pdf), [TPS7A20](https://www.ti.com/lit/ds/symlink/tps7a20.pdf), [Nexperia 2N7002](https://assets.nexperia.com/documents/data-sheet/2N7002.pdf) datasheets; Seeed wiki; Final Report 6.4 (author's own top fix) | Verified; LM27762 EN input current is not specified (assumed small against 100 k, unverified) |
| R6 | **USB-present sense:** R39 100 k / R40 150 k from the XIAO 5V pin to D9 (GPIO8): 5 V → 3.0 V | Firmware needs to know when USB is present so it can hold the SPI pins high-impedance while the ADS1299 is unpowered | Seeed wiki (5V pin) | Divider arithmetic verified; exact 5V-pin voltage unverified |
| R7 | **Battery voltage:** R41 / R42 220 k + C50 100 nF from VIN to D0 (GPIO1) | Battery gauge (VIN/2, at most 2.1 V at 4.2 V) | – | GPIO1 being on ADC1 is from the ESP32-S3 datasheet, not re-opened here (unverified) |
| R8 | **XIAO ESP32-S3 (U6)** with Seeed's own KiCad symbol and SMD footprint (castellated plus underside pads). BAT+ pad → VIN, BAT− → GND, 3V3 → XIAO_3V3, 5V → VUSB. Underside pads 15–22 and 25 are left unconnected. | Pin map below | [Seeed OPL KiCad library](https://github.com/Seeed-Studio/OPL_Kicad_Library) (`XIAO-ESP32-S3-SMD`); Seeed wiki | Footprint not checked against Seeed's drawing (unverified); pad 25's function unverified |
| R9 | **I²C headers J6 (earlobe MAX30102) and J7 (BMI270):** 1×4, 2.54 mm. Pads copied from the reference's TSW-103 header. Pinout 1 GND, 2 3V3, 3 SDA, 4 SCL. No on-board pull-ups. | Same bus (D8 SDA, D7 SCL). Leads are soldered in, as for the electrodes. "All Qwiic devices have pull-up resistors on the I2C lines" | [SparkFun Qwiic guide](https://learn.sparkfun.com/tutorials/qwiic-adapter-hookup-guide/hardware-overview) | Pull-ups on the actual modules unverified |
| R10 | **SW1 changes role:** battery on/off (throw 1 VBAT, common VIN, throw 3 now open; it was VBUS) | Battery only; USB power goes to the XIAO | Reference schematic | Verified |
| R11 | **ERC housekeeping:** PWR_FLAGs on VIN, VBAT, GND, AVDD, AVSS and DVDD; power symbols numbered #PWR001…; symbol instance paths set to the root sheet | The import had no power-output pins on those nets (6 ERC errors) and left power symbols un-numbered. No netlist change (checked) | – | Verified |

### Final XIAO pin map (replaces the draft in pcb/README.md)

The SPI and I²C pins were chosen so that the reference's SPI traces reach the XIAO's top row in the same order, and the I²C lines reach the bottom row without crossing. The ESP32-S3 routes SPI and I²C through its GPIO matrix, so any GPIO can be used.

| XIAO pin | GPIO | Net |
|---|---|---|
| D0 | 1 | VBAT_SENSE (VIN / 2) |
| D1 | 2 | DRDY |
| D2 | 3 | CS (R28 10 k pull-up to DVDD, as on the reference). GPIO3 is a strapping pin (JTAG source), used only if the eFuse is set (unverified here) |
| D3 | 4 | MOSI (ADS1299 DIN) |
| D4 | 5 | SCLK |
| D5 | 6 | MISO (ADS1299 DOUT) |
| D6 | 43 | not connected (UART0 TX boot log) |
| D7 | 44 | I2C_SCL |
| D8 | 7 | I2C_SDA |
| D9 | 8 | USB_SENSE |
| D10 | 9 | not connected |
| 5V / 3V3 / BAT+ / BAT− | – | VUSB / XIAO_3V3 / VIN / GND |

## Board changes

The full list is in [review/copper-and-placement-diff.txt](review/copper-and-placement-diff.txt).

| # | Change | Why | Status |
|---|---|---|---|
| B1 | **Outline 77 × 50 mm** (asked for: about 70 × 50). Left corners R5 as on the reference; right corners R1. The two right-hand mounting holes (x = 95) are gone; the two left ones stay. | The LM27762 block (U1, C1–C5, R1–R4) sits at x 63–76 on the reference and was kept exactly in place. 77 mm is the smallest width that keeps it. The XIAO's bottom-right pad needs a square-ish corner. | **Deviation from the request:** the v6 left pod must be checked for 77 × 50 (unverified). Right end of the board needs a printed clip in the pod |
| B2 | **Analog half (x < 56) unchanged except:** (a) SRB: R27/C31's via (25.5, 44.5) is joined on B.Cu (2 short segments) to the old SRB2 run, which still lands on pin 18. The SRB1 run to pin 17 (4 segments) and the header SRB2 run from D5 onwards (1 via, 3 segments) are removed; the J3J.2–D5 copper stays. (b) START trace ends at R36 (52.5, 31.6). (c) RESET/PWDN traces stop at R30/R31. (d) Five GND stitching vias at x 47–56, y 39–45 removed for SW1/J1. (e) SW1, J1 and new VBAT/VIN copper at x 44–55, y 38–50. No other track, via, pour or part in the analog half moved. | Changes 1 and 4, and space for the battery parts | Verified by the copper diff |
| B3 | **LM27762 enables:** its two VIN vias at EN− (66.25, 10.25) and EN+ (67.10, 13.60), with their four short traces, become AEN. They are joined on B.Cu to a via at U3 EN and to Q1. The In2 VIN plane now clears them. | Change 2 | Verified (DRC, 0 unconnected) |
| B4 | **TPS7A2033 (U3) with C9/C10** moved from x 80–88 into the strip under the LM27762 block (x 60.5–69, y 18–21), in the same order (C9 output, U3, C10 input). The reference's five small copper polygons (5.5 mm tall) are replaced by traces: DVDD 0.5 mm to the existing DVDD vias, VIN 0.4 mm, GND to a new via, EN to AEN. | No room for the 5.5 mm block on a 77 mm board. **This is a re-layout of a part the request listed as unchanged.** | Review item |
| B5 | **XIAO** at (56, 31), rotated 270°: USB-C flush with the right edge, top row facing the SPI traces. Old ESP32 copper under it removed (thermal-pad fan-out, GND vias, the stray GND stubs). No vias under the XIAO's pads; tented vias under its body only away from its pads (DRC clearance to the underside pads passes). | Change 7 | Verified (DRC) |
| B6 | **SPI:** same traces from the ADS1299; only the last bend of each is re-aimed at the XIAO pads (DRDY, CS, SCLK on F.Cu; MOSI and MISO from their existing vias) | – | Verified |
| B7 | **Interlock (Q1, R37, R38) on top**, right of the SPI bundle. USB-sense and battery dividers (R39–R42, C50) on the **bottom**, under the XIAO, as clones of the reference's bottom 0603 parts. J6/J7 left of the LM27762 block. Their B.Cu lines run over the In2 VIN plane, then DVDD, then VIN (not over AVDD/AVSS). | Space | Verified (DRC) |
| B8 | **Battery:** SW1 and J1 at the bottom-left (where J5 and SW3 were). VBAT 0.6 mm on F.Cu; D6 (TVS) and C49 (4.7 µF) on the bottom at J1/SW1. SW1 pin 2 → via → In2 VIN plane. TP6 (VIN) moved onto its via at (75.4, 17). | Only free edge area big enough for the 6.8 × 12.9 mm switch | **Review:** battery return current now enters near the analog half (see checklist) |
| B9 | **In2:** the old 3v3 plane under the module is renamed VIN (same outline, extended at the right edge to join the old VIN plane). AVSS, AVDD, DVDD and GND planes are unchanged. | VIN reaches the XIAO and the bottom dividers | Verified |
| B10 | **GND stitching vias** removed where they clashed with new copper (17): (47.5, 42.25), (50.5, 42.25), (50.5, 44.5), (52, 39.25), (56.5, 30.25), (58, 9.25), (59.5, 12.25), (59.5, 30.25), (61, 9.25), (62.5, 12.25), (64, 21.25), (67, 21.25), (71.5, 18.25), (71.5, 24.25), (73, 21.25), (73, 27.25), (74.5, 18.25) | Clearance | Verified (DRC) |
| B11 | **Silkscreen:** ESP-side labels removed; TP labels moved left of the test points; "REF nc"; "I2C: 1 GND 2 3V3 3 SDA 4 SCL"; attribution moved to the bottom under the XIAO (Neuryo rev B; Low-Cost-EEG, X. Asghar, University of Bath, GPL-3.0) | – | Silkscreen warnings remain (cosmetic) |

## Not changed (deliberately)

- **Change 3** (charge batteries outside the headset) needs no board change. J1 stays a removable JST-PH. The XIAO still charges at 50 mA when USB and the switch are both on (Seeed wiki).
- **Change 6.** Bottom-side parts are kept, and five more are added (R39–R42, C50). The board needs two-sided assembly.
- **Change 8** (stock): LCSC/JLCPCB numbers found:
  - ADS1299IPAGR: C476817
  - LM27762DSSR: C473398
  - TPS7A2033PDBVR: C2862740
  - TPD4E1B06DCKR: C840093 (LCSC)

  The JLC pages say "Extended". Live stock is not shown on the pages (unverified).
- **Stack-up:** left as imported (0.59 mm total, Altium's template). Choose the real JLC 4-layer stack before ordering.
