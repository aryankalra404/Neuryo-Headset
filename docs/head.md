# Shared mannequin head

Every design uses the same head, so designs can be compared fairly and new versions don't need to re-measure anything.

Files: `designs/shared/head/head.glb` (mesh) and `designs/shared/head/head.json` (sites, skull surface, ear and earlobe data).

## What it is
- **Mesh:** MakeHuman 1.x base mesh, released under CC0 1.0 (no credit required). Head, ears, eyes, neck and shoulders, smoothed once, then cut flat at the chest and shoulders.
- **Size:** scaled to a **540 mm** head circumference, the mid-point of Indian adult male (548 mm) and female (532 mm) means (Neuryo-Research P190). Nasion to inion 324.2 mm; ear to ear over Cz 355.4 mm.
- **Frame:** millimetres; y up, face toward +z, wearer's left = +x. `az` is the angle round the head from the front (left is +), `el` is the angle up from the head centre.

## How the sites were measured
10-10 sites measured on the skull surface (ears masked out): nasion-inion midline arc in 10% steps; preauricular-Cz-preauricular arc for T7/T8; Fpz-T7-Oz circumference in 10% steps; each lateral row (AF, F, FC, C, CP, P, PO) as an arc from its left circumference point through its midline point to the right one, in equal steps; Nz-preauricular-Iz ring for the 9/10 row. Inion is not visible on this smooth mannequin and is taken on the back midline at nasion height + 5 mm.

The skull surface the sites sit on has the ears masked out and filled, so parts sit on the skull, not on the ear.

## Using it in a new design
1. In the design page, load `../shared/head/head.json` and `../shared/head/head.glb` (copy them from `designs/v2/index.html`).
2. Pick sites by name: `HEAD.sites.F3`, `HEAD.sites.Pz`, and so on, or the adjusted ones in `HEAD.extra`.
3. `surf(az, el)` gives the point and the outward normal on the skull at any spot.
4. The **All sites** button in v2 shows every position below on the head.

To change the head (another size, a female or male head), edit and re-run the scripts in `tools/` (order: `prep1.py`, `prep2.py`, `prep3.py`, `smooth.py`, `prep4.py`, `all1010.py`, `export.py <out folder>`, then `mastoid.py --write` to add M1/M2 again). They need Python with `trimesh`, `numpy`, `scipy`, `rtree`, `shapely`, `manifold3d`, and the MakeHuman `base.obj` in the working folder.

## Standard 10-10 sites (77)
| Site | az (°) | el (°) | x, y, z (mm) |
|---|---|---|---|
| Nz | 0.0 | 4.8 | 0.0, 6.6, 79.2 |
| Fpz | 360.0 | 25.8 | -0.0, 38.9, 80.6 |
| Fp1 | 18.2 | 20.9 | 24.8, 30.2, 75.1 |
| Fp2 | 341.8 | 20.9 | -24.8, 30.2, 75.1 |
| AFz | 360.0 | 44.9 | -0.0, 69.1, 69.3 |
| AF3 | 24.7 | 36.3 | 30.7, 53.8, 66.7 |
| AF4 | 335.3 | 36.2 | -30.7, 53.8, 66.7 |
| AF7 | 37.3 | 16.5 | 46.6, 22.8, 61.3 |
| AF8 | 322.8 | 16.5 | -46.6, 22.8, 61.3 |
| Fz | 360.0 | 62.4 | -0.0, 94.6, 49.5 |
| F1 | 28.4 | 57.9 | 26.3, 87.9, 48.5 |
| F2 | 331.5 | 57.8 | -26.3, 87.9, 48.5 |
| F3 | 45.2 | 46.9 | 46.3, 69.9, 46.1 |
| F4 | 314.8 | 46.9 | -46.4, 69.9, 46.1 |
| F5 | 53.3 | 32.4 | 57.3, 45.3, 42.7 |
| F6 | 306.7 | 32.4 | -57.3, 45.3, 42.7 |
| F7 | 57.2 | 14.4 | 60.6, 18.5, 39.0 |
| F8 | 302.8 | 14.3 | -60.6, 18.4, 39.0 |
| F9 | 53.9 | -12.9 | 60.4, -17.1, 44.0 |
| F10 | 306.1 | -12.9 | -60.4, -17.1, 44.0 |
| FCz | 0.0 | 79.0 | 0.0, 110.7, 21.5 |
| FC1 | 57.3 | 69.6 | 32.5, 103.8, 20.9 |
| FC2 | 302.6 | 69.5 | -32.7, 103.7, 20.9 |
| FC3 | 71.6 | 53.7 | 56.7, 81.4, 18.8 |
| FC4 | 288.4 | 53.6 | -56.8, 81.3, 18.9 |
| FC5 | 76.7 | 35.7 | 67.7, 50.1, 16.0 |
| FC6 | 283.3 | 35.6 | -67.7, 49.9, 16.0 |
| FT7 | 79.1 | 13.6 | 67.6, 16.7, 13.0 |
| FT8 | 280.9 | 13.6 | -67.6, 16.6, 13.0 |
| FT9 | 75.0 | -15.3 | 66.7, -19.0, 17.9 |
| FT10 | 285.0 | -15.3 | -66.7, -19.0, 17.9 |
| Cz | 180.0 | 85.0 | 0.0, 116.2, -10.1 |
| C1 | 105.8 | 71.8 | 34.5, 109.1, -9.7 |
| C2 | 254.3 | 71.8 | -34.6, 109.1, -9.7 |
| C3 | 98.0 | 54.6 | 59.7, 84.8, -8.4 |
| C4 | 262.0 | 54.5 | -59.7, 84.7, -8.4 |
| C5 | 95.3 | 35.8 | 71.2, 51.6, -6.6 |
| C6 | 264.7 | 35.7 | -71.2, 51.4, -6.6 |
| T7 | 93.8 | 12.8 | 70.6, 16.1, -4.7 |
| T8 | 266.2 | 12.8 | -70.6, 16.0, -4.7 |
| T9 | 92.3 | -15.7 | 69.1, -19.4, -2.8 |
| T10 | 267.7 | -15.7 | -69.1, -19.4, -2.8 |
| LPA | 92.3 | -15.7 | 69.1, -19.4, -2.8 |
| RPA | 267.7 | -15.7 | -69.1, -19.4, -2.8 |
| CPz | 180.0 | 69.4 | 0.0, 112.3, -42.2 |
| CP1 | 141.9 | 63.2 | 32.9, 105.6, -42.0 |
| CP2 | 218.1 | 63.1 | -33.0, 105.5, -42.0 |
| CP3 | 126.1 | 49.5 | 57.0, 82.6, -41.7 |
| CP4 | 233.9 | 49.4 | -57.1, 82.5, -41.6 |
| CP5 | 120.9 | 32.5 | 68.6, 51.0, -41.1 |
| CP6 | 239.1 | 32.5 | -68.6, 51.0, -41.1 |
| TP7 | 120.2 | 12.1 | 69.7, 17.4, -40.6 |
| TP8 | 239.8 | 12.1 | -69.7, 17.3, -40.5 |
| TP9 | 118.6 | -12.7 | 63.9, -16.4, -34.8 |
| TP10 | 241.4 | -12.7 | -63.9, -16.4, -34.8 |
| Pz | 180.0 | 54.1 | 0.0, 98.2, -71.1 |
| P1 | 158.6 | 50.8 | 27.7, 93.2, -70.7 |
| P2 | 201.5 | 50.8 | -27.9, 93.2, -70.7 |
| P3 | 144.6 | 41.7 | 49.5, 75.9, -69.5 |
| P4 | 215.5 | 41.6 | -49.5, 75.8, -69.5 |
| P5 | 139.0 | 28.8 | 58.9, 49.4, -67.7 |
| P6 | 221.0 | 28.8 | -58.9, 49.2, -67.6 |
| P7 | 137.2 | 13.3 | 60.8, 21.2, -65.7 |
| P8 | 222.8 | 13.3 | -60.8, 21.1, -65.7 |
| P9 | 137.1 | -8.6 | 55.7, -12.4, -60.0 |
| P10 | 222.9 | -8.6 | -55.7, -12.4, -60.0 |
| POz | 180.0 | 38.7 | 0.0, 74.1, -92.7 |
| PO3 | 159.1 | 32.3 | 35.0, 62.0, -91.4 |
| PO4 | 201.0 | 32.3 | -35.1, 61.9, -91.4 |
| PO7 | 152.1 | 15.1 | 46.5, 26.9, -87.8 |
| PO8 | 207.9 | 15.1 | -46.5, 26.8, -87.8 |
| PO9 | 152.5 | -4.1 | 43.4, -6.8, -83.2 |
| PO10 | 207.5 | -4.1 | -43.4, -6.8, -83.2 |
| Oz | 180.0 | 22.9 | 0.0, 43.8, -103.4 |
| O1 | 166.0 | 18.4 | 25.3, 34.8, -101.6 |
| O2 | 194.0 | 18.4 | -25.3, 34.7, -101.6 |
| Iz | 180.0 | 6.2 | 0.0, 11.5, -104.6 |

## Adjusted and extra sites
| Name | az (°) | el (°) | x, y, z (mm) | Note |
|---|---|---|---|---|
| TP9_clear | 126.9 | -11.1 | 60.8, -14.9, -45.7 | TP9 moved 15 mm back along its ring so a 9 mm pad clears this mannequin's ear. |
| TP10_clear | 233.1 | -11.1 | -60.8, -14.9, -45.7 | Mirror of TP9_clear. |
| EOG_L | 27.3 | -16.3 | 36.1, -22.9, 69.7 | About 20 mm below the centre of the left eye (vertical EOG). |
| EOG_R | 332.7 | -16.3 | -36.1, -22.9, 69.7 | About 20 mm below the centre of the right eye. |
| M1 | 129.8 | -21.6 | 55.6, -28.6, -46.3 | Left mastoid bone, halfway between ear-canal and earlobe height, 16 mm behind the back edge of the ear so a 25 mm wide pad clears it (`tools/mastoid.py`). Used by v3. |
| M2 | 230.2 | -21.6 | -55.6, -28.6, -46.3 | Mirror of M1. |

## Eyebrow line
`HEAD.browY` is the height of the eyebrow line (about 16 mm above the eye centres, `HEAD.eyes`). Both designs keep the front module's lower edge 1 degree above it, so it never covers the eyes. On this head Fp1 sits about 30 mm and AF7 about 22 mm above the eye centre, i.e. just above the eyebrow, as on a real head.

## Limits
- One average head. Real heads vary; the plan calls for a fitted frame covering about 500 to 580 mm (D19).
- The inion is estimated (see method). TP9/TP10 in the standard table sit under this mannequin's ear overhang; v2 uses `TP9_clear` / `TP10_clear`; v3 uses the mastoid-bone points `M1` / `M2`.
- No hair is modelled.
