# Rev B review checklist (for the professor, before anything is ordered)

Nothing has been ordered. Each item says what to look at and where. Items marked ★ are the ones I'm least sure about.

Open `Neuryo_RevB.kicad_pro` in KiCad 9 or 10. The baseline (the reference imported unchanged) is in `baseline-import/`. Diffs, renders and reports are in `review/`.

## 1. Import fidelity (the base everything rests on)
- [ ] Compare `baseline-import/` with `low-cost-eeg/Production_Files/PCB Schematic and Layout.pdf`, sheet by sheet and layer by layer. Already checked:
  - same 118 references as the reference BOM
  - imported board and imported schematic agree net for net
- [ ] Footprints imported from Altium: spot-check the ADS1299 (PAG0064A), LM27762 (DSS0012B, thermal pad and its three vias), TPS7A20 (DBV0005A) and TPD4E1B06 (DCK) against TI's land patterns. 11 imported courtyards are "malformed" (an import artifact, the same on the baseline).
- [ ] Stack-up: now JLCPCB JLC04161H-7628, 1.6 mm, ENIG (CHANGES B12). Confirm 1.6 mm suits the pod and that ENIG is wanted (flat pads for the XIAO underside). No controlled-impedance lines are left.

## 2. Each change against its reason ([CHANGES.md](CHANGES.md))
- [ ] **Change 1 (SRB2).**
  - REF → R27 → SRB2 (pin 18), C31 on that node, pin 17 open.
  - Copper: R27's via (25.5, 44.5) → 2 B.Cu segments → the reference's old SRB2 run.
  - J3J pin 2 is now a dead pin (silkscreen "REF nc").
  - Firmware (F3) sets MISC1 = 0x00, CHnSET SRB2 on channels 1–7 and off on channel 8, and expects the electrodes on the N (−) pins. Bias and lead-off now sense the N inputs (BIAS_SENSN 0x7F, LOFF_SENSN 0xFF, LOFF_SENSP 0x81): agree with this starting point?
- [ ] **Change 2 (interlock).**
  - AEN schematic; Q1 pinout (Nexperia: 1 G, 2 S, 3 D).
  - EN thresholds: LM27762 VIH 1.2 V; TPS7A20 VEN(HI) 0.9 V with an internal 500 k pull-down against R38 100 k.
  - ★ LM27762 EN input current is not in the datasheet. Is 100 k pull-up fine?
  - ★ When USB is present the ADS1299 is unpowered while the XIAO is live. Firmware (F4) keeps SCLK/MOSI/CS as inputs at boot and clears their output enables in the USB_SENSE interrupt. For a few microseconds after plug-in, while the rails are still decaying, the ESP32 still drives them. Is that acceptable, or should rev B add series resistors (e.g. 100 Ω–1 k) on SCLK/MOSI/CS?
- [ ] **Change 4.** START: R36 10 k to GND. RESET/PWDN/CLKSEL keep their 10 k pull-ups. Firmware (F2) uses the RESET (0x06) and START (0x08) commands; BIASREF_INT = 1 as upstream.
- [ ] **Change 5.** R10 = 51 k (MCT06030D5102BP500). Bias still works at 51 k? Test with bias on and off, as the reference author did.
- [ ] **USB sense** 100 k / 150 k (3.0 V at 5 V). ★ What voltage does the XIAO's 5V pin actually show on USB (diode drop)?
- [ ] **Battery divider** 2 × 220 k + 100 nF on GPIO1 (= A0 in Seeed's variant, so ADC-capable). ★ GPIO3 (CS) is a strapping pin (JTAG source select, only if the eFuse is set): ESP32-S3 datasheet not re-opened.

## 3. Layout items that need a human eye
- [ ] ★ **Board is 77 × 50 mm, not 70 × 50.** The LM27762 block was kept exactly in place, which sets the width. Check the v6 left pod (and the 2 remaining mounting holes; the right end needs a clip).
- [ ] ★ **U3 (TPS7A2033) area re-laid out** (CHANGES B4). The reference's copper polygons became traces; same part order and caps. Check DVDD output path, C9/C10 placement and the GND return (via at 67.2, 19.6).
- [ ] **Battery entry at the right-hand end** (2nd pass, CHANGES B8): J1 opening at the right edge, PCM12 switch actuator about 1 mm past the edge. Check both against the pod (cable exit, a slot for the actuator). ★ The silkscreen doesn't mark which slider position is "on" (common terminal 2 to terminal 1, VBAT). Confirm on the part and add an arrow if wanted.
- [ ] **SW1 = C&K PCM12SMTR**, 0.3 A at 6 V DC. Enough for the XIAO's BLE peaks plus the analog side? (Datasheet rating; the reference used a 6 A switch.)
- [ ] **XIAO footprint (Seeed's library).** Checked against Seeed's own module PCB: pads match to about 0.02 mm, and pad 25 is the module's exposed GND (now GND with a via). Pads 15–22 are copper only, nothing soldered. Underside pads need hot-air or a hot plate (change 7).
- [ ] **I²C lines on B.Cu.** B.Cu's reference plane is In2 (VIN, then DVDD, then VIN), not GND. That matches how the reference already routed MOSI/MISO/CS on B.Cu over DVDD.
- [ ] **New stitching-via gaps** (CHANGES B10, 19 vias, all at x ≥ 56): enough GND stitching left on the right?
- [ ] **Q1 land pattern** is KiCad's standard SOT-23, not Nexperia's own figure.
- [ ] **No third mounting hole.** There is no room at the right end once J1 and SW1 are there; the board relies on the 2 left holes plus a clip. OK for the pod?

## 4. Firmware ([firmware/](firmware/))
- [ ] Read F1–F6 in CHANGES.md. Compile status is in `firmware/README.md`. Nothing has run on hardware.
- [ ] Electrode wiring changes for the user: electrodes on the − pins of channels 1–7; sign inverted (host must flip it).

## 5. Parts and assembly
- [ ] **Stock and price** (JLCPCB "Extended" parts):
  - ADS1299IPAGR: C476817
  - LM27762DSSR: C473398
  - TPS7A2033PDBVR: C2862740
  - TPD4E1B06DCKR: LCSC C840093

  Live stock was not visible on the pages.
- [ ] **Assign LCSC numbers** for the new passives (100 k, 150 k, 220 k, 10 k, 100 nF 0603) and Q1. SW1 is C221841. The XIAO and the headers are hand-soldered.
- [ ] **Two-sided assembly.** Bottom: C15–C31, R32–R35 (as on the reference) plus C49, D6 (moved), R39–R42, C50.
- [ ] **I²C modules.** ★ Do the chosen MAX30102 and BMI270 boards have pull-ups, and to what voltage? Some MAX30102 modules pull up to 1.8 V. Is the header pinout (1 GND, 2 3V3, 3 SDA, 4 SCL) right for the cables?
- [ ] **Fab outputs.** `review/fab-draft-do-not-order/` is a draft from kicad-cli for viewing only. Set the drill/place origin and regenerate after review.

## 6. KiCad check results to confirm
- [ ] ERC: 1 error (U1 PGOOD tied to GND meets the GND PWR_FLAG; datasheet allows tying PGOOD to ground). The rest are warnings from the import.
- [ ] DRC: 0 unconnected. Errors are the import's own (11 malformed courtyards, 1 zero-length track at 26.25, 22.25). Warnings: library links (import), the XIAO footprint's silkscreen over its own pads, SW1's outline past the edge, 3 silkscreen overlaps already on the reference.
- [ ] Schematic ↔ board: 75 of 75 multi-pin nets identical (net names differ because the import named them differently; KiCad's parity report lists those as 199 "net conflicts").
- [ ] `review/netlist-diff-original-vs-revb.txt` lists every connection change; nothing outside CHANGES.md should be there.
