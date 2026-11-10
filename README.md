# Neuryo Headset

Interactive 3D models of the Neuryo EEG + heart-rate headset. Each design is its own model; the start page lists them and lets you switch between them.

**Open it:** https://aryankalra404.github.io/Neuryo-Headset/

| Design | What it is | Direct link |
|---|---|---|
| v1 · 26 Oct design | 4 channels: AF7, AF8, Fz, Pz. TP9 + TP10 linked reference, Fpz ground, saline sponge pods, forehead heart sensor. Has AR and try-on. | https://aryankalra404.github.io/Neuryo-Headset/designs/v1/ |
| v2 · 29 Oct research plan | 6 channels: Fp1, Fp2, Fz, Pz, TP10, eye (VEOG). TP9 reference alone, Fpz bias, hydrogel on the forehead, semi-dry pods in hair, earlobe heart-sensor clip. Built from the Neuryo-Research library (decisions D01 to D28) on the shared realistic head. Superseded by v3. | https://aryankalra404.github.io/Neuryo-Headset/designs/v2/ |
| v3 · 29 Oct review | Superseded by v4. 6 channels on the head (Fp1, Fp2, Fz, Pz, M2, eye) on an 8-channel ADS1299 at gain 12. M1 mastoid-bone reference on SRB2, Fpz bias. One 4 mm snap socket per site with swappable inserts: paste on the forehead, semi-dry pods in hair. **Test kit** toggle adds ECG on channel 7 and dry comparison inserts; **Confidence** colours each part by how sure the plan is. | https://aryankalra404.github.io/Neuryo-Headset/designs/v3/ |
| v4 · 7 Nov product design | Superseded by v6, which keeps its midline band and carriages. Was the launch design (v4.4). A 5-minute in-clinic recording at baseline, day 7 and every visit of a depression treatment course. 7 channels on the head (Fp1, Fp2, Fz, Cz, Pz, M2, eye), M1 reference, Fpz bias. Single-use 3-pad hydrogel forehead strip placed by a nasion template, earlobe heart clip, BMI270, 1000 mAh at the back. Buildable frame for 500–580 mm circumference and 300–390 mm nasion–inion: bought hard-hat ratchet harness with a 3 mm lining or a 7 mm small-head insert; midline band 3D-printed already in the head's curve (PA12, PETG for fit tests) with a TPU tail through a cam lock; spring-loaded semi-dry pods pinned at one size number (1–9) read off a size tape; damp single-use foam tips (2–3 mm proud, set weight) topped up only when the app's wetting check asks; wipe-clean silicone lining. Main board (v4.5): about 70 × 50 mm in the brow module, the analog half copied from the open Low-Cost-EEG board plus a Seeed XIAO ESP32-S3. Page adds a 9-step **Session walkthrough**, head-size and nasion–inion sliders, a buy/print parts list and frame build steps, and a **Single-use vs reusable** overlay. | https://aryankalra404.github.io/Neuryo-Headset/designs/v4/ |
| v5 · arch concept (v5.2) | Superseded by v6. Same electronics and sites as v4.5, new frame: spring arch over Cz, main board in a pod above the left ear and battery above the right, temple arms to soft pads, rear band with a hook under the occiput and a dial. v5.2 (8 Nov): Fz, Cz and Pz in spring carriages on a rigid spine clipped to the arch at Cz, one soft spring per pod. Forehead bare apart from the strip. | https://aryankalra404.github.io/Neuryo-Headset/designs/v5/ |
| v6 · 8 Nov head ring + v4 midline | Lead design. v4's midline band lying on the head with a spring carriage per pod (one size number 1–9 sets Fz and Pz from Fpz), held between a small front anchor (about 34 × 34 × 7.5 mm, replacing v4's brow module) and a cam lock above the rear dial. Head ring: a front band across the forehead above the strip and v5's rear band with a hook under the occiput and a dial. Board in a pod above the left ear, battery above the right. Real windows in the band and real lead slots in the carriages. v6.1 (9 Nov): the real rev B board from KiCad (77 × 50 mm), pods resized to about 98 × 77 × 22 mm. v6.2 (10 Nov): carriages wrap the rails and click into size notches, rails 3 mm thick beside the windows, Cz pod moved to the test kit (6 channels on the product headset). | https://aryankalra404.github.io/Neuryo-Headset/designs/v6/ |
| Ultracortex pod adapter · 8 Nov | Test rig part: holds a Neuryo pod in an OpenBCI Ultracortex Mark IV frame node at Fz, Cz or Pz to test a rigid frame with a spring per pod. Four STL print files plus the generator `tools/uc_adapter.py`. | https://aryankalra404.github.io/Neuryo-Headset/designs/uc-adapter/ |

Add `#v1` to `#v6` to the start page link to open a design straight away.

**Docs:** [docs/](docs/README.md): one file per design ([v1](docs/v1.md), [v2](docs/v2.md), [v3](docs/v3.md), [v4](docs/v4.md), [v5](docs/v5.md), [v6](docs/v6.md), each with why it changed from the one before) and the [shared head](docs/head.md) with all 77 measured 10-10 positions plus the mastoid points M1/M2.

**PCB:** [pcb/](pcb/README.md): rev B in KiCad 10 (77 × 50 mm: Low-Cost-EEG's analog half + a XIAO ESP32-S3, final pin map, ERC/DRC/netlist checks, firmware) and the Low-Cost-EEG reference design it copies (Altium project, Gerbers, schematic, report; GPL-3.0). Laid out, waiting for professor review, not ordered. Rev A (30 Oct, made for v3) is in the git history.

## Adding a new design
1. Copy the latest design folder, for example `designs/v5/` to `designs/v6/`, and change the model in `designs/v6/index.html`. It already loads the shared head from `designs/shared/head/`; pick electrode sites by name (`HEAD.sites.F3`, `HEAD.extra.M1` and so on, see [docs/head.md](docs/head.md)).
2. Add an entry to `designs/designs.json` with its `id`, `name`, `date`, `path`, `channels`, `summary` and `status`.
3. Add `docs/v6.md` with its spec and what changed from v5, and why.

The new design then shows up on the start page and in the switcher.

## Using it on Meta Quest 3S (v1)
1. Open https://aryankalra404.github.io/Neuryo-Headset/designs/v1/ in the **Meta Quest Browser**.
2. Tap **View in AR** and allow the permission prompt.
3. Pinch the headset to lift it off the mannequin, or pinch an electrode pod to pull it out on its own. Pinch empty space to move everything. Reset on the panel puts parts back.
   Right stick: explode. Left stick: turn and resize. Use the floating panel for Inside, Electronics only, Labels and Head.

AR is tested on v1 only. v3 and v4 show a **View in AR** button on headsets that support WebXR, but it has not been tested on the Quest yet. Try-on is v1 only.

## Try it on (webcam or phone)
v6: https://aryankalra404.github.io/Neuryo-Headset/designs/v6/tryon.html (or **Try it on** on the v6 page). v1: the link below.

### v1
Open https://aryankalra404.github.io/Neuryo-Headset/tryon.html on a laptop or phone, press **Start camera** and face the camera. The headset locks onto your head at true size. Use Size / Up-down / Forward-back to fit it, **Show head guide** to check the fit, and **Take photo** to save a picture. Face tracking runs in the browser with Google MediaPipe; the video is not uploaded.

## In a normal browser
Rotate and zoom the model, see inside, open the **Electrode build** and **Board guide** walkthroughs, and check sources under **Details → Sources**.

v3 adds a Product / Test kit mode switch, a **Display** menu, **Copy link** (opens exactly what you are looking at), **Measure**, and two new Details tabs: **Build** (parts list, wiring, tests) and **Changes** (what moved since v2 and why). See [docs/v3.md](docs/v3.md#on-the-page).

v4 adds **Fit & finish** (head circumference 500–580 mm and nasion–inion 300–390 mm sliders that give the ratchet setting and lining, the strip height and the band size number 1–9; silicone lining vs the dropped knit idea; lining and shell colours), a **Session walkthrough** under Guides (G), a **Session** tab, **Channel numbers** (N) and a **Single-use vs reusable** overlay (U). See [docs/v4.md](docs/v4.md#on-the-page).

v1 is built from the 26 Oct design doc. v2 is built from the 29 Oct research plan; its module, board layout and battery are carried over from v1. Shapes and sizes neither source gives are marked as model estimates in the page. In v2, **All sites** shows every measured 10-10 position on the head.

## Shared head
`designs/shared/head/` holds the mannequin every design uses (v1 to v6): MakeHuman base mesh (CC0), 540 mm head circumference, sites measured with the 10-20 rules. The scripts in `tools/` rebuild it; see [docs/head.md](docs/head.md).
