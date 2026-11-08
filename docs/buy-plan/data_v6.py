# Neuryo v6 buy plan data (9 Nov 2026). price = INR incl. GST.
# seen: '9 Nov' = read on the seller page on 9 Nov; '7 Nov' / '8 Nov' = read then (v4.4 / v5.2 plans, not re-read); 'est' = estimate.
RATE_MID = 94.05            # x-rates, 7 Nov 2026 16:25 UTC (carried over)
CARD = round(RATE_MID * 1.035, 2)   # ~3.5% card markup
AZ = 'https://www.amazon.in/dp/'
orders = [
 dict(store='Upside Down Labs', note='Free delivery above ₹999 (store page).', items=[
  ('UDL colour snap cables, pack of 10 (100 cm, snap one end)', '11 leads: Fp1, Fp2, Fpz bias, eye, M1, M2, Fz, Cz, Pz + 2 ECG; cut the plug end and solder into the board holes', 2, 1999, 'https://store.upsidedownlabs.tech/product/different-color-snap-cables-pack-of-10/', '9 Nov', ''),
  ('UDL Neo Gel electrodes, 100 pcs (3.2 × 2.5 cm)', 'Forehead pads (Fp1, Fpz, Fp2), M1, M2, eye pad, ECG pair', 1, 799, 'https://store.upsidedownlabs.tech/product/neo-gel-electrodes/', '9 Nov', ''),
 ]),
 dict(store='Robu', note='XIAO in stock on 9 Nov (Robu search page). Filament: skip if the VIT printer room has it.', items=[
  ('Seeed Studio XIAO ESP32S3 (plain, not Sense/Plus)', '1 for bench firmware now + 1 per board (rev B footprint is the plain XIAO)', 3, 1139, 'https://robu.in/product/seeed-studio-xiao-esp32s3-2-4ghz-wifi-ble-5-0/', '9 Nov', ''),
  ('PETG 1.75 mm, 1 kg', 'Pods, midline band (fit tests), carriages, anchor, cam lock, ear clip', 1, 780, 'https://robu.in/product/numaker-petg-hs-1-75mm-blue-translucent-filament/', '7 Nov', 'skip'),
  ('TPU 95A 1.75 mm, 1 kg', 'Midline band tail through the cam lock (v6 needs it); linings can be the silicone sheet', 1, 2149, '', 'est', 'skip'),
 ]),
 dict(store='Probots', note='₹99 flat shipping under ₹4,999 (7 Nov plan). Only in-stock protected cell on 9 Nov.', items=[
  ('Li-ion 3.7 V 950 mAh YB-503450, protected (50 × 34 × 5 mm)', '1 per board + 1 spare; its plug is listed as 3-pin 1.25 mm, so fit the 2 mm JST lead below', 3, 399, 'https://probots.co.in/lithium-ion-rechargeable-battery-3-7v-950mah-yb-503450.html', '9 Nov', ''),
  ('TP4056 1 A charger module, Type-C, with DW01 protection', 'Rev B review change 3: charge the cells outside the headset', 2, 49, 'https://probots.co.in/tp4056-1a-li-ion-lithium-battery-charging-module-with-current-protection-type-c.html', '9 Nov', ''),
  ('GY-MAX30102 pulse sensor', 'Earlobe clip + spare; check the I²C pull-ups go to 3.3 V', 2, 199, 'https://probots.co.in/search/max30102', '9 Nov', ''),
  ('USB logic analyzer, 24 MHz, 8 ch', 'Debug the ADS1299 SPI and the USB interlock at bring-up', 1, 449, 'https://probots.co.in/search/logic%20analyzer%208%20channel', '9 Nov', ''),
  ('Probots shipping', '', 1, 99, '', '7 Nov', ''),
 ]),
 dict(store='Vishaworld', note='Shipping shown at checkout.', items=[
  ('7Semi BMI270 Nano IMU (Qwiic)', 'Rev B: breakout on a 4-wire lead to J7, 1 per board', 2, 501, 'https://vishaworld.com/search?q=bmi270', '9 Nov', ''),
 ]),
 dict(store='Robocraze', note='Free delivery from ₹999; this order is small, so add it to another Robocraze order or expect a delivery fee.', items=[
  ('2 mm pitch 2-pin JST cable with connector, pack of 10', 'Battery leads into J1 (JST-PH 2.0); check polarity against the "+" on the board', 1, 55, 'https://robocraze.com/search?q=jst+ph+2.0+2+pin', '9 Nov', ''),
 ]),
 dict(store='Amazon.in', note='Delivery depends on the seller.', items=[
  ('Stainless compression spring assortment', 'Pod springs, about 1 N at 6 mm; pick on the scale', 1, 300, '', 'est', ''),
  ('OLEIO M3 × 12 mm screws with nuts', 'Anchor tongue, band splice, cam lock, pod shells (nuts in printed pockets)', 1, 289, AZ + 'B0HKJ7692J', '7 Nov', ''),
  ('Silicone rubber sheet 2 mm, 1 × 1 ft', 'Front band and midline linings, rear hook pad, pod linings', 1, 459, AZ + 'B0D243VWDB', '7 Nov', ''),
  ('Worison black foam sheets, A4 × 10', 'Light-blocking pad on the ear clip', 1, 175, AZ + 'B09G3BDXYL', '7 Nov', ''),
  ('Araldite Standard 90 g', 'Seal pod lids, strain relief on soldered leads', 1, 195, AZ + 'B01HS00QX0', '7 Nov', ''),
  ('Romsons alcohol swabs, 100', 'Skin prep', 1, 179, AZ + 'B0G653LQPL', '7 Nov', ''),
  ('PVA sponge, pack of 2', 'Cut into the pods’ foam tips', 1, 239, AZ + 'B0BRGG1LFY', '7 Nov', ''),
  ('Flat 6-core 28 AWG cable, 5 m', 'Ear-clip lead (4 wires into J6) and the BMI270 lead (J7)', 1, 140, AZ + 'B084V1TR88', '7 Nov', ''),
  ('2 mm steel dowel pins', 'Size-hole pins under the carriages’ right feet', 1, 200, '', 'est', ''),
  ('Breadboard, jumper wires, male headers', 'Bench firmware on the spare XIAO with the MAX30102 and BMI270', 1, 508, '', 'est', ''),
  ('IONIX 150 cm tailor tape', 'Head circumference, nasion–inion, size tape', 1, 99, AZ + 'B098R1VVWX', '7 Nov', ''),
  ('Weaver Ten20 paste, 228 g', 'Demo insurance: paste + a TDE-211 at Pz if the semi-dry pods are not ready for the review. Check seal and expiry', 1, 1890, '', '8 Nov', ''),
  ('ATOM pocket scale, 200 g × 0.01 g', 'Pod force (1 N ≈ 102 g) and spring picking', 1, 289, AZ + 'B06XMZV7RH', '7 Nov', 'skip'),
  ('Vinabo digital caliper 150 mm', 'Print fit, pad and spring sizes', 1, 399, AZ + 'B0BDLX8DWG', '7 Nov', 'skip'),
 ]),
 dict(store='ToolBuy', note='Dispatch in 2 business days.', items=[
  ('Karam PN521 ratchet helmet (harness only)', '1 to cut for the rear dial and straps, 1 spare (range not published: measure on arrival)', 2, 306, 'https://www.toolbuy.com/tp/karam-isi-marked-shelmet-ratchet-type-safety-helmet-with-plastic-cradle-red-pn521', '9 Nov', ''),
  ('ToolBuy shipping', '', 1, 100, '', 'est', ''),
 ]),
 dict(store='Chemist', note='', items=[
  ('0.9% saline + three 1 ml syringes (no needle)', 'Wetting the pod tips', 1, 60, '', 'est', ''),
 ]),
]
# FRI (import). Price shown in INR on FRI's own store on 9 Nov.
fri = dict(qty=6, each_inr=500, ship_inr=4400)   # DHL figure from the 29 Oct cart (shown only at checkout)
# JLCPCB, rev B, 2 boards, Standard PCBA double-sided (rev B has 28 parts on the bottom).
jlc = [  # (line, usd, seen, link)
 ('4-layer PCB, 1.6 mm, 77 × 50 mm, 5 pcs', 10.00, 'est', ''),
 ('Standard PCBA engineering fee, double-sided', 51.12, '9 Nov', 'https://jlcpcb.com/help/article/pcb-assembly-price'),
 ('Stencil, double-sided assembly', 16.42, '9 Nov', 'https://jlcpcb.com/help/article/pcb-assembly-price'),
 ('Component loading, about 29 SMT part types × $1.53', 44.37, 'est', 'https://jlcpcb.com/help/article/pcb-assembly-price'),
 ('SMT joints, about 1,040 × $0.0016', 1.66, 'est', 'https://jlcpcb.com/help/article/pcb-assembly-price'),
 ('ADS1299IPAGR × 2 at $70.817 (367 in stock)', 141.63, '9 Nov', 'https://jlcpcb.com/partdetail/TexasInstruments-ADS1299IPAGR/C476817'),
 ('LM27762DSSR × 2, TPS7A2033PDBVR × 2, TPD4E1B06DCKR × 10', 6.64, '7 Nov', 'https://jlcpcb.com/parts/componentSearch?searchTxt=LM27762DSSR'),
 ('0.1 % thin-film resistors, C0G caps, other passives, Q1, SW1 (bom-jlc.csv)', 15.00, 'est', ''),
 ('Shipping to India', 15.00, 'est', ''),
]
# Economic alternative: top side only, bottom 28 parts hand-soldered (not recommended)
jlc_econ_delta = -(51.12 - 8.18) - (16.42 - 1.53) - (44.37 - 14 * 3.07)   # setup, stencil, loading (about 14 extended parts at $3.07)
