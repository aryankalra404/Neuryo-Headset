# Neuryo rev B PCB review (commit a3c452d, 11 Nov 2026)

Don't order yet. The copper is sound, but the order package is not: 66 of the 108 JLCPCB-assembled parts have no LCSC number, nine of those part numbers can't be filled from JLCPCB stock today, and the placement file will likely show several parts rotated.

Reviewed at commit `a3c452d`. No repo file was edited and nothing was ordered. On the Mac, two fresh copies of the commit were added (`pcb-work/review-a3c452d-asis`, `-refill`) plus the runner outputs `out/rv5asis`, `out/rv5refill`.

## 1. BOM

**The 13 rows with an LCSC number all match** (MPN, value, tolerance, package, board footprint). Verified on each part page, e.g. [C476817](https://jlcpcb.com/partdetail/C476817); the others are C14663, C840093, C65189, C25804, C25803, C22807, C22961, C23138, C23162, C221841, C473398, C2862740. All are in stock. The ADS1299 shows 256 in stock at $79.04 each.

**17 rows have no LCSC number.** Each MPN was searched in JLCPCB's library and its part page opened. Stock is as of the night of 10–11 Nov.

| Row | BOM MPN | JLCPCB # | Stock | In-stock equivalent (same value, tolerance, case) |
|---|---|---|---|---|
| C1 | C0603C474K4RACAUTO | C561783 | 650 | not needed |
| C4, C5 | GCM21BR71C225KA64K | C1852484 | 3,944 | not needed |
| C10 + 8 | CC0603KRX7R7BB105 | C106248 | 563,350 | not needed |
| C34 | GRM31CR61A107MEA8L | C883598 | 46,599 | not needed |
| D6 | SD05T1G | C233423 | 56,677 | not needed |
| R2 | RT0603BRD07120KL | C705720 | 128,157 | not needed |
| R3 | RT0603BRD07105KL | C861072 | 3,720 | not needed |
| R4 | AT0603BRD07100KL | C855559 | 3,317 | not needed |
| C15–C31 | C0603C102F5GACTU | C2167790 | **0** | GRM1885C1H102FA01D, [C913702](https://jlcpcb.com/partdetail/C913702), 14,074 |
| C32, 37, 41, 42, 45, 47 | C0603X104J4RACTU | C2259003 | **0** | C0603C104J4RACTU, [C22401913](https://jlcpcb.com/partdetail/C22401913), 4,190 |
| R1 | MCT06030D1303BP100 | C1706338 | **0** | RT0603BRD07130KL, [C861109](https://jlcpcb.com/partdetail/C861109), 4,841 |
| R9 | MCT06030C1004FPW00 | C2107808 | **0** | 0603WAF1004T5E, [C22935](https://jlcpcb.com/partdetail/C22935), Basic (thick film, 1 %) |
| R10 | MCT06030D5102BP500 | C1700586 | **0** | RT0603BRD0751KL, [C861458](https://jlcpcb.com/partdetail/C861458), 61,957 |
| R11–R27 | MCT06030D2201BP500 | C1702497 | **0** | RT0603BRD072K2L, [C861295](https://jlcpcb.com/partdetail/C861295), 108,144 |
| C2, C3, C49 | GCJ21BR71C475KA01K | **not listed** | – | CL21B475KOFNNNE, [C107365](https://jlcpcb.com/partdetail/C107365), 71,336 |
| C9, C33 | GRJ21BR61E106KE01L | C668336 | **6** | CL21A106KAYNNNE, [C15850](https://jlcpcb.com/partdetail/C15850), Basic |
| C14 | GRM1885C2A152JA01D | C710906 | **11** | GRM1885C1H152JA01D, [C162204](https://jlcpcb.com/partdetail/C162204), 18,198 (50 V, was 100 V) |

- **Recommendation:** use the equivalents; the alternative is asking JLCPCB to source the exact parts, which adds lead time. They keep the technology (0.1 % thin film, C0G, X7R/X5R) except R9, which becomes thick film.
- **Unverified:** the C913702 page does not state the dielectric; C0G comes from Murata's part code.
- The 4.7 µF "L" reel twin (C161119) shows 6 in stock, so it is no way out.

## 2. Footprints against manufacturer drawings

| Part | Drawing | Board | Result |
|---|---|---|---|
| SW1 terminals | 0.7 × 1.5 at −2.25 / +0.75 / +2.25, 1.75 above the peg line | 0.7 × 1.5 at −2.25 / +0.75 / +2.25, 1.76 above | Match (Verified) |
| SW1 pegs, tabs | Holes Ø0.9, 3.0 apart; tabs 1.0 × 0.8, inner edges 6.3 apart | Ø0.9 NPTH at ±1.5; 1.0 × 0.8 at ±3.65 (6.30) | Match (Verified) |
| SW1 tab rows | One dimension (1.13) could not be assigned | 2.21 centre to centre | Unverified; mechanical tabs only |
| J1 | 2 holes Ø0.7 +0.1/−0, pitch 2.0; post 0.5 square; mating face 6.25 from pins | Drill 0.7, pad 1.2, pitch 2.0; face at x = 76.90, edge at 77.0 | Position matches; hole is at JST's minimum (section 6) |
| Q1 | 3 lands 0.6 × 0.7; pitch 1.9; rows 2.0 apart; 1 G, 2 S, 3 D | 0.8 × 0.9; 1.9; 2.0; VUSB, GND, AEN | Match, pads 0.2 larger (Verified) |
| U3 | 5 lands 1.1 × 0.6, pitch 0.95, rows 2.6; 1 IN, 2 GND, 3 EN, 4 N/C, 5 OUT | Identical; VIN, GND, AEN, GND, DVDD | Match; pin 4 has no internal connection (Verified) |
| U6 pad 23 | (4.445, −10.882), 2.5 × 1.1 | Same, now plated hole 0.7 | Match (Verified) |
| U6 pad 24 | (4.445, −12.787), 2.5 × 1.1 | Same, now plated hole 0.7 | Match (Verified) |
| U6 pad 25 | (10.01, −8.5), 2.75 × 2.5 | Same, no paste | Match (Verified) |

- The 0.2 mm ring on pads 23/24 equals JLCPCB's recommended minimum for multilayer boards.
- Seeed's module BAT pad is 2.03 × 1.02 mm, so it covers the 0.7 mm hole.
- Sources: C&K PCM sheet, [JST PH sheet](https://datasheet.lcsc.com/datasheet/pdf/6c6fce4367275d84ec6a99bf09f1250f.pdf?productCode=C173752) and [Nexperia 2N7002](https://datasheet.lcsc.com/datasheet/pdf/5799b048ec886fff0aa915589422b872.pdf?productCode=C65189) (LCSC-hosted copies; the makers' sites refused the download); [TI TPS7A20](https://www.ti.com/lit/ds/symlink/tps7a20.pdf) p. 57; [Seeed OPL library](https://github.com/Seeed-Studio/OPL_Kicad_Library), commit `b0035c5`.

## 3. Placement

Two format problems first:
- The header row (Ref, PosX, PosY, Rot, Side) has to become Designator, Mid X, Mid Y, Rotation, Layer before upload ([JLCPCB help](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)).
- Bottom-side angles need converting to 180° minus the KiCad angle, because JLCPCB's viewer does not mirror bottom parts the way KiCad does ([KiBot notes](https://kibot.readthedocs.io/en/master/notes_position.html)).

The "likely" column is a prediction from the [community rotation table](https://github.com/matthewlai/JLCKicadTools/blob/master/jlc_kicad_tools/cpl_rotations_db.csv) (Unverified); JLCPCB's preview decides. Pin-1 positions are from the board file (Verified), in mm from the top-left corner.

| Part | File angle | Likely needed | Correct position |
|---|---|---|---|
| U4 | 0 | 270 | Pin 1 top of the left pad column, (33.68, 21.25), at the dot |
| U1 | 180 | 90 | Pin 1 bottom-right, (69.20, 12.50) |
| U3 | 180 | 90 | Pin 1 bottom-right, (65.75, 20.55), C10 side |
| D1–D5 | 0 | 180 | Pin 1 top-left, x = 17.15; y = 5.60, 14.35, 24.35, 34.35, 43.10 |
| Q1 | 0 | 270 | Single pin (drain) toward the right edge, (76.0, 3.4); gate top-left |
| D6 (bottom) | 0 | 180 | Cathode on the VBAT pad, (72.29, 22.30), nearer the board centre |
| R45 (bottom) | 135 | 45 | Along the CS diagonal, pads at (66.10, 26.03) and (64.90, 24.83) |

D6 matters most: reversed, it is a forward diode across the battery. Tick "Confirm Parts Placement" when ordering.

## 4. Firmware

**Register writes: all legal** against the [ADS1299 datasheet](https://www.ti.com/lit/ds/symlink/ads1299.pdf) (Verified).

| Register | Value | Meaning |
|---|---|---|
| CONFIG1 | 0x95 | Reserved bits correct, 500 SPS |
| CONFIG3 | 0xFE | Reference buffer on, internal BIASREF, bias buffer on, bias sense on; also sets BIAS_MEAS |
| CONFIG4 | 0x02 | Lead-off comparators on |
| LOFF | 0x04 | 24 nA, DC, 95 % |
| CH1–7SET | 0x68 | Gain 24, SRB2 closed |
| CH8SET | 0x60 | Gain 24, SRB2 open |
| MISC1 | 0x00 | SRB1 open |
| GPIO | 0x00 | Four outputs low, into R32–R35 |

**Timing: within limits** (Verified).
- 1 s wait before reset, against a 128 ms minimum.
- Hardware pulse 10 µs, against 2 clock periods (about 1 µs).
- 1 ms and 10 ms waits after reset, against 18 clock periods (about 9 µs).
- SPI mode 1 at 2 MHz, and SDATAC before any register access.

**Three things to fix in firmware; none blocks the board.**
- **USB plug-in then unplug.** The ISR clears `adsRunning`, so the loop's `if (usb && adsRunning)` never calls `adsStop()` and `SPI.end()` never runs. On unplug, [`SPI.begin()` returns early](https://github.com/espressif/arduino-esp32/blob/2.0.17/libraries/SPI/src/SPI.cpp). Either the ADS1299 fails to restart or SCLK/MOSI were never released. Verified by reading; which of the two happens is Unverified.
- **CONFIG3** sets BIAS_MEAS with no channel using it; harmless, and the comment omits it.
- **Reference settling.** There is no wait after enabling the internal reference (150 ms start-up), so the first samples are off.

The checklist question on BIASREF is answered: the datasheet says to tie it to AVSS or leave it floating when unused, which is the case with BIASREF_INT = 1.

## 5. ERC and DRC

Both ran in KiCad 10.0.8 on the Mac, on the committed files as they are and again after refilling zones.
- **ERC:** 231 items, 1 error (U1 PGOOD), identical item for item to `review/erc.json`.
- **DRC:** 393 items, 0 unconnected, 12 errors (11 courtyards, 1 zero-length track), identical item for item to `review/drc.json`.
- The regenerated Gerbers, drill file and positions file are identical to the committed draft apart from date lines.

## 6. Other changes before ordering

- **R37: 100 kΩ to 10 kΩ.** In Seeed's own board file the 5V pin is VBUS, with 100 kΩ to ground and a Schottky (LMBR4010BST5G) to the regulator input. On battery that diode's leakage is what sits on Q1's gate. Its [datasheet limit](https://datasheet.lcsc.com/datasheet/pdf/06d3ea725ed70ec6b5cbec3ad00b2d06.pdf?productCode=C2912031) is 30 µA at 10 V; into the 42 kΩ now on that node that is 1.25 V, above the 2N7002's 1 V minimum threshold. The interlock could then switch the analog side off on battery. With 10 kΩ it is 0.26 V. Same footprint, part already in the BOM. Real leakage is Unverified: on the bare-XIAO test, the board sees 0.42 × the reading now and 0.09 × with 10 kΩ.
- **J1 drill: 0.7 to 0.8 mm.** JST asks for Ø0.7 +0.1/−0 and the post's diagonal is 0.71 mm. [JLCPCB's hole tolerance](https://jlcpcb.com/capabilities/pcb-capabilities) is +0.13/−0.08, so a 0.7 hole can arrive at 0.62. Rerun DRC after the change.
- **Gerber set.** Only copper, paste, silkscreen, mask and Edge.Cuts belong in the upload, per [JLCPCB's KiCad guide](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-8). The draft has a dozen extra layers. Check in the viewer that the SW1 peg holes and mounting holes show as non-plated.
- **Bench board.** With Q1 removed and USB in, the analog side runs from the XIAO's charger output. Keep the battery connected for noise tests (reviewer's judgement, Unverified).

## Findings

| # | What | Where | Severity | Status | Source |
|---|---|---|---|---|---|
| 1 | 17 rows (66 parts) have no LCSC number | `bom-jlc.csv` | High | Verified | JLCPCB search and part pages |
| 2 | 6 MPNs at zero stock, 1 not listed, 2 nearly out | C2/3/49, C9/33, C14, C15–31, C32…, R1, R9, R10, R11–27 | High | Verified (stock that night) | Part pages in section 1 |
| 3 | D6 likely shown reversed | `positions.csv`, bottom | High | Unverified | KiBot notes, board file |
| 4 | U4, U1, U3, D1–D5, Q1 likely shown rotated | `positions.csv`, top | High | Unverified | Rotation table |
| 5 | KiCad headers; R45 likely 90° off | `positions.csv` | Medium | Headers Verified, R45 Unverified | JLCPCB help, KiBot notes |
| 6 | Interlock can false-trip on diode leakage | R37 | Medium | Circuit Verified, leakage Unverified | Seeed board file, LRC and Nexperia datasheets |
| 7 | Hole can finish below JST's minimum | J1 | Medium | Verified | JST sheet, JLCPCB capabilities |
| 8 | No clean restart after USB plug-in then unplug | `main.cpp` loop and ISR | Low | Logic Verified | Arduino-ESP32 2.0.17 `SPI.cpp` |
| 9 | BIAS_MEAS set; no reference settling wait | `main.cpp` `adsStart()` | Low | Verified | ADS1299 datasheet |
| 10 | Tab row spacing not confirmed | SW1 | Low | Unverified | C&K PCM sheet |
| 11 | Extra Gerber layers | `fab-draft-do-not-order/` | Low | Verified | JLCPCB KiCad guide |

Fix these first: fill in the BOM with in-stock parts (1, 2), correct the placement file and confirm it in JLCPCB's preview (3–5), and change R37 and the J1 drill (6, 7); then order.