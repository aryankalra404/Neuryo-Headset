# Neuryo rev B, 4th pass: implementation plan

**For:** the model implementing this (Claude Opus 5.5).
**From:** design review of 10 Nov 2026 (Claude Fable 5.2).
**Repo:** `aryankalra404/Neuryo-Headset`, folder `pcb/neuryo-rev-b/`. Commit to `main` directly (owner's standing rule for this repo).

Read this whole file before changing anything. Do the steps in order. Run the checks in section 3 after every step, not only at the end.

---

## 1. Context

### 1.1 What the board is
Rev B is the open Low-Cost-EEG board (ADS1299, LM27762 ±2.5 V, TPS7A20 3.3 V) with its ESP32 module side replaced by a Seeed XIAO ESP32-S3. It is 77 × 50 mm, 4 layers (F.Cu / In1 GND / In2 split power / B.Cu), KiCad 10.0.8. It has not been ordered. The team can afford one order of 2 assembled boards, so nothing may be left unchecked.

Read first: `pcb/README.md`, `pcb/neuryo-rev-b/CHANGES.md`, `pcb/neuryo-rev-b/REVIEW-CHECKLIST.md`.

### 1.2 What the 10 Nov review found
Checked and correct, do not rework:
- Every ADS1299 and LM27762 pin, the ±2.5 V divider values (R1–R4) and all decoupling match the datasheets.
- Board and schematic agree on all 344 pads.
- The analog half's copper, mask and paste match the upstream Gerbers layer by layer, apart from the intended SRB2 and START changes.
- The XIAO footprint is not mirrored, USB is at the right edge, BAT− is the pad nearer USB (as Seeed's wiki says).
- Rev B's drill file matches the board (258 of 258 holes).

Problems this pass fixes:

| # | Problem | Fix | Priority |
|---|---|---|---|
| A | The XIAO takes battery power only through the BAT+ pad under the module, which an iron cannot reach | Plated hole in the BAT pads; no paste on XIAO pads | Must |
| B | USB switches the ADS1299 off (interlock), so no serial log is possible while it runs; firmware reports `ads=1` even if the ID read fails | Bench build flag, honest status, silkscreen note | Must |
| C | The XIAO can drive SCLK/MOSI/CS into an unpowered ADS1299 | 330 Ω in series on each | Must |
| D | No I²C pull-ups on the board; some MAX30102 modules pull up to 1.8 V | Two 4.7 kΩ to XIAO_3V3 | Must |
| E | ADS1299 RESET has no GPIO although D6 and D10 are free | D10 (GPIO9) → RESET | Should; skip if not clean |
| F | Nothing to clip a logic analyzer to | Test pads on MISO, DRDY, AEN | Optional; skip if not clean |

### 1.3 Rules
1. **Do not move, delete or re-route anything at x < 56 mm** except the one RESET trace in step E. That half is proven; every other change there is a regression.
2. **Do not change values that are same-footprint swaps:** input resistors (2.2 kΩ), input capacitors (1 nF), R10 (51 kΩ), gain, BIASREF tie. They are bench decisions.
3. **Every edit is scripted**, as in `scripts/edit_sch.py` and `scripts/edit_pcb2.py`. Add `scripts/edit_sch4.py` and `scripts/edit_pcb4.py`. No hand edits to the `.kicad_sch` / `.kicad_pcb`.
4. **Never guess a clearance.** KiCad's DRC decides. The coordinates below are suggestions measured from the current file; if DRC disagrees, move the new part, never the existing copper.
5. **If a Should/Optional step cannot be made DRC-clean without touching existing copper, skip it** and say so in CHANGES.md. A missing test pad is fine. A broken board is not.
6. Mark every claim in CHANGES.md **Verified** (with what verified it) or **Unverified**, as the file already does.
7. Do not order anything. Do not regenerate `review/fab-draft-do-not-order/` under another name.

### 1.4 Coordinates
All coordinates here are mm from the board's top-left corner, y down, the same frame as CHANGES.md. File coordinates = these + (98.5011, 80.0036), as in `edit_pcb2.py` (`X0`, `Y0`).

### 1.5 Running KiCad
KiCad's CLI runs on the owner's Mac through the job runner (`scripts/runner.sh`, copy at `~/Desktop/Neuryo-Research/pcb-work/`). Ask the owner to start it in Terminal if `pcb-work/out/<job>/DONE` does not appear. A job is a file `pcb-work/jobs/<name>.job`: line 1 the project path inside `pcb-work` without extension, line 2 options (`img refill fab fw`). Work on a copy inside `pcb-work/revb/`, then copy results back into the repo.

---

## 2. Steps

New reference designators: R43–R47, TP7–TP9. Next free numbers after R42, C50, TP6.

### Step A. XIAO battery pads: plated holes, no paste (Must)

**Why.** U6 pad 23 (BAT+, net VIN) is under the module. With a plated hole it is soldered from the back of the board with an iron. Paste on any XIAO pad would be reflowed by JLCPCB into bumps, and the module would not sit flat.

**Current state.**
- Pad 23: (66.88, 35.45), VIN, SMD roundrect 2.5 × 1.1 (1.1 mm along board x).
- Pad 24: (68.79, 35.45), GND, same size.
- Pad 25: (64.50, 41.01), GND, 2.75 × 2.5, has a via.
- VIN via beside pad 23 at (65.55, 35.45). Keep it.

**Change (footprint `Neuryo_RevB.pretty/XIAO-ESP32-S3-SMD.kicad_mod` and the U6 instance on the board).**
1. Pads 23 and 24: type `thru_hole`, same shape and size, drill 0.7 mm, layers `*.Cu *.Mask`. No paste layer.
2. Pads 1–14 and 25: remove `F.Paste` from their layers. Keep `F.Cu F.Mask`.
3. Pad 25 stays SMD. It is a second ground only (pad 13 is the GND pin), so it may stay unsoldered. Do **not** make it through-hole: the XIAO_3V3 track on B.Cu runs under it at y = 41.5.
4. Pads 15–22 unchanged (copper only, no mask opening).

**Check.**
- DRC: pad 23 joins the In2 VIN zone, pad 24 joins GND on In1 and B.Cu, and neither shorts the other plane. Refill zones.
- Hole-to-hole and annular ring pass (ring is 0.2 mm on the narrow side). If DRC or JLCPCB's 4-layer rules need more, reduce the drill to 0.6 mm; do not widen the pads (they are 1.91 mm apart).
- Nearest bottom parts are R41 (71.85, 33.00) and C50; confirm clearance to pad 24's B.Cu copper.
- Netlist diff: none.

### Step B. Bench mode for the interlock (Must; firmware and silkscreen only)

**Why.** Q1 pulls AEN low whenever USB is plugged in, which is right for a board on a head but makes first bring-up blind. The reference author powered the whole board from USB for debugging (Final Report 6.4). Without Q1 fitted, R38 holds AEN high and the analog side runs on USB.

**Board.** No copper change. JLCPCB fits Q1 on both boards. On the one bench board the team removes Q1 by hand and keeps it.
- Silkscreen near Q1 (top-right corner, 0.8 mm text, must pass the silk rules): `Q1: USB interlock`.
- Bottom silkscreen, in the attribution block or beside it: `No Q1 = bench only, never on a person`.

**Firmware.** See step G.

**Check.** Netlist diff: none. DRC silk warnings: none new.

### Step C. 330 Ω in series on SCLK, MOSI, CS (Must)

**Why.** When USB is present the ADS1299 is unpowered and the XIAO is live. 330 Ω limits the current into the ADS1299's input diodes to about 8 mA at 3.3 V (datasheet limit 10 mA continuous per pin). CS is the worst case because it idles high. At 1–4 MHz SPI, 330 Ω with about 15 pF adds roughly 5 ns.

**Schematic.** Split each net at the XIAO end:
- R43: `SCLK_X` (U6 pad 5, D4) – `SCLK` (U4 pin 40).
- R44: `MOSI_X` (U6 pad 4, D3) – `MOSI` (U4 pin 34).
- R45: `CS_X` (U6 pad 3, D2) – `CS` (U4 pin 39 **and** R28). R28's pull-up must stay on the ADS1299 side.
- 0603, 330 Ω 1 %, footprint `FP-AC0603-MFG` (the one R36–R42 use).

**Board (suggested, all F.Cu, all at x ≥ 56).**
- **R43 (SCLK):** on the vertical run (63.96, 26.43) → (63.96, 30.90). Centre about (63.96, 28.2), rotated 90°.
- **R44 (MOSI):** on the F.Cu run at y = 28.25 before the via at (60.00, 28.25). Centre about (57.75, 28.25), rotated 0°. XIAO pad 7 (unconnected) starts at y = 30.47 below it.
- **R45 (CS):** on the run (53.75, 22.60) → (62.67, 22.60), right of R28 and at x ≥ 56. DRDY (y = 21.75) and MISO (y = 23.73) run beside it, so there is not room for a 0603 in line. Options, in order: jog CS and the resistor into free space, or put R45 on the bottom with two vias (the board already has bottom-side assembly). Do not move DRDY or MISO.

**Check.**
- Netlist diff shows exactly three nets split and three new parts.
- DRC clean. Prefer ≥ 0.2 mm from the new pads to neighbouring tracks even where the imported rule allows 0.1 mm.
- No change at x < 56 (copper diff).

### Step D. I²C pull-ups (Must)

**Why.** J6/J7 have no pull-ups. The plan relied on the modules', but some MAX30102 modules pull SDA/SCL up to 1.8 V, below the ESP32-S3's input-high level at 3.3 V.

**Schematic.** R46: `I2C_SDA` – `XIAO_3V3`. R47: `I2C_SCL` – `XIAO_3V3`. 0603, 4.7 kΩ 1 %, same footprint.

**Board (suggested).** Bottom side, as clones of R39–R42. Useful existing B.Cu copper:
- XIAO_3V3: horizontal at y = 41.5 from x = 56.65 to 69.04; vertical at x = 56.65.
- I2C_SDA: horizontal at y = 44.4 from x = 56.20 to 61.42; via (61.42, 45.60).
- I2C_SCL: horizontal at y = 45.0 from x = 55.75 to 58.28; via (58.88, 45.60).
- R46 fits between the 3V3 run and the SDA run, for example centred (60.2, 42.95), rotated 90°.
- R47 has to cross SDA to reach SCL. Use the J6/J7 end instead if that is cleaner (bottom side between the header columns at x = 58.3 and 61.3; 3V3 at y = 7.14, SDA 9.68, SCL 12.22), or a short F.Cu hop under the XIAO body away from its pads.

**Check.** Netlist diff: two parts, no net renamed. DRC clean. No via under any XIAO pad.

### Step E. D10 → ADS1299 RESET (Should; skip if not clean)

**Why.** CHANGES.md says the XIAO has no spare GPIO, but D6 (GPIO43) and D10 (GPIO9) are unconnected. A hardware reset is the datasheet's first-choice path and costs one trace. D6 stays free (it prints the ROM boot log).

**Schematic.** Net `ADS_RESET` (U4 pin 36, R30 pin 1) gains U6 pad 11 (D10). R30 (10 kΩ to DVDD) stays. No series resistor: firmware only ever pulls this line low (open-drain), so it cannot back-power the ADS1299.

**Board (suggested).**
1. F.Cu from R30 pad 1 (48.75, 26.10) east along y = 26.10 to about x = 54.3. This is the reference's own RESET trace: the baseline has (48.75, 26.10) → (61.09, 26.10) on F.Cu, and rev B left that corridor empty between SCLK (y = 25.25) and MOSI (y = 28.25). This is the only edit allowed at x < 56.
2. Via at about (54.3, 26.10).
3. B.Cu south along x ≈ 54.3 to y ≈ 46.9. GND vias sit at (53.50, 30.25) and (55.00, 39.25); the I²C and 3V3 runs are at x = 55.75, 56.20, 56.65.
4. B.Cu east along y ≈ 46.9 to x = 66.5. This passes below the vias at (58.88, 45.60), (61.42, 45.60), (63.96, 45.60).
5. North to a via at about (66.5, 45.75), then F.Cu to U6 pad 11 at (66.50, 48.00), the same pattern as pads 8–10. R39's pads on B.Cu are at (65.45, 44.45) and (67.15, 44.45).

**Check.** Netlist diff: one pin added to ADS_RESET. DRC clean with no existing track, via or part moved. Copper diff at x < 56: one F.Cu trace and at most one via. If any of that fails, undo the step, leave D10 unconnected and record it.

### Step F. Test pads (Optional; skip if not clean)

**Why.** For the logic analyzer. After step C, the pads of R43–R45 already give SCLK, MOSI and CS.

**Change.** 1.0 mm round SMD pads, mask open, **no paste**, on F.Cu or B.Cu at x ≥ 56: TP7 MISO, TP8 DRDY, TP9 AEN. Label them on the silkscreen. Do not add a through-hole header and do not move existing tracks to make room.

**Check.** Netlist diff: three single-pin parts. DRC clean.

### Step G. Firmware (`firmware/src/main.cpp`, library in `firmware/lib/ADS1299/`)

1. **Honest status.** `adsStart()` returns `false` and leaves `adsRunning = false` when `(id & 0x1F) != 0x1E`. The status string becomes `usb=<0|1> ads=<0|1> id=<hex> vbat=<mV> i2c=<...>`. Today it reports `ads=1` whatever the ID is, and over BLE that string is the only thing visible on battery.
2. **Bench flag.** A second PlatformIO environment `xiao_esp32s3_bench` with `-D BENCH_NO_INTERLOCK`. With it, USB_SENSE is ignored and the ADS1299 starts on USB. It prints at boot and puts in the status string: `BENCH BUILD: interlock ignored, not for use on a person`. The default environment is unchanged.
3. **Hardware reset (only if step E was done).** `#define ADS_RESET_PIN 9`. Pulse it open-drain: `pinMode(9, OUTPUT_OPEN_DRAIN)`, low for ≥ 10 µs (datasheet minimum is 2 clock periods), then `pinMode(9, INPUT)`, wait ≥ 1 ms (minimum 18 clock periods). Keep the RESET command after it. The pin is an input at boot and whenever USB is present; never drive it high. Do not pass it to the library if the library would drive it push-pull.
4. **Leave alone:** register values, gain, sample rate, packet format, BLE UUIDs, the USB ISR.
5. Build both environments with the runner (`fw` option). Record the result in `firmware/build-log.txt`. 0 errors and 0 warnings, as now.

### Step H. BOM and assembly data

1. `scripts/jlcbom.py` output must include R43–R47 with `MPN` and `LCSC` fields. Candidate JLCPCB basic parts, **from memory, verify each on its JLCPCB part page before writing it in**: 330 Ω 0603 C23138, 4.7 kΩ 0603 C23162. Also assign the still-missing LCSC numbers CHANGES.md lists (100 k, 150 k, 220 k, 10 k, 100 nF 0603, Q1).
2. Mark as not assembled by JLCPCB: U6 (XIAO), J1, J6, J7, J10–J19, JP1, TP1.
3. Add `pcb/neuryo-rev-b/ASSEMBLY.md`, short:
   - XIAO: solder the castellations with an iron, then BAT+ and BAT− through their holes from the back. Pad 25 may stay unsoldered.
   - Bench board: remove Q1, flash the bench build, inputs shorted or on a signal generator, never on a person.
   - Battery: check lead polarity against the "+" mark with a multimeter before the first plug-in; the board has no reverse-polarity protection.
   - Electrodes go on the "−" hole of channels 1–7; leave the "+" holes of channels 1–7 and J10 pin 2 (GND) empty.
   - Antenna: fix the XIAO's antenna at the rear of the pod, away from the electrode leads.
   - USB is never plugged in while the headset is worn. The interlock stops recording; it does not isolate the wearer.

### Step I. Documents

1. `CHANGES.md`: new section "4th pass (10 Nov)" with one row per step done or skipped, in the existing table format (change, why, source, status). Update the final pin map (D10 = ADS_RESET if step E was done).
2. Correct one existing statement: CHANGES.md B13 says 15 teardrop zones were removed. The committed rev B board has **no** teardrop zones at all; the baseline import has 417. They were lost at the first rev B save. This is cosmetic (no connection depends on them). State it; do not try to restore them.
3. Add a warning to `pcb/README.md` under the reference folder: the upstream `Production_Files/NC Drill` files are offset from the Gerbers (round holes span x 63.8–159.05 mm on a 100 mm board), so that folder must not be ordered as it is.
4. `REVIEW-CHECKLIST.md`: add the bench checks from section 4 below, and remove items this pass closes (series resistors, pull-ups).
5. `pcb/README.md` status line and the root `README.md` PCB line: "4th pass, 10 Nov".

---

## 3. Checks after every step

Run through the runner with `img refill`, then:

| Check | Pass condition |
|---|---|
| ERC | Still exactly 1 error (U1 PGOOD on GND meeting the GND PWR_FLAG). No new warning types |
| DRC | 0 unconnected. Errors only the 11 malformed courtyards and the 1 zero-length track crossing at (26.25, 22.25) that the import has. No new clearance, hole or silk item |
| Schematic parity | Board and schematic agree pin for pin (`scripts/netdiff.py`; net-name "conflicts" from the import are expected) |
| Netlist diff vs previous step | Only what the step says |
| Copper diff vs previous step (`scripts/copperdiff.py`) | Nothing at x < 56 except step E's trace and via |
| Renders | Look at `top.png` and `bottom.png`: new parts where intended, no silk on pads |

### Final check: Gerbers against the upstream board
After the last step, export a fab set (`fab` option) and compare the analog half with the upstream Gerbers in `pcb/low-cost-eeg/Production_Files/Gerber/`. Upstream (x, y) maps to rev B Gerber (x + 98.5, y − 130.0). This is the check that proved the import on 10 Nov; it must still pass.

```python
# pip install gerbonara cairosvg scipy pillow numpy
import io, numpy as np, cairosvg
from gerbonara import GerberFile
from gerbonara.utils import MM
from scipy import ndimage as ndi
from PIL import Image
O = 'pcb/low-cost-eeg/Production_Files/Gerber/ADS ESP EEG.'
R = '<fab folder>/Neuryo_RevB-'
PAIRS = [('GTL','Top Layer.gtl'), ('G1','GND Layer.g1'), ('G2','Power Layer.g2'), ('GBL','Bottom Layer.gbl'),
         ('GTS','Top Solder.gts'), ('GBS','Bottom Solder.gbs'), ('GTP','Top Paste.gtp'), ('GBP','Bottom Paste.gbp')]
def raster(path, bounds, ppm=40):
    (x0, y0), (x1, y1) = bounds
    svg = str(GerberFile.open(path).to_svg(arg_unit=MM, svg_unit=MM, force_bounds=bounds, fg='black', bg='white'))
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=int((x1-x0)*ppm), output_height=int((y1-y0)*ppm),
                           background_color='white')
    return np.array(Image.open(io.BytesIO(png)).convert('L')) < 128
for a, b in PAIRS:
    o = raster(O + a, ((0, 0), (56, 50)))
    r = raster(R + b, ((98.5, -130), (154.5, -80)))
    h, w = min(o.shape[0], r.shape[0]), min(o.shape[1], r.shape[1])
    diff = ndi.binary_opening(o[:h, :w] ^ r[:h, :w], iterations=2)   # drops sub-pixel edge noise
    lab, n = ndi.label(diff)
    print(a, 'different regions:', n)          # then list each region's centre and size and explain it
```

Expected on 10 Nov, before this pass: bottom paste identical; inner layers differ only at the removed ESP32-side vias and plane edge near x 48–56; top copper differs only by the ground pour filling the removed SRB1 trace, the missing teardrops, and the boundary at x > 52. After this pass, the only new difference at x < 56 is step E's trace and via. Explain every other region or treat it as a fault.

---

## 4. What the owner must do before paying (put in REVIEW-CHECKLIST.md; not for the implementer to do)

1. **XIAO 5V pin on battery.** Power a bare XIAO from a cell on its BAT pads, no USB, and measure the 5V pin. It must read about 0 V. The interlock depends on this (Seeed's wiki says the pin has no voltage on battery).
2. **Paper fit.** Print the top layer 1:1 and lay the XIAO, the JST-PH socket and the PCM12 switch on it.
3. **JLCPCB placement preview.** Check pin 1 of U4 (ADS1299), U1, U3 and D1–D5 against the silkscreen dot. These footprints came from Altium, so their zero rotation may not match JLCPCB's. Ask for placement confirmation before production.
4. **MAX30102 module.** Measure what voltage its SDA/SCL pull-ups go to. If 1.8 V, remove them from the module.
5. **Professor review** of the checklist, as already planned.

---

## 5. Report back

When done, write a short summary for the owner:
- each step: done or skipped, and why if skipped;
- the final ERC and DRC counts and the netlist diff against the 3rd-pass netlist;
- the Gerber comparison result, with every region at x < 56 explained;
- anything still Unverified.

Then stop. The result goes back for one more independent review before any order.
