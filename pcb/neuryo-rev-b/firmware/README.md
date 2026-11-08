# Rev B firmware (XIAO ESP32-S3)

The upstream Low-Cost-EEG firmware (`../../low-cost-eeg/Software/Firmware_Platformio_Project`), changed for the rev B board. The table of changes is in [../CHANGES.md](../CHANGES.md#firmware-2nd-pass) (F1–F6).

**Same as upstream:**
- BLE name `ESP32_EEG_DATA`, service and data characteristic UUIDs
- 28-byte packets (counter, 3 status bytes, 8 channels × 3 bytes), 8 packets per notify
- 500 SPS, gain 24, BOOT button turns lead-off detection off

The upstream receiver works unchanged.

**Different:**
- **Electrode wiring.** Electrodes go on the **−** pins of channels 1–7. The reference (M1) goes on REF, which is wired to SRB2. Leave the + pins of channels 1–7 empty. Channel 8 is differential: ECG goes on + and −.
- **Sign.** The ADS1299 measures P − N, so channels 1–7 read (reference − electrode). Invert them on the host.
- **USB.** While USB is plugged in the analog side has no power (interlock), and the firmware leaves the ADS1299 alone. Unplug USB to record. Serial output is there for debugging while USB is connected.
- **Status characteristic.** UUID `5c3a1f2e-8d4b-4f6a-9e21-7b0c6d9a4e13`, read or notify, every 10 s. Example: `usb=0 ads=1 vbat=3912 i2c=57 68`.
- **I²C.** The bus is scanned at boot. MAX30102 is at 0x57 and BMI270 at 0x68/0x69. There are no drivers for them yet.

## Build
```
pio run            # PlatformIO, espressif32 ~6.13.0, board seeed_xiao_esp32s3
pio run -t upload  # XIAO on USB
```

## Status
- **Compile:** builds with **0 errors and 0 warnings** (8 Nov 2026, PlatformIO, espressif32 6.13.0, Arduino core 2.0.17). RAM 13.9 % (45 kB), flash 28.0 % (937 kB of 3.3 MB). Log: [build-log.txt](build-log.txt).
- **Bench test:** not done (no board yet). On the first board, in order:
  1. Rails come up with the switch on and USB unplugged.
  2. Rails go off when USB is plugged in.
  3. ADS1299 ID reads 0x3E.
  4. Shorted-input noise.
  5. Lead-off flags.
  6. Alpha with eyes closed.
