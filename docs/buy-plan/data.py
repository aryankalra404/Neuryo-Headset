# Neuryo v5 buy plan data. price = INR incl. GST as read on 7 Nov 2026; est=True if not read on a seller page.
RATE_MID = 94.05            # x-rates, 7 Nov 2026 16:25 UTC
CARD = round(RATE_MID * 1.035, 2)   # ~3.5% card markup (7 Nov plan assumption)
AZ = 'https://www.amazon.in/dp/'
orders = [
 dict(store='Upside Down Labs', note='Free delivery above ₹999 (store page).', items=[
  ('UDL colour snap cables, pack of 10', 'Leads for 9 head sites + 2 ECG; cut the plug end and solder to the board', 2, 1999, 'https://store.upsidedownlabs.tech/product/different-color-snap-cables-pack-of-10/', False, ''),
  ('UDL Neo Gel electrodes, 100 pcs (3.2 × 2.5 cm)', 'Forehead strip pads (MVP), M1, M2, eye pad, ECG', 1, 799, 'https://store.upsidedownlabs.tech/product/neo-gel-electrodes/', False, ''),
 ]),
 dict(store='Robu', note='Free shipping above ₹499 (per GrabOn; confirm at checkout).', items=[
  ('Seeed Studio XIAO ESP32S3', 'One for bench firmware now, one soldered onto the board (replaces the ESP32-S3 DevKitC)', 2, 1139, 'https://robu.in/product/seeed-studio-xiao-esp32s3-2-4ghz-wifi-ble-5-0/', False, ''),
  ('Numakers PETG-HS 1.75 mm, 1 kg', 'Pods, bar, carriages, temple arms, rear band, ear clip', 1, 780, 'https://robu.in/product/numaker-petg-hs-1-75mm-blue-translucent-filament/', False, 'skip'),
 ]),
 dict(store='Robocraze', note='Free delivery on orders of ₹999 and above (shipping policy page); this order is ₹1,317.', items=[
  ('MAX30102 pulse sensor module', 'Earlobe clip + test-kit forehead window', 2, 249, 'https://robocraze.com/products/max30102-pulse-oximeter-heart-rate-sensor-module', False, ''),
  ('Witty Fox 3.7 V 1000 mAh Li-ion, with protection', 'Battery in the right pod; check pouch size on arrival', 1, 205, 'https://robocraze.com/products/3-7v-1000mah-li-ion-battery', False, ''),
  ('8CH USB logic analyzer', 'Debug the ADS1299 SPI link', 1, 614, 'https://robocraze.com/products/8ch-usb-logic-analyzer', False, ''),
 ]),
 dict(store='Amazon.in', note='Delivery charges depend on seller; check at checkout.', items=[
  ('Koss KPH7 on-ear headphones', 'Spring arch + sliders for the mock-up (listing: metal and plastic)', 1, 1000, AZ+'B006T9ZKAQ', False, ''),
  ('20 mm woven elastic, dark grey, 15 m', 'Elastic ends and Y legs of the midline strap', 1, 314, AZ+'B0FRS4LY29', False, ''),
  ('20 mm PP webbing, black, 10 m', 'Non-stretch Fz–Cz–Pz section with heat-punched size holes', 1, 304, AZ+'B0DXVF6C41', False, ''),
  ('OLEIO M3 × 12 mm screws with nuts', 'Arch sliders, pod shells, ear clip hinge', 1, 289, AZ+'B0HKJ7692J', False, ''),
  ('Silicone rubber sheet 2 mm, 1 × 1 ft', 'Temple pads, rear hook pad, pod linings (replaces TPU filament)', 1, 459, AZ+'B0D243VWDB', False, ''),
  ('Worison black foam sheets, A4 × 10', 'Light-blocking pad on the ear clip', 1, 175, AZ+'B09G3BDXYL', False, ''),
  ('Araldite Standard 90 g', 'Seal pod lids, strain relief on soldered leads', 1, 195, AZ+'B01HS00QX0', False, ''),
  ('Romsons alcohol swabs, 100', 'Skin prep', 1, 179, AZ+'B0G653LQPL', False, ''),
  ('PVA sponge, pack of 2', 'Cut into foam tips for the pods', 1, 239, AZ+'B0BRGG1LFY', False, ''),
  ('Flat 6-core 28 AWG cable, 5 m', 'Ear-clip lead (5 wires)', 1, 140, AZ+'B084V1TR88', False, ''),
  ('ATOM pocket scale, 200 g × 0.01 g', 'Pod force check (1 N ≈ 102 g) and spring picking', 1, 289, AZ+'B06XMZV7RH', False, 'skip'),
  ('IONIX 150 cm tailor tape', 'Head circumference, nasion–inion, size tape', 1, 99, AZ+'B098R1VVWX', False, ''),
  ('Vinabo digital caliper 150 mm', 'Print fit, pad and spring sizes', 1, 399, AZ+'B0BDLX8DWG', False, 'skip'),
 ]),
 dict(store='ToolBuy', note='Dispatch in 2 business days; shipping shown at checkout.', items=[
  ('Karam PN521 ratchet helmet', 'Cut out the rear knob + both toothed straps for the dial', 1, 306, 'https://www.toolbuy.com/tp/karam-isi-marked-shelmet-ratchet-type-safety-helmet-with-plastic-cradle-red-pn521', False, ''),
  ('ToolBuy shipping', '', 1, 100, '', True, ''),
 ]),
 dict(store='Chemist', note='', items=[
  ('0.9% saline + three 1 ml syringes (no needle)', 'Wetting the pod tips', 1, 60, '', True, ''),
 ]),
]
# Imports (USD). via='vit' assumes ~10% duty + ₹500 (7 Nov plan); personal = 42.08% duty + ₹500.
fri = dict(usd_goods=4*4.95, ship_inr=4400)   # FRI $4.95 each (shop page); DHL ₹4,400 from your 29 Oct cart
jlc = [  # (line, usd, est, link)
 ('4-layer PCB, 5 pcs, ~70 × 50 mm', 10.00, True, ''),
 ('Economic PCBA setup fee', 8.18, False, 'https://jlcpcb.com/solutions/pcb-prototype-assembly'),
 ('Stencil', 1.50, True, ''),
 ('SMT joints, 2 boards × ~450 × $0.0016', 1.44, False, 'https://jlcpcb.com/solutions/pcb-prototype-assembly'),
 ('Extended-part feeder fees, ~12 × $3', 36.00, True, 'https://jlcpcb.com/help/article/98-pcb-assembly-faqs'),
 ('ADS1299IPAGR × 2 at $70.817 (419 in stock)', 141.63, False, 'https://jlcpcb.com/partdetail/TexasInstruments-ADS1299IPAGR/C476817'),
 ('LM27762DSSR × 2 at $0.9617', 1.92, False, 'https://jlcpcb.com/parts/componentSearch?searchTxt=LM27762DSSR'),
 ('TPS7A2033PDBVR × 2 at $0.2082', 0.42, False, 'https://jlcpcb.com/parts/componentSearch?searchTxt=TPS7A2033PDBVR'),
 ('BMI270 × 2 at $2.5906', 5.18, False, 'https://jlcpcb.com/parts/componentSearch?searchTxt=BMI270'),
 ('TPD4E1B06DCKR × 10 at $0.4302', 4.30, False, 'https://jlcpcb.com/parts/componentSearch?searchTxt=TPD4E1B06DCKR'),
 ('Other passives, regulators, connectors', 10.00, True, ''),
 ('Shipping to India', 15.00, True, ''),
]
