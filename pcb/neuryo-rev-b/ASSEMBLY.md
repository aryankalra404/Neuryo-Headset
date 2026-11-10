# Rev B assembly notes

JLCPCB assembles both sides from the order folder [review/order-draft-do-not-order/](review/order-draft-do-not-order/): Gerbers and drill in `gerber-and-drill/`, [bom-jlc.csv](review/order-draft-do-not-order/bom-jlc.csv) and [cpl-jlc.csv](review/order-draft-do-not-order/cpl-jlc.csv) (97 parts, the same in both). The parts in [bom-hand.csv](review/order-draft-do-not-order/bom-hand.csv) are not assembled by JLCPCB: U6 (XIAO), J1, J6, J7, J10–J19, JP1 and TP1.

## Check in JLCPCB's placement preview (before paying)
`cpl-jlc.csv` carries KiCad's angles as exported; no part is pre-rotated. The 11 Nov review expects JLCPCB's viewer to show these parts turned. For each one, compare pin 1 in the preview with the position below and rotate it there if it is wrong. Tick **"Confirm Parts Placement"** when ordering. "Expected" is a prediction from a community rotation table and the bottom-side rule (180° minus KiCad's angle); it is **Unverified** until the preview shows it. Positions are mm from the board's top-left corner, y down; Mid X/Y are the same points in the CPL file's frame.

| # | Part | Side | CPL angle | Expected in preview | Correct pin 1 / orientation | CPL Mid X, Mid Y |
|---|---|---|---|---|---|---|
| 1 | **D6** (SD05T1G) | Bottom | 0 | 180 | **Cathode on the VBAT pad at (72.29, 22.30), the pad nearer the board centre.** Reversed, it is a forward diode across the battery | 171.9011, −102.3036 |
| 2 | U4 (ADS1299) | Top | 0 | 270 | Pin 1 at the top of the left pad column, (33.68, 21.25), at the silkscreen dot | 138.0011, −105.0036 |
| 3 | U1 (LM27762) | Top | 180 | 90 | Pin 1 bottom-right, (69.20, 12.50) | 166.7511, −91.2536 |
| 4 | U3 (TPS7A20) | Top | 180 | 90 | Pin 1 bottom-right, (65.75, 20.55), on the C10 side | 162.9511, −99.6036 |
| 5 | D1–D5 (TPD4E1B06) | Top | 0 | 180 | Pin 1 top-left, x = 17.15; y = 5.60, 14.35, 24.35, 34.35, 43.10 | x 116.7511 |
| 6 | Q1 (2N7002) | Top | 0 | 270 | The single pin (drain) toward the right edge, (76.0, 3.4); gate top-left | 173.5011, −83.4036 |
| 7 | R45 (330 Ω) | Bottom | 135 | 45 | Along the CS diagonal, pads at (66.10, 26.03) and (64.90, 24.83) (a resistor: only the axis matters) | 164.0011, −105.4336 |

## XIAO ESP32-S3 (U6)
1. Solder the castellations with an iron. The XIAO pads have no paste, so the module sits flat.
2. Turn the board over. Solder BAT+ (VIN) and BAT− (GND) through their plated holes from the back. BAT− is the hole nearer the USB end.
3. Pad 25 (the module's GND copper) may stay unsoldered; pad 13 is the ground pin.
4. Pads 15–22 (JTAG, EN, USB test pads under the module) have no mask opening. Nothing is soldered there.

## Bench board (first bring-up)
- Remove Q1 (the USB interlock, top-right corner) by hand and keep it.
- Flash the bench build: `pio run -e xiao_esp32s3_bench -t upload`. It prints "BENCH BUILD: interlock ignored, not for use on a person".
- Inputs shorted, or on a signal generator. **Never on a person.**
- Probe points: MISO (TP7, bottom), DRDY (TP8, top), AEN (TP9, bottom); SCLK, MOSI and CS on R43, R44 and R45.

## Battery
- Before the first plug-in, check each cell's lead polarity against the "+" mark beside J1 with a multimeter. The board has no reverse-polarity protection.

## Electrodes
- Electrodes go on the **−** hole of channels 1–7.
- Leave the **+** holes of channels 1–7 empty, and J10 pin 2 (GND).

## In the pod
- Fix the XIAO's antenna at the rear of the pod, away from the electrode leads.
- USB is never plugged in while the headset is worn. The interlock stops recording; it does not isolate the wearer.
