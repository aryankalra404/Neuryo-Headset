# Neuryo EEG board rev A: review checklist

Work through this before paying JLCPCB. Tick each box in KiCad (open `kicad/neuryo.kicad_pro`).

## A. For the ECE professor (schematic, about 30 minutes)
- [ ] ADS1299 support pins match the datasheet table in `DESIGN.md` section 5 (VCAP1 to 4, VREFP/VREFN, RESV1, CLKSEL, unused GPIO).
- [ ] Bias drive: 1 MOhm parallel 1 nF between BIASOUT and BIASINV, BIASIN tied to BIASOUT, BIASREF to GND (0 V mid-supply).
- [ ] Bipolar supply chain copied from the Cyton: +3V3_D -> LM2664 -> -3.3 V -> TPS72325 -> -2.5 V; +3V3_D -> TLV70025 -> +2.5 V.
- [ ] Input network: TPD4E1B06 at the connector, 2.2 kOhm series, 1 nF C0G to GND. Is a differential capacitor also wanted (datasheet section 12.1)?
- [ ] MCU 3.3 V rail: TLV75533 -> SiP32431 reverse-blocking switch -> devkit 3V3 pin. OK to power the devkit through its 3V3 pin?
- [ ] Battery: TP4056 (580 mA) + DW01A/FS8205A protection, power switch drives only the regulator EN pins.

## B. For whoever opens the PCB (about 20 minutes)
- [x] Run DRC in KiCad: 0 errors, 0 unconnected items (done 30 Oct; re-run after any edit).
- [ ] Analog area (left/top) has no digital tracks running through it; SPI crosses once near the ADS1299 right side.
- [ ] Every ADS1299 decoupling capacitor sits next to its pin with no via in between.
- [ ] DAISY_IN (pin 41) is tied to GPIO1 (pin 42), held low by its 10 kOhm pull-down: firmware must keep ADS GPIO1 as an input.
- [ ] GND plane (In1) is unbroken under the ADS1299 and the electrode traces.
- [ ] ESP32 antenna end overhangs the right edge; nothing copper under it.
- [ ] 3D view: devkit, USB-C, battery plug and slide switch all reach the edges they should.

## C. Measure on real parts before ordering
- [ ] DevKitC-1 header row spacing with calipers: the board assumes 25.40 mm.
- [ ] Battery plug polarity on the Robu cell: board expects JST-PH pin 1 = +.
- [ ] Snap-cable female ends fit the 2.54 mm electrode header.

## D. On the JLCPCB order page
- [ ] Upload `fab/neuryo-revA-gerbers.zip`: 4 layers, 1.6 mm, JLC04161H-7628 stack-up.
- [ ] Assembly: Economic, top side, 2 boards. Upload `neuryo-revA-BOM-JLCPCB.csv` and `neuryo-revA-CPL.csv`.
- [ ] BOM page: every part in stock. ADS1299IPAGR is C476817.
- [ ] Placement preview: check pin 1 / rotation of U1 to U9, Q1, D1 to D7, J1, J2, SW1. Rotate in the preview if any is off (JLCPCB rotations differ from KiCad for some packages).
- [ ] Hand-soldered afterwards (not assembled): J4, J5, J6, J7, J8, J9 (see `neuryo-revA-BOM-hand-soldered.csv`).

## E. First power-up (bench, nobody attached)
1. Battery only, PWR off: board draws only microamps.
2. PWR on, no devkit fitted: measure +3V3_MCU, +3V3_D, +2V5, -2V5 at the test points.
3. Fit the devkit, flash firmware with PWR on, read the ADS1299 ID register (expect 0x3E).
4. Inputs shorted to SRB2 at gain 12: noise under 6 uVpp (IEC limit).
