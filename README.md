# Neuryo Headset

Interactive 3D models of the Neuryo EEG + heart-rate headset. Each design is its own model; the start page lists them and lets you switch between them.

**Open it:** https://aryankalra404.github.io/Neuryo-Headset/

| Design | What it is | Direct link |
|---|---|---|
| v1 · 26 Oct design | 4 channels: AF7, AF8, Fz, Pz. TP9 + TP10 linked reference, Fpz ground, saline sponge pods, forehead heart sensor. Has AR and try-on. | https://aryankalra404.github.io/Neuryo-Headset/designs/v1/ |
| v2 · 29 Oct research plan | 6 channels: Fp1, Fp2, Fz, Pz, TP10, eye (VEOG). TP9 reference alone, Fpz bias, hydrogel on the forehead, semi-dry pods in hair, earlobe heart-sensor clip. Built from the Neuryo-Research library (00-montage-options.md, decisions D01 to D28). | https://aryankalra404.github.io/Neuryo-Headset/designs/v2/ |

Add `#v1` or `#v2` to the start page link to open a design straight away.

## Adding a new design
1. Copy the latest design folder, for example `designs/v2/` to `designs/v3/`, and change the model in `designs/v3/index.html`.
2. Add an entry to `designs/designs.json` with its `id`, `name`, `date`, `path`, `channels`, `summary` and `status`.

The new design then shows up on the start page and in the switcher.

## Using it on Meta Quest 3S (v1)
1. Open https://aryankalra404.github.io/Neuryo-Headset/designs/v1/ in the **Meta Quest Browser**.
2. Tap **View in AR** and allow the permission prompt.
3. Pinch the headset to lift it off the mannequin, or pinch an electrode pod to pull it out on its own. Pinch empty space to move everything. Reset on the panel puts parts back.
   Right stick: explode. Left stick: turn and resize. Use the floating panel for Inside, Electronics only, Labels and Head.

AR and try-on are not set up for v2 yet.

## Try it on (v1, webcam or phone)
Open https://aryankalra404.github.io/Neuryo-Headset/tryon.html on a laptop or phone, press **Start camera** and face the camera. The headset locks onto your head at true size. Use Size / Up-down / Forward-back to fit it, **Show head guide** to check the fit, and **Take photo** to save a picture. Face tracking runs in the browser with Google MediaPipe; the video is not uploaded.

## In a normal browser
Rotate and zoom the model, see inside, open the **Electrode build** and **Board guide** walkthroughs, and check sources under **Details → Sources**.

v1 is built from the 26 Oct design doc. v2 is built from the 29 Oct research plan; its module, board layout and battery are carried over from v1. Shapes and sizes neither source gives are marked as model estimates in the page.
