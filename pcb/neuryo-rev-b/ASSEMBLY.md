# Rev B assembly notes

JLCPCB assembles both sides from [bom-jlc.csv](review/fab-draft-do-not-order/bom-jlc.csv). The parts in [bom-hand.csv](review/fab-draft-do-not-order/bom-hand.csv) are not assembled by JLCPCB: U6 (XIAO), J1, J6, J7, J10–J19, JP1 and TP1.

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
