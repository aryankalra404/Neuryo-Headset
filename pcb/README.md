# Neuryo EEG board, rev B (plan)

**Status (7 Nov 2026):** planned, not laid out. Rev B copies the analog half of a proven open board and adds a ready-made ESP32 board. Rev A (30 Oct, the v3 board: Cyton circuit, auto-routed, 100 × 80 mm, DevKit on sockets) is removed from this folder; it is in the git history (commit `14b8c37` and earlier).

| Folder | What is in it |
|---|---|
| [reference/low-cost-eeg/](reference/low-cost-eeg/) | The design rev B copies: [Low-Cost-EEG](https://github.com/XavierAsghar/Low-Cost-EEG) by Xavier Asghar, commit `3730d31` (12 Aug 2026). Altium project (schematic, 4-layer PCB, libraries, BOM), Gerbers and drill files, schematic and layout PDF, Final Report and User Guide. GPL-3.0 ([LICENSE](reference/low-cost-eeg/LICENSE)) |

## Why this board
- **Same chips as ours:** ADS1299 (8 channels, SRB2 reference, bias drive) and an ESP32-S3, battery powered, 4-layer.
- **Built and used:** it recorded ECG, EMG, eyes-closed alpha, SSVEPs and P300s (Final Report, chapter 5), and a second person [rebuilt it](https://github.com/agteo/diy-eeg-mac) from the same files and recorded alpha.
- **Not measured:** its report has no noise figure for the board itself (the 2 µVpp in it is from TI's evaluation board). Our first-board test fills that in.
- **Its analog section follows the OpenBCI Cyton**, like rev A did.

## What rev B copies unchanged (the analog half, about 55 × 50 mm)
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
| UART header | J6: earlobe MAX30102 (I²C bus 0) · J8: forehead test-window MAX30102 (I²C bus 1) · BMI270 on bus 0 |
| | Battery divider (2 × 220 kΩ + 100 nF) to an ADC pin |
| | Outline about 70 × 50 mm (could reach 75), 4 mounting holes, shaped for the brow module |

## Draft XIAO pin map (to confirm in the schematic)
| XIAO pin | GPIO | Use |
|---|---|---|
| D8 | 7 | ADS1299 SCLK |
| D9 | 8 | ADS1299 DOUT (MISO) |
| D10 | 9 | ADS1299 DIN (MOSI) |
| D0 | 1 | ADS1299 CS |
| D1 | 2 | ADS1299 DRDY (interrupt) |
| D4 | 5 | I²C bus 0 SDA: earlobe MAX30102, BMI270 |
| D5 | 6 | I²C bus 0 SCL |
| D6 | 43 | I²C bus 1 SDA: forehead MAX30102 (test kit). Also the boot-log UART TX: harmless to the sensor, can be silenced in firmware |
| D7 | 44 | I²C bus 1 SCL |
| D3 | 4 | Battery voltage (ADC1) |
| D2 | 3 | Spare (strapping pin; leave free or use for BMI270 INT) |

ADS1299 START, RESET and PWDN: copy the reference's choices where its ESP32 pins are not needed; START and RESET can be sent as SPI opcodes.

## Channel map (v4)
Electrodes on the N inputs with M1 on SRB2, as on the Cyton: ch 1 Fp1, ch 2 Fp2, ch 3 Fz, ch 4 Pz, ch 5 M2, ch 6 eye, ch 7 Cz, ch 8 ECG (SRB2 off, differential, test kit). BIAS to Fpz.

## Steps
1. Open the reference in KiCad 8+ (File → Import → Altium project) and check the import against `production/PCB Schematic and Layout.pdf`, sheet by sheet and layer by layer.
2. Delete the digital half; add the XIAO, BMI270, J6, J8, battery switch and divider; keep every analog part, trace and pour.
3. ERC and DRC at zero; every new net checked against its datasheet; 3D check in the v4 brow module.
4. Professor review of the changed parts and the import.
5. Order 2 assembled boards (JLCPCB); hand-solder the XIAOs.
6. First board: power rails, ADS1299 ID register, shorted-input noise against the 6 µVpp target, then alpha with eyes closed.

## Licence
The reference is GPL-3.0, so rev B's board files will be GPL-3.0 too. That is fine for the prototype; decide before the product whether to keep the board open or redraw it.
