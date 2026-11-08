# Neuryo EEG board, rev B (plan)

**Status (8 Nov 2026):** designed in KiCad 10 ([neuryo-rev-b/](neuryo-rev-b/)), ERC/DRC/netlist checked, **waiting for professor review, not ordered** ([checklist](neuryo-rev-b/REVIEW-CHECKLIST.md)). Rev B copies the analog half of a proven open board and adds a ready-made ESP32 board. Rev A (30 Oct, the v3 board: Cyton circuit, auto-routed, 100 × 80 mm, DevKit on sockets) is removed from this folder; it is in the git history (commit `14b8c37` and earlier).

| Folder | What is in it |
|---|---|
| [neuryo-rev-b/](neuryo-rev-b/) | Rev B in KiCad 10: project, [change list](neuryo-rev-b/CHANGES.md), [review checklist](neuryo-rev-b/REVIEW-CHECKLIST.md), renders, ERC/DRC reports, netlist and copper diffs against the reference, the reference imported into KiCad, and the scripts that made the edits |
| [low-cost-eeg/](low-cost-eeg/) | The upstream repo, complete (hardware, production files, firmware, receiver, case STLs, docs). The design rev B copies: [Low-Cost-EEG](https://github.com/XavierAsghar/Low-Cost-EEG) by Xavier Asghar, commit `3730d31` (12 Aug 2026). GPL-3.0 ([LICENSE](low-cost-eeg/LICENSE)); what was left out is listed in its [NOTICE](low-cost-eeg/NOTICE.md) |

## Why this board
- **Same chips as ours:** ADS1299 (8 channels, SRB2 reference, bias drive) and an ESP32-S3, battery powered, 4-layer.
- **Built and used:** it recorded ECG, EMG, eyes-closed alpha, SSVEPs and P300s (Final Report, chapter 5), and a second person [rebuilt it](https://github.com/agteo/diy-eeg-mac) from the same files and recorded alpha.
- **Measured:** 1.10 µVpp input-referred noise with the inputs shorted, on the board itself (Final Report, section 6.1; the 2 µVpp earlier in the report is TI's evaluation board). The ADS1299 datasheet gives 1.13 µVpp typical at gain 12, 250 SPS.
- **Its analog section follows the OpenBCI Cyton**, like rev A did.

## What rev B copies unchanged (the analog half, about 55 × 50 mm)
In the KiCad rev B the analog half (x < 56 mm) and the LM27762 block are unchanged apart from the review changes; the TPS7A20 and its two capacitors had to be re-laid out in a strip under the LM27762 block (see [CHANGES B4](neuryo-rev-b/CHANGES.md)).

Placement, routing, ground pours and stitching kept as in the reference, left half of its board:
- Electrode inputs: 2.54 mm pin headers, 8 differential pairs, BIAS, SRB2.
- TPD4E1B06 ESD diodes, then 2.2 kΩ + 1 nF C0G low-pass on every input.
- ADS1299 with its decoupling, bipolar ±2.5 V mode.
- LM27762 charge-pump LDO for ±2.5 V; TPS7A20 low-noise LDO giving the ADS1299 its own 3.3 V.
- Stack-up: signal / ground / segmented power / signal; no split ground plane; analog left, digital right.

## What rev B changes (the digital half)
| Removed from the reference | Added in rev B |
|---|---|
| ESP32-S3-WROOM-1 and its 3.3 V LDO | Seeed XIAO ESP32-S3, soldered flat on castellated pads (Seeed's KiCad footprint); its 3V3 feeds the digital parts |
| USB-C, USB ESD, boot and reset buttons | The XIAO's own USB-C and buttons |
| USB / battery selector switch | Battery on/off slide switch; battery JST-PH to the XIAO's BAT pads (the XIAO charges it) and to the LM27762 and TPS7A20 inputs |
| UART header | J6: earlobe MAX30102 and J7: BMI270, 1×4 headers on one I²C bus (the forehead MAX30102 header J8 was dropped) |
| | Battery divider (2 × 220 kΩ + 100 nF) to an ADC pin; USB-present divider; USB interlock (Q1, R37, R38) |
| | Outline 77 × 50 mm (the LM27762 block is kept in place, so 70 was not reachable), 2 mounting holes, for the v6 left pod |

## XIAO pin map
Final map in [neuryo-rev-b/CHANGES.md](neuryo-rev-b/CHANGES.md#final-xiao-pin-map-replaces-the-draft-in-pcbreadmemd). SPI on D1–D5, battery on D0, I²C on D7/D8, USB sense on D9; START, RESET and PWDN are tied (change 4).

## Review (8 Nov 2026): changes needed before ordering
Checked against the reference schematic and firmware (upstream `main.cpp`), the ADS1299 datasheet and the Seeed XIAO ESP32-S3 wiki.

| # | Change | Why |
|---|---|---|
| 1 | **Reference through SRB2, filtered.** Move R27 (2.2 kΩ) and C31 (1 nF) from SRB1 (pin 17) to SRB2 (pin 18, the next pin); leave SRB1 open and drop the header's direct SRB2 line. | On the reference, the REF header goes through R27/C31 to SRB1, but its SRB2 pin runs straight to the ADS1299 with no series resistor or filter. Upstream firmware uses SRB1 (MISC1 = 0x20, electrodes on the P inputs). D25 needs SRB2 so channel 8 can run differential (ECG). |
| 2 | **Analog off while USB is plugged in.** XIAO 5V pin → 2N7002 gate (100 kΩ to ground); its drain pulls the LM27762 EN+/EN− and TPS7A20 EN net (100 kΩ up to the battery) low. D2 (GPIO3) reads USB-present through a divider; firmware keeps the SPI pins high-impedance then. | Recording only on battery isolates the patient from mains. The XIAO's 5V pin is live only on USB (Seeed). The reference author lists this as the top-priority fix (Final Report 6.4). |
| 3 | **Charge batteries outside the headset.** Removable JST-PH cell, a separate charger and a spare. | The XIAO ESP32-S3 charges at 50 mA (Seeed), about 20 h for 1000 mAh. |
| 4 | **Pins with no XIAO GPIO:** START to ground through 10 kΩ (use the START command), RESET and PWDN to DVDD through 10 kΩ (RESET command), CLKSEL high as on the reference. Firmware sets BIASREF_INT = 1 (CONFIG3), as upstream does; the BIASREF pin is tied to AVSS on this board. | Datasheet: keep START low when using the command; mode pins through ≥ 10 kΩ. Upstream issue #1 (RESET on GPIO8 vs GPIO14) does not apply: rev B has no RESET GPIO. |
| 5 | **BIAS series resistor 51 kΩ** (R10, was 2.2 kΩ). Inputs stay 2.2 kΩ for the prototype; revisit with the test lab. | The bias amplifier can source 1.1 mA (datasheet) against DC patient-current limits of 10 µA normal and 50 µA single fault. TI's own figures show 51 kΩ patient-protection resistors. A 51 kΩ input resistor would add about 0.23 µVrms of noise, so not on the inputs yet. The reference author found the bias drive gave no benefit on ECG, so test with it on and off. |
| 6 | **Keep the bottom-side parts.** The 17 input filter capacitors, R32–R35, C49 and D6 are on the bottom: order two-sided assembly or hand-solder them; don't move analog parts. | The analog layout is the part that is proven. |
| 7 | **XIAO flat on the board:** its BAT pads are underneath, so the footprint needs matching pads and hot-air or hot-plate soldering; no copper or vias under its other pads. | Castellated edges can be hand-soldered, the underside cannot. |
| 8 | **Stock check:** ADS1299IPAGR, LM27762DSSR, TPS7A2033PDBVR, TPD4E1B06DCKR at LCSC/JLCPCB. | One order. |

## Channel map (v4)
Electrodes on the N inputs with M1 on SRB2 (through the filtered REF path, change 1), as on the Cyton: ch 1 Fp1, ch 2 Fp2, ch 3 Fz, ch 4 Pz, ch 5 M2, ch 6 eye, ch 7 Cz, ch 8 ECG (SRB2 off, differential, test kit). BIAS to Fpz.

## Steps
1. ~~Import the reference into KiCad and check it~~ (done 8 Nov: BOM references and board/schematic connectivity match; sheet-by-sheet PDF comparison is on the checklist).
2. ~~Remove the module side; add the XIAO, J6, J7, interlock, dividers~~ (done; see the change list).
3. ~~ERC, DRC, netlist diff after every change~~ (done; reports in `neuryo-rev-b/review/`). 3D check in the v6 left pod at 77 × 50 mm still to do.
4. Professor review ([checklist](neuryo-rev-b/REVIEW-CHECKLIST.md)).
5. Order 2 assembled boards (JLCPCB); hand-solder the XIAOs. For the v5 left pod, leave the electrode input headers off and solder each lead into its two holes (the headers stand about 8.4 mm: Samtec TSW-xxx-26 is a 5.84 mm post on a 2.54 mm body). Footprints and layout stay as in the reference.
6. First board: power rails, ADS1299 ID register, shorted-input noise against the 6 µVpp target, then alpha with eyes closed.

## Licence
The reference is GPL-3.0, so rev B's board files will be GPL-3.0 too. That is fine for the prototype; decide before the product whether to keep the board open or redraw it.
