# Neuryo EEG board, rev A: design specification

Status: draft for review · 30 Oct 2026 · KiCad 7
Based on: OpenBCI Cyton (V3 Hardware Design Files, CC BY-SA 4.0). Changes from Cyton are listed in section 9.
License: this board is a derivative of the Cyton and is released under CC BY-SA 4.0 (attribution: OpenBCI).

## 1. What the board does
- 8-channel EEG/ExG acquisition with a TI ADS1299 (24-bit, 250 SPS to 16 kSPS).
- Bipolar analog supply (+2.5 V / -2.5 V) exactly as on the Cyton, so the electrode common mode sits at 0 V.
- ESP32-S3-DevKitC-1 (N8R2) plugs on top for Bluetooth LE streaming. No radio layout on this board.
- Two I2C sensor ports (2 x MAX30102 PPG, 1 x MPU6050 IMU on cables) and a battery-voltage monitor.
- Single-cell LiPo, on-board charger (USB-C, charging only) and on-board cell protection.

## 2. Use and safety rules (printed on the silkscreen)
- Battery only while electrodes are on a person. USB-C is for charging with nobody connected.
- Never connect the devkit's USB to a computer while electrodes are on a person.
- To flash firmware: PWR switch ON, nobody connected to the electrodes (the SiP32431 then blocks back-feed between the devkit's regulator and ours).
- Research prototype. Not a medical device. Not tested to IEC 60601.

## 3. Block diagram
```
USB-C (5 V, charge only) -> TP4056 charger -> LiPo cell <- DW01A + FS8205A protection
                                                |
                                     VBAT (3.0 to 4.2 V)
         PWR switch (PCM12) drives the EN pins only (no load current through the switch)
             |                         |                               |
     TLV75533 -> +3V3_MCU      TLV75533 -> +3V3_D               divider -> ESP32 ADC (VBAT_SENSE)
             |                         |      |      |
     SiP32431 load switch       ADS1299 DVDD  |   LM2664 inverter -> -3.3 V -> TPS72325 -> -2V5 (AVSS)
     (reverse blocking)                       TLV70025 -> +2V5 (AVDD)
             |
     ESP32-S3-DevKitC-1 3V3 pin, I2C sensor ports
```

## 4. Electrode interface (J4, 2 x 11, 2.54 mm male header)
| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | BIAS | 2 | BIAS |
| 3 | IN8N | 4 | IN8P |
| 5 | IN7N | 6 | IN7P |
| 7 | IN6N | 8 | IN6P |
| 9 | IN5N | 10 | IN5P |
| 11 | IN4N | 12 | IN4P |
| 13 | IN3N | 14 | IN3P |
| 15 | IN2N | 16 | IN2P |
| 17 | IN1N | 18 | IN1P |
| 19 | SRB2 | 20 | SRB1 |
| 21 | GND | 22 | GND |

- Odd pins (left row) are the N inputs: electrodes go here. SRB2 is the reference (M1 in the v3 plan). Same convention and channel order as the Cyton (channel 8 at the top), which keeps the input traces straight into the ADS1299.
- v3 channel map on this header: Fp1 = IN1N (pin 17), Fp2 = IN2N (15), Fz = IN3N (13), Pz = IN4N (11), M2 = IN5N (9), eye = IN6N (7), ECG = IN7N/IN7P (5/6), M1 = SRB2 (19), Fpz bias = BIAS (1 or 2).
- Channel 7 ECG (test kit): IN7P and IN7N, with SRB2 turned off for channel 7 in firmware.
- Every line: TPD4E1B06 ESD clamp at the connector, 2.2 kOhm series resistor, 1 nF C0G to GND at the ADS1299 pin (Cyton values).

## 5. ADS1299 configuration (fixed in hardware)
| Pin | Connection | Source |
|---|---|---|
| CLKSEL (52) | DVDD via 10 kOhm: internal 2.048 MHz oscillator | datasheet |
| CLK (37) | test point only | datasheet |
| RESV1 (31) | DGND | datasheet |
| DAISY_IN (41) | tied to GPIO1 (42), held low by its 10 kOhm pull-down (no daisy chain). Firmware keeps GPIO1 an input. | layout choice |
| GPIO1 to 4 | 10 kOhm to DGND each | datasheet |
| NC (27, 29), reserved (64) | open | datasheet |
| BIASREF (60) | GND (0 V = mid-supply) | Cyton |
| BIASOUT (63) / BIASINV (61) | 1 MOhm parallel 1 nF feedback | datasheet typical / Cyton |
| BIASIN (62) | tied to BIASOUT | Cyton |
| VCAP1 / 2 / 3 / 4 | 100 uF / 1 uF / 1 uF + 0.1 uF / 1 uF to AVSS | datasheet |
| VREFP | 10 uF (0805, 25 V) + 0.1 uF to VREFN; VREFN = AVSS | datasheet |
| AVDD / AVDD1 | 1 uF + 0.1 uF to GND per pin pair | datasheet fig. 78 |
| AVSS / AVSS1 | -2V5 rail, 1 uF + 0.1 uF to GND | datasheet fig. 78 |
| DVDD | +3V3_D, 1 uF + 0.1 uF to GND | datasheet |

Firmware settings this hardware expects: gain 12 (D29), SRB2 per channel, SRB1 off, internal reference on, bias from the channels in use.

## 6. ESP32-S3-DevKitC-1 pin map
| Function | GPIO | Devkit pin |
|---|---|---|
| ADS SCLK | 12 | J1-18 |
| ADS DIN (MOSI) | 11 | J1-17 |
| ADS DOUT (MISO) | 13 | J1-19 |
| ADS CS | 10 | J1-16 |
| ADS DRDY | 9 | J1-15 |
| ADS START | 14 | J1-20 |
| ADS RESET | 21 | J3-18 |
| ADS PWDN | 4 | J1-4 |
| I2C bus 0 SDA / SCL (PPG 1, IMU) | 8 / 18 | J1-12 / J1-11 |
| IMU INT | 17 | J1-10 |
| PPG 1 INT | 16 | J1-9 |
| I2C bus 1 SDA / SCL (PPG 2) | 5 / 6 | J1-5 / J1-6 |
| PPG 2 INT | 7 | J1-7 |
| VBAT_SENSE (ADC1_CH0) | 1 | J3-4 |

- Avoided: strapping pins (0, 3, 45, 46), USB (19, 20), UART0 console (43, 44), GPIO35 to 37 (used by octal PSRAM on N8R8), GPIO38 and 48 (RGB LED).
- Two MAX30102 modules share I2C address 0x57, so each gets its own bus.

## 7. Power budget (typical)
| Rail | Load | Current |
|---|---|---|
| +3V3_MCU | ESP32-S3 BLE streaming (peaks 189 mA TX at 0 dBm, X03) + sensors | ~100 mA avg, 250 mA peak |
| +3V3_D | ADS1299 DVDD + LM2664 + TLV70025 input | < 30 mA |
| +2V5 / -2V5 | ADS1299 analog, 8 channels | ~8 mA each |
- Battery 2500 mAh: about 15 to 20 h streaming (estimate).
- Charge current 580 mA (RPROG 2.0 kOhm), about 0.23 C.

## 8. PCB stack-up and layout rules
- 4 layers, 1.6 mm, JLCPCB standard (JLC04161H-7628).
  - L1: components, analog and digital signals, ground fill.
  - L2: solid GND plane, no splits, no traces.
  - L3: power pours: +2V5 and -2V5 under the analog area, +3V3_D and +3V3_MCU under the digital area.
  - L4: secondary signals, ground fill.
- Partition: analog (electrode header, protection, filters, ADS1299, +/-2.5 V regulators) on one side; ESP32, charger and battery on the other. SPI crosses once, at the ADS1299 digital side.
- Electrode traces: short, equal length per pair where possible, no digital lines alongside or underneath, ground fill both sides.
- Decoupling capacitors on L1 next to each supply pin; no via between capacitor and pin.
- ESP32 antenna overhangs the board edge; copper keep-out under it on all layers.
- Minimum: 0.15 mm track / 0.15 mm space, 0.3 mm via drill (JLCPCB 4-layer standard). Power tracks 0.4 mm or wider.

## 8b. Layout as built (rev A)
- 100 x 80 mm, 4 layers, 152 parts (133 assembled by JLCPCB, 19 hand-fitted or not placed: J4 to J9, test points, mounting holes).
- Rules used: 0.15 mm signal tracks, 0.4 mm power tracks (VBUS, VBAT, battery, MCU rail, inverter), 0.13 mm clearance, vias 0.5/0.25 mm (two 0.45/0.2 mm vias at U9-31 and U4-2). All within JLCPCB standard 4-layer limits.
- Ground: In1 is a solid GND plane; every SMD ground pad has its own via to it; F.Cu, B.Cu and spare In2 area are ground fills tied down with a 4 mm stitching-via grid.
- In2 pours: -2V5 under the ADS1299, +3V3_D under the analog supplies, VBAT under the power section.
- Checks: KiCad DRC 0 violations, 0 unconnected pads, PCB matches schematic (parity check 0 issues).

## 9. Changes from the OpenBCI Cyton
| Cyton | Neuryo rev A | Why |
|---|---|---|
| PIC32 + RFD22301 BLE | ESP32-S3 devkit on sockets | BLE 5, Wi-Fi option, no RF layout on our board |
| MCP1754 3.3 V | 2 x TLV75533 (analog-side and MCU-side 3.3 V) | Keeps ESP32 radio current off the ADS supply; MCP1754 is low-stock |
| No charger | TP4056 + DW01A/FS8205A + USB-C | Charge in place; cell protection on board |
| SRB1 reference default | SRB2 per channel (firmware) | v3 plan, allows bipolar ECG channel (X25) |
| microSD, LIS3DH | removed; I2C ports for MAX30102 x2 and MPU6050 | v3 sensor set |
| R/C arrays | discrete 0603 parts | JLCPCB basic parts, easier rework |
| Daisy header | removed | 8 channels are enough |

## 10. Open items to check before ordering
1. Professor review of sections 3, 5 and the schematic.
2. ESP32-S3-DevKitC-1 header spacing (25.4 mm assumed from the Espressif drawing): measure the real board with calipers.
3. Battery plug polarity: JST-PH pin 1 = +. Check the Robu cell before plugging in.
4. Snap-cable female ends fit the 2.54 mm header.
5. Re-run the JLCPCB BOM: every part in stock on the day of ordering.
