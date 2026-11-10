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
  - J19 (was J3J) pin 2 is now a dead pin (silkscreen "REF nc"). The electrode headers J3A–J3J are now J10–J19 (CHANGES R11).
  - Firmware (F3) sets MISC1 = 0x00, CHnSET SRB2 on channels 1–7 and off on channel 8, and expects the electrodes on the N (−) pins. Bias and lead-off now sense the N inputs (BIAS_SENSN 0x7F, LOFF_SENSN 0xFF, LOFF_SENSP 0x81): agree with this starting point?
- [ ] **Change 2 (interlock).**
  - AEN schematic; Q1 pinout (Nexperia: 1 G, 2 S, 3 D).
  - EN thresholds: LM27762 VIH 1.2 V; TPS7A20 VEN(HI) 0.9 V with an internal 500 k pull-down against R38 100 k.
  - ★ LM27762 EN input current is not in the datasheet. Is 100 k pull-up fine?
  - When USB is present the ADS1299 is unpowered while the XIAO is live. 4th pass: 330 Ω in series on SCLK, MOSI and CS (R43–R45, CHANGES P3) limit the current into its input diodes; the firmware still releases the lines (F4).
- [ ] **Change 4.** START: R36 10 k to GND. RESET/PWDN/CLKSEL keep their 10 k pull-ups. Firmware (F2) uses the RESET (0x06) and START (0x08) commands; BIASREF_INT = 1 as upstream. 4th pass: RESET also goes to XIAO D10, pulsed open-drain before the RESET command (CHANGES P5, F9).
- [ ] **Change 5.** R10 = 51 k (MCT06030D5102BP500). Bias still works at 51 k? Test with bias on and off, as the reference author did.
- [ ] **USB sense** 100 k / 150 k (3.0 V at 5 V). ★ What voltage does the XIAO's 5V pin actually show on USB (diode drop)?
- [ ] **Battery divider** 2 × 220 k + 100 nF on GPIO1 (= A0 in Seeed's variant, so ADC-capable). ★ GPIO3 (CS) is a strapping pin (JTAG source select, only if the eFuse is set): ESP32-S3 datasheet not re-opened.

## 3. Layout items that need a human eye
- [ ] ★ **Board is 77 × 50 mm, not 70 × 50.** The LM27762 block was kept exactly in place, which sets the width. The v6 model (v6.1, 9 Nov) now holds the real layout: the left pod grows to about 98 × 77 mm and 22 mm off the skin, and every part clears a 2 mm wall plus 0.5 mm air (tightest: the JP1 header with its shunt, then J1 and the XIAO). Still to check on a print: the 2 remaining mounting holes and the clip at the back end.
- [ ] ★ **U3 (TPS7A2033) area re-laid out** (CHANGES B4). The reference's copper polygons became traces; same part order and caps. Check DVDD output path, C9/C10 placement and the GND return (via at 67.2, 19.6).
- [ ] **Battery entry at the right-hand end** (2nd pass, CHANGES B8): J1 opening at the right edge, PCM12 switch actuator about 1 mm past the edge. Check both against the pod (cable exit, a slot for the actuator). ★ The silkscreen doesn't mark which slider position is "on" (common terminal 2 to terminal 1, VBAT). Confirm on the part and add an arrow if wanted.
- [ ] **SW1 = C&K PCM12SMTR**, 0.3 A at 6 V DC. Enough for the XIAO's BLE peaks plus the analog side? (Datasheet rating; the reference used a 6 A switch.)
- [ ] **XIAO footprint (Seeed's library).** Checked against Seeed's own module PCB: pads match to about 0.02 mm, and pad 25 is the module's exposed GND (now GND with a via). Pads 15–22 are copper only, nothing soldered. Underside pads need hot-air or a hot plate (change 7).
- [ ] **I²C lines on B.Cu.** B.Cu's reference plane is In2 (VIN, then DVDD, then VIN), not GND. That matches how the reference already routed MOSI/MISO/CS on B.Cu over DVDD.
- [ ] **New stitching-via gaps** (CHANGES B10, 19 vias, all at x ≥ 56): enough GND stitching left on the right?
- [ ] **Q1 land pattern** is KiCad's standard SOT-23, not Nexperia's own figure.
- [ ] **No third mounting hole.** There is no room at the right end once J1 and SW1 are there; the board relies on the 2 left holes plus a clip. OK for the pod?

## 4. Firmware ([firmware/](firmware/))
- [ ] Read F1–F12. Both environments (normal and bench) compile cleanly (0 errors, 0 warnings, 11 Nov); nothing has run on hardware.
- [ ] Electrode wiring changes for the user: electrodes on the − pins of channels 1–7; sign inverted (host must flip it).
- [ ] **Gain and sample rate.** The firmware keeps upstream's tested gain 24 at 500 SPS (±187.5 mV range); the design doc's D29 says gain 12 at 250 SPS (±375 mV). Keep 24 for bring-up, read each channel's DC offset on real electrodes, then make D29 and the firmware agree (CHnSET 0x58 / CH8SET 0x50 and CONFIG1 0x96 for gain 12 at 250 SPS).
- [ ] ★ **USB interlock releases SCLK and MOSI?** The ISR clears the GPIO output enables; that releases CS (a plain GPIO), but SCLK and MOSI are driven by the SPI peripheral through the GPIO matrix, and `SPI.end()` only runs in `loop()` 20–120 ms later (since the 5th pass it does run on every plug-in, F10; before, it never ran). Scope SCLK, MOSI and CS while plugging USB in with the board running; if they stay driven, detach the SPI pins in the ISR.

## 5. Parts and assembly
- [ ] **Stock and price** (JLCPCB "Extended" parts):
  - ADS1299IPAGR: C476817
  - LM27762DSSR: C473398
  - TPS7A2033PDBVR: C2862740
  - TPD4E1B06DCKR: LCSC C840093

  Live stock was not visible on the pages.
- [ ] **Order from [bom-jlc.csv](review/fab-draft-do-not-order/bom-jlc.csv)** (`scripts/jlcbom.py`), not from the value-only `bom.csv`: it carries the reference's part numbers (CHANGES R14), so the 0.1 % thin-film resistors (R1–R4, R10–R27) and C0G capacitors stay what the reference was tested with. If JLCPCB has no exact match, pick the same value, tolerance, dielectric and size. Since the 5th pass every assembled part has an LCSC number; nine reference parts that were out of stock are replaced by in-stock equivalents of the same value, tolerance and case (CHANGES Q1; R9 becomes thick film, C14 50 V). **Use the order folder [review/order-draft-do-not-order/](review/order-draft-do-not-order/)** (Gerbers and drill, bom-jlc.csv, cpl-jlc.csv). The XIAO, J1, the headers, JP1 and TP1 are in bom-hand.csv: not assembled by JLCPCB ([ASSEMBLY.md](ASSEMBLY.md)).
- [ ] **Battery polarity** (CHANGES B14): "+" is now beside J1 pin 2. Check every cell's lead order against it before plugging in.
- [ ] **Two-sided assembly.** Bottom: C15–C31, R32–R35 (as on the reference) plus C49, D6 (moved), R39–R42, C50, and (4th pass) R45, R46, R47.
- [ ] **I²C header pinout** (1 GND, 2 3V3, 3 SDA, 4 SCL): right for the cables? The board now has its own 4.7 k pull-ups to 3.3 V (R46, R47); for the module's own pull-ups see section 9.
- [ ] **Fab outputs.** Upload from `review/order-draft-do-not-order/gerber-and-drill/` (11 Gerbers: 4 copper, 2 paste, 2 silkscreen, 2 mask, Edge.Cuts; drill split into PTH and NPTH, 5th pass). In JLCPCB's Gerber viewer the SW1 peg holes and the two mounting holes must show as non-plated (they are the only 4 holes in the NPTH file). `review/fab-draft-do-not-order/` is the full kicad-cli export, for viewing only.

## 6. KiCad check results to confirm
- [ ] ERC: 1 error (U1 PGOOD tied to GND meets the GND PWR_FLAG; datasheet allows tying PGOOD to ground). The rest are warnings from the import.
- [ ] DRC: 0 unconnected. Errors are the import's own (11 malformed courtyards, 1 zero-length track at 26.25, 22.25). Warnings: library links (import), the XIAO footprint's silkscreen over its own pads, SW1's outline past the edge, 3 silkscreen overlaps already on the reference.
- [ ] Schematic ↔ board: 78 of 78 multi-pin nets identical after the 4th pass (net names differ because the import named them differently; KiCad's parity report lists those as 199 "net conflicts").
- [ ] `review/netlist-diff-original-vs-revb.txt` lists every connection change; nothing outside CHANGES.md should be there.

## 7. Bench tests added by the 3rd-pass review (9 Nov)
- [ ] **Interlock.** Board on battery, switch on: AVDD, AVSS and DVDD at their test points. Plug USB in: all three fall to 0 V. Unplug: they return and the ADS1299 ID reads 0x3E again.
- [ ] **Input-capacitor A/B (CHANGES "Not changed").** Use 20 kΩ and 50 kΩ resistors in place of electrodes (and a lower one, about 5 kΩ, for the M1 reference, like a gel pad), drive their common end with a small 50 Hz signal, and record the 50 Hz amplitude on channels 1–7. Then remove C15, C29, C27, C25, C23, C21 and C19 from one board with hot air and repeat. Keep the change only if it lowers the 50 Hz on the pod channels as well as the gel-pad channels.
- [ ] **DC offsets** on real electrodes (strip, pods, mastoid and eye pads) at gain 24, to settle the gain (section 4).
- [ ] **SW1 direction.** With a multimeter find which slider position joins terminal 2 to 1 (battery on), then add an "ON" arrow to the silkscreen.

## 8. Questions for the professor (3rd-pass review)
- [ ] **Fault current through the inputs.** Inputs have 2.2 kΩ, as on the reference and the OpenBCI Cyton. Estimated currents if the ADS1299 fails:
  - one input pin shorted to a ±2.5 V rail: about 25–95 µA, through the electrodes and the 51 kΩ bias path, depending on electrode impedance and the bias state;
  - two pins at opposite rails: about 100–350 µA (5 V across 4.4 kΩ plus two electrode impedances of 20 kΩ down to 5 kΩ).

  The single-fault DC limit quoted in pcb/README is 50 µA. Raising the inputs to 51 kΩ would cover it but adds about 0.23 µVrms each against the ADS1299's own about 0.17 µVrms (1.13 µVpp at gain 12, 250 SPS). Acceptable for an ethics-approved prototype, or change before anyone wears it?
- [ ] **BIASREF pin.** It is tied to AVSS (as on the reference) while the firmware sets BIASREF_INT = 1 (internal mid-supply). The datasheet text available to me did not say how the pin should be connected in that mode. Is the AVSS tie harmless? (The reference author saw no benefit from the bias drive.) **Answered by the 11 Nov review:** the datasheet says to tie BIASREF to AVSS or leave it floating when unused, which is the case with BIASREF_INT = 1 (review section 4; not re-opened here).

## 9. Before paying (4th pass, 10 Nov; for the owner)
- [ ] **XIAO 5V pin on battery.** Power a bare XIAO from a cell on its BAT pads, no USB, and measure the 5V pin. It must read about 0 V: the interlock depends on it (Seeed's wiki says the pin has no voltage on battery). Since the 5th pass (R37 10 k) the board's VUSB node sees about 0.09 × the open-pin reading; Q1 needs well under 1 V.
- [ ] **Paper fit.** Print the top layer 1:1 and lay the XIAO, the JST-PH socket and the PCM12 switch on it.
- [ ] **JLCPCB placement preview.** Go through the list in [ASSEMBLY.md](ASSEMBLY.md) ("Check in JLCPCB's placement preview"): **D6 first** (reversed it shorts the battery through its forward diode), then U4, U1, U3, D1–D5, Q1, R45. The CPL carries KiCad's angles unrotated. Tick "Confirm Parts Placement".
- [ ] **JLCPCB stock at order time.** LCSC stock was checked on 11 Nov (CHANGES Q1); JLCPCB's own assembly stock could not be read. The tightest line is R11–R27 (Yageo RT0603BRD072K2L, C861295): 17 per board.
- [ ] **J1 hole vs C49 (5th pass).** DRC has one new error: J1 pin 2's 0.8 mm hole reaches 0.05 mm into C49's courtyard (bottom). C49's pad is 0.44 mm from the hole, its body about 1.15 mm. Decide: accept it, or move C49 about 0.1 mm to the right (existing copper; would need a scripted edit and a DRC run).
- [ ] **MAX30102 module.** Measure what voltage its SDA/SCL pull-ups go to. If 1.8 V, remove them from the module (the board now pulls up to 3.3 V).
- [ ] **Professor review** of this checklist, as planned.
- [ ] **Bench board.** On one board remove Q1 and flash the bench build (ASSEMBLY.md). Check that the status string shows `ads=1 id=3E` and the bench warning, and that SCLK, MOSI, CS (R43–R45), MISO, DRDY and AEN (TP7–TP9) look right on a logic analyzer. Put Q1 back before that board is ever worn, or keep it as the bench board.
- [ ] **Hardware reset.** With the analog side on, scope D10/RESET: one low pulse of about 10 µs at start-up, otherwise held high by R30. With USB in (Q1 fitted), D10 must stay high-impedance.
- [ ] **XIAO battery pads.** After soldering BAT+ and BAT− through the holes, check continuity from the battery connector to the XIAO's BAT+ and that the module sits flat.
- [ ] **USB plug-in then unplug (5th pass, F10).** With the analog side running on battery, plug USB in, then out: the status string must go `ads=0`, then back to `ads=1 id=3E`, and data must resume.
