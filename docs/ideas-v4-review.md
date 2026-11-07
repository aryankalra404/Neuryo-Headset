# Ideas from the 7 Nov v4 review

**Status:** ideas only, not decisions.

**Read with v4.4 in mind.** This review looked at v4.1. Since then: the rigid spine became a band printed in the head's curve that lies on the head, with size holes 1–9 (v4.2–v4.4), which answers section 2's height and bending problems a different way than threaded carriages; the 1 ml reservoir and refill port were dropped for a damp foam tip plus 2–4 drops when the app asks (v4.3–v4.4); the frame test now covers 10+ heads from 500 to 580 mm with oiled, thick and short hair; and in v5 the board moves from the brow module to a side box, so the weight split in section 4 changes. Section 6's budget line is out of date: see the 7 Nov buy plan. The rest (hair parting, sealed prints, stainless parts near saline, weighing the frame) still applies.

Nothing here changes v4 until it is tested or turned into a decision in `00-decisions.md`. Numbers marked *estimate* are rough calculations, not measurements.

Source: a review of v4.1 (`docs/v4.md`, `designs/v4/`) against the Neuryo-Research library on 7 Nov 2026. Codes like D21 or C71 point to that library.

## 1. Hair electrodes (Fz, Cz, Pz)

**Semi-dry with a small reservoir looks right. Keep it.**
- Semi-dry stayed under 40 kΩ for 5 h through hair [P29]; 1 ml saline kept under 6 kΩ for 4 h [L05]; r 0.96 vs wet [L05]. Up to 40 kΩ does not change band amplitude with a high-impedance amplifier [L53].
- Dry raises delta and theta and loses more data [L19, L02, D30]; paste needs a hair wash; a plain sponge dries in about 20 min [L37, D21]. Chair time is about 12 min, close to that, so keep the reservoir.
- No mid-session refill is needed. The pod is wetted once at setup.

**Ideas**
- Drop the refill port. Fill the cup with a 1 ml blunt syringe before lowering the pod. One less leak path.
- Add "part the hair under each pod" to the session steps. Combing the scalp before placement lowered impedance [L50].
- Fill to "foam damp", not dripping, so saline does not run through the hair between sites.
- Use stainless springs and screws near the pods (saline).
- FDM prints leak water between layers. Print the cup at 100% infill with 4+ walls, or seal the inside with epoxy.
- Print plunger sleeves standing upright so the bore comes out round (keep the 14.4 / 14.6 / 14.8 mm test prints).

Still unknown: oiled and thick Indian hair (no data in the library). Study 1 item 2 covers it.

## 2. Midline spine: keep it, but fix height

**The spine is the simplest frame for these three sites.** Fz, Cz and Pz all sit on the midline (30, 50, 70% of nasion to inion), so one arc is the minimum structure. Other headsets need more because they have more sites: Ultracortex uses a full printed shell in S/M/L with spring holders twisted into nodes [C71]; Zeto a semi-rigid PA12 frame [C72]; UB ERP a cap [C03]; Cumulus an adjustable shell [C02]. A cap would bring back fabric (D34).

**Problem 1: height across head sizes (estimate).** The halo fits 52 to 64 cm and the carriages slide, but scalp height under a fixed-shape spine changes with head size. Scaling the shared head from 52 to 62 cm moves the scalp at Cz by roughly 10 mm or more relative to the spine. Spring travel is about 6 mm, so pods may not reach on small heads and may bottom out on large ones.

**Problem 2: spine bending (estimate).** Three springs at about 1.4 N push up with about 4.2 N. The spine is 16 × 4.5 mm and the load bends it through the 4.5 mm side. A straight-beam estimate (PETG, 200 to 250 mm span) gives 3 to 6 mm at Cz, about the same as the spring travel. The real arch and its end mounts will change this.

**Ideas**
- **Threaded carriages (from Ultracortex [C71]).** Each carriage is a threaded sleeve; the pod screws down about 15 to 20 mm until it touches, then one more turn, with the spring giving the last few mm of force. This removes both problems above and keeps the slide, the single spine and the bought halo. Coarse threads print fine (Ultracortex prints PLA at 0.2 mm layers [C71]).
- **Deeper spine.** Make it about 8 to 10 mm deep toward the head, or add a rib. Twice the depth is about 8× stiffer for a few grams.
- **Print the spine on its edge**, with the arc flat on the bed, so layers run along its length.
- **Setting positions:** measure nasion to inion with a tape, put Cz at the vertex, set Fz and Pz 20% of that length in front of and behind it. Mark the spine in % of nasion to inion.

## 3. Frame test (Study 0) additions
- Test on three heads, not one: small (about 52 cm), large (about 60 cm), and oiled thick hair.
- At each, check the pods reach the scalp, stay upright, and press with similar force at Fz, Cz and Pz.
- Check the headband does not ride up the forehead when all three pods press down.
- Weigh the frame.

## 4. Weight (estimate, nothing weighed yet)
| Part | Rough grams |
|---|---|
| PN521 headband and ratchet (shell and cradle removed) | 60–100 |
| Brow module shell + board | 25–35 |
| Spine + joint | 25–35 |
| 3 pods with carriages, electrodes, springs, foam | 35–45 |
| Saline (1 ml per pod) | 3 |
| 1000 mAh battery (about 19 g) + battery pod | 25–30 |
| Leads, earlobe clip, pads, lining, screws | 45–60 |
| **Total** | **about 230–320** |

For comparison: the whole PN521 helmet with its shell is listed at 300 g by Karam and 340–360 g on ToolBuy; the Neurosity Crown is 228 g; the library has DSI-24 at about 600 g (not verified). For a 12-min session this looks fine. Board at the front and battery at the back keep it balanced. The saline adds almost no weight; leaks matter, weight does not.

## 5. Buildability, hardest first
1. ADS1299 board: 4-layer, low noise, under 6 µVpp. Get the JLCPCB quote and part stock early. If VIT has a ready-made 8-channel ADS1299 board, borrow it for Study 1 while ours is made.
2. Saline pods: no leaks, foam stays wet.
3. Spine height and stiffness (section 2).
4. The frame itself: easy (bought halo, printed parts, screws).

## 6. Doc wording to fix
- The project plan's one-line summary says a "6-minute" check; v4 says a 5-minute recording in about 12 min of chair time.
- The plan lists "plain water or saline sponges" under "Not used" while v4 calls the hair contacts "saline pods". D21 rules out plain sponges, not saline-fed reservoirs. Say "semi-dry reservoir pods" everywhere.
- The prototype budget (₹42,555 + ₹7,445 reserve) is exactly the ₹50,000 SSV grant, with no margin.
