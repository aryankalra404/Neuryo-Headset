"""Neuryo v6 buy plan PDF. python3 make_pdf_v6.py Neuryo-v6-buy-plan.pdf"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from urllib.parse import urlparse
import sys
from data_v6 import *

D = '/usr/share/fonts/truetype/dejavu/'
for n, f in [('Sans', 'DejaVuSans.ttf'), ('SansB', 'DejaVuSans-Bold.ttf'), ('Cond', 'DejaVuSansCondensed.ttf'), ('CondB', 'DejaVuSansCondensed-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(n, D + f))
addMapping('Sans', 0, 0, 'Sans'); addMapping('Sans', 1, 0, 'SansB'); addMapping('Cond', 0, 0, 'Cond'); addMapping('Cond', 1, 0, 'CondB')
INK = colors.HexColor('#1d2329'); MUTED = colors.HexColor('#5b646c'); ACC = colors.HexColor('#2f7d77')
LINE = colors.HexColor('#d9dcdf'); HEAD = colors.HexColor('#eef3f2'); EST = colors.HexColor('#fff7e6')
st = lambda name, **k: ParagraphStyle(name, fontName=k.pop('font', 'Sans'), textColor=k.pop('color', INK), **k)
H1 = st('h1', font='SansB', fontSize=17, leading=21, spaceAfter=2)
SUB = st('sub', fontSize=9, leading=12, color=MUTED, spaceAfter=8)
H2 = st('h2', font='SansB', fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=4, color=ACC)
BODY = st('b', fontSize=8.8, leading=12)
NOTE = st('n', fontSize=7.8, leading=10, color=MUTED)
CELL = st('c', font='Cond', fontSize=8, leading=10)
CELLR = st('cr', font='Cond', fontSize=8, leading=10, alignment=2)
CELLRB = st('crb', font='CondB', fontSize=8, leading=10, alignment=2)
LNK = st('l', font='Cond', fontSize=7.6, leading=9.5, color=colors.HexColor('#1f5fa8'))
rs = lambda v: '₹{:,}'.format(int(round(v)))
def link(u):
    if not u: return Paragraph('', LNK)
    p = urlparse(u); short = p.netloc.replace('www.', '') + (p.path if len(p.path) < 28 else p.path[:26] + '…')
    return Paragraph(f'<link href="{u}">{short}</link>', LNK)
W = landscape(A4)[0] - 24 * mm
def table(rows, widths, est_rows=(), bold_rows=()):
    t = Table(rows, colWidths=widths, repeatRows=1)
    s = [('LINEBELOW', (0, 0), (-1, 0), 0.8, INK), ('BACKGROUND', (0, 0), (-1, 0), HEAD), ('LINEBELOW', (0, 1), (-1, -1), 0.3, LINE),
         ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
         ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3)]
    for r in est_rows: s.append(('BACKGROUND', (0, r), (-1, r), EST))
    for r in bold_rows: s.append(('LINEABOVE', (0, r), (-1, r), 0.8, INK))
    t.setStyle(TableStyle(s)); return t
P = lambda t, s=CELL: Paragraph(t, s)

# ---------- numbers ----------
dom = {o['store']: sum(q * p for _, _, q, p, _, _, _ in o['items']) for o in orders}
DOM = sum(dom.values())
SKIP = sum(q * p for o in orders for _, _, q, p, _, _, f in o['items'] if f == 'skip')
fg = fri['qty'] * fri['each_inr']; fs = fri['ship_inr']
FRI_V = round((fg + fs) * 1.10 + 500); FRI_P = round((fg + fs) * 1.4208 + 500)
JU = sum(x[1] for x in jlc); JI = JU * CARD; JLC_V = round(JI * 1.10 + 500); JLC_P = round(JI * 1.4208 + 500)
JE = (JU + jlc_econ_delta) * CARD; JLCE_V = round(JE * 1.10 + 500)
TOT_V = DOM + FRI_V + JLC_V; TOT_P = DOM + FRI_P + JLC_P

story = [P('Neuryo v6 prototype buy plan', H1),
         P('9 Nov 2026 · for v6 with the rev B board (77 × 50 mm, KiCad) · prices marked 9 Nov were read on the seller page today; 7 Nov / 8 Nov come from '
           'your v4.4 and v5.2 plans; yellow rows are estimates · USD at ₹' + f'{RATE_MID} mid-market (7 Nov), ₹{CARD} on the card', SUB)]
summ = [[P('<b>What</b>'), P('<b>When</b>'), P('<b>Total</b>', CELLR)],
        [P('Domestic orders: Upside Down Labs, Robu, Probots, Vishaworld, Robocraze, Amazon, ToolBuy, chemist'), P('Now'), P(rs(DOM), CELLR)],
        [P(f'FRI TDE-211 Ag/AgCl pod cores × {fri["qty"]} (import through VIT)'), P('Now (2–3 weeks by DHL)'), P(rs(FRI_V), CELLR)],
        [P('Rev B board × 2 assembled at JLCPCB, Standard PCBA double-sided (import through VIT)'), P('After the professor’s review'), P(rs(JLC_V), CELLR)],
        [P('<b>Total, imports through VIT</b>'), P(''), P(f'<b>{rs(TOT_V)}</b>', CELLRB)],
        [P(f'If the VIT lab has PETG, TPU, a 0.01 g scale, a caliper and a breadboard set (−{rs(SKIP)})'), P(''), P(rs(TOT_V - SKIP), CELLR)],
        [P('If both imports go as personal imports instead (42.08% duty)'), P(''), P(rs(TOT_P), CELLR)]]
story += [table(summ, [W * .62, W * .26, W * .12], bold_rows=(4,)), Spacer(1, 5)]
story.append(P(f'<b>Recommendation.</b> Order the domestic lists and the FRI pods now, and the boards the day your professor signs off. Through VIT this lands at about '
    f'<b>{rs(TOT_V)}</b> ({rs(TOT_V - SKIP)} if the lab has the filament, tools and a breadboard set), about {rs(TOT_V - SKIP - 50000)} over the ₹50,000 grant. '
    'The board is the biggest line and the one that decides the demo, so this plan pays for JLCPCB to place both sides of it rather than you hand-soldering '
    f'the 17 input filter capacitors on the underside (that option saves about {rs(JLC_V - JLCE_V)}; section 3). Upload the rev B Gerbers, positions and '
    'bom-jlc.csv to JLCPCB for the real quote before paying.', BODY))
story.append(Spacer(1, 3))
story.append(P('<b>Changes from your v4.4 and v5.2 plans.</b> Rev B now exists, so the board is priced from its BOM. Standard PCBA (double-sided) replaces Economic, '
    'because rev B has 28 parts on the bottom. No ESP32-S3 DevKitC (the bench XIAO does bench firmware), no Koss headphones (v5 arch only), no BMI270 chips on the board '
    '(rev B takes a breakout on J7), no PA12 band (PETG is enough for the demo), no PVA powder or glycerol. One of everything for one headset: 1 cell, 1 charger, 1 MAX30102, '
    '1 BMI270, 1 PN521, 1 snap-cable pack (no ECG pair), 4 FRI pods, and 2 XIAOs (bench + board). Added: a TP4056 charger (the review says to charge the cell outside the headset), '
    'JST leads (the only in-stock cell has the wrong plug), the logic analyzer (back in stock) and Ten20 paste as demo insurance. The second JLCPCB board is the assembly minimum: leave it unpopulated until needed.', BODY))

def order_block(o):
    rows = [[P('<b>Item</b>'), P('<b>For</b>'), P('<b>Qty</b>', CELLR), P('<b>Price</b>', CELLR), P('<b>Line</b>', CELLR), P('<b>Read</b>'), P('<b>Link</b>')]]
    est = []
    for i, (n, why, q, p, u, seen, f) in enumerate(o['items'], start=1):
        nm = n + (' <font color="#8a5a00">(skip if the lab has it)</font>' if f == 'skip' else '')
        rows.append([P(nm), P(why), P(str(q), CELLR), P(rs(p), CELLR), P(rs(q * p), CELLR), P(seen), link(u)])
        if seen == 'est': est.append(i)
    rows.append([P(f'<b>{o["store"]} total</b>'), P(o['note'], NOTE), '', '', P(f'<b>{rs(dom[o["store"]])}</b>', CELLRB), '', ''])
    return KeepTogether([P(o['store'], H2), table(rows, [W * .25, W * .33, W * .04, W * .07, W * .07, W * .05, W * .19], est_rows=est, bold_rows=(len(rows) - 1,))])

story.append(P('1 · Order now: domestic', H2))
for o in orders: story.append(order_block(o))

story.append(P('2 · Imports (route both through VIT purchase)', H2))
fr = [[P('<b>FRI TDE-211 reusable Ag/AgCl snap electrode</b>'), P('<b>Amount</b>', CELLR), P('<b>Link</b>')],
      [P(f'{fri["qty"]} × ₹{fri["each_inr"]} (read 9 Nov on FRI’s store): 3 pods (Fz, Cz, Pz) + 1 for the Pz paste fallback. No spares: a lost one means a second DHL shipment'), P(rs(fg), CELLR),
       link('https://www.fri-fl-shop.com/products/reusable-snap-ag-agcl-electrode-tde-211')],
      [P('DHL shipping (your 29 Oct cart; FRI shows it only at checkout)'), P(rs(fs), CELLR), P('')],
      [P('Duty and clearance through VIT (~10% + ₹500, plan assumption)'), P(rs(FRI_V - fg - fs), CELLR), P('')],
      [P(f'<b>FRI total through VIT</b> (personal import {rs(FRI_P)})'), P(f'<b>{rs(FRI_V)}</b>', CELLRB), P('')]]
story += [table(fr, [W * .62, W * .12, W * .26], est_rows=(2, 3), bold_rows=(4,)), Spacer(1, 6)]
jr = [[P('<b>Rev B, 2 boards assembled at JLCPCB (Standard PCBA, both sides)</b>'), P('<b>USD</b>', CELLR), P('<b>Read</b>'), P('<b>Link</b>')]]
je = []
for i, (n, u, seen, l) in enumerate(jlc, start=1):
    jr.append([P(n), P(f'${u:,.2f}', CELLR), P(seen), link(l)])
    if seen == 'est': je.append(i)
jr.append([P(f'<b>Board total</b> ${JU:,.2f} × ₹{CARD} = {rs(JI)}; through VIT (~10% + ₹500) <b>{rs(JLC_V)}</b>; personal import {rs(JLC_P)}'), P(f'<b>${JU:,.2f}</b>', CELLRB), P(''), P('')])
story.append(KeepTogether([P('Gate: the professor’s review of rev B. Leave the electrode headers (J10–J19), J6, J7 and the XIAO off the JLCPCB order: you solder the leads and the XIAO '
    '(its underside pads need hot air or a hot plate, so borrow the lab’s). J1, JP1 and TP1 are through-hole: solder them yourself too.', NOTE), Spacer(1, 2),
    table(jr, [W * .58, W * .1, W * .06, W * .26], est_rows=je, bold_rows=(len(jr) - 1,))]))

story.append(P('3 · Options and what not to buy', H2))
alts = [[P('<b>Option</b>'), P('<b>Effect</b>')],
    [P('Economic PCBA, top side only, and hand-solder the 28 bottom parts'), P(f'About {rs(JLCE_V)} instead of {rs(JLC_V)} (saves about {rs(JLC_V - JLCE_V)}). Not recommended: the 17 underside parts are the input filter '
        'capacitors on the noise-critical analog half, and those parts must then be bought separately.')],
    [P('UDL gold cup electrodes, pack of 10 (₹2,999 on 8 Nov) instead of FRI'), P(f'Saves about {rs(FRI_V - 2999)} through VIT. Gold, not Ag/AgCl, so more drift with saline; your semi-dry evidence is for Ag/AgCl. Only if money runs short.')],
    [P('ECG test pair (channel 8)'), P('Needs a second snap-cable pack (₹1,999) for its 2 leads. Left out: the earlobe sensor already gives heart rate; add it after the demo.')],
    [P('Skip Ten20 (₹1,890)'), P('Fine if the semi-dry pods pass the drying test before the review; it is there so the demo can show eyes-closed alpha even if they do not.')],
    [P('Only if a test fails'), P('EVA foam 7 mm for a small-head insert (only if the PN521 will not close small enough), PVA powder + glycerol for a hydrogel tip (only if the damp foam tips fail the drying test).')],
    [P('Do not buy'), P('ESP32-S3 DevKitC, Koss headphones, BMI270 chips for the board, PA12 bands, heat-set insert kits (M3 nuts in printed pockets), FR4 strip, '
        'Philips 13955C pads, OpenBCI parts, BioAmp EXG Pill, drone LiPo packs (unprotected; the in-stock 1000 mAh ones on Robu are these).')]]
story.append(table(alts, [W * .32, W * .68]))

story.append(P('4 · Checks before paying', H2))
for c in ['Re-open each link the day you pay; pay if the price is within 15% of this plan. 9 Nov stock: XIAO in stock at Robu (sold out at TNT and Atomlab); every protected 1000 mAh '
          'wearable cell at Robu and Probots was out of stock, which is why the 950 mAh YB-503450 is used.',
          'Battery plug: the YB-503450 page lists a 3-pin 1.25 mm connector; rev B’s J1 is a 2-pin JST-PH 2.0. Cut it off and crimp or solder the 2 mm JST lead, red to the "+" '
          'beside J1 pin 2. Check with a meter before plugging in: rev B has no reverse-polarity protection.',
          'TP4056 charges at a fixed 1 A, about 1 C for this cell: charge on a hard surface, never inside the pod. Charge between sessions (950 mAh lasts hours; a session is about 5 minutes).',
          'GY-MAX30102: check the I²C pull-ups go to 3.3 V, not 1.8 V, before wiring it to J6.',
          'JLCPCB: upload the Gerbers, positions.csv and bom-jlc.csv for the real quote; the loading fee basis ("per system") and part count are estimates here. Recheck ADS1299 stock (367 on 9 Nov).',
          'Ask VIT purchase whether the JLCPCB and FRI orders can go through the institute import route; the ~10% duty is a plan assumption, not a quote.',
          'PN521: the harness range is not published. Measure it the day it arrives.']:
    story.append(P('• ' + c, BODY))
story.append(P('Sources', H2))
story.append(P('Opened 9 Nov 2026: seller pages linked in each row (Robu and Probots via their search results), FRI TDE-211, JLCPCB ADS1299IPAGR part page, '
    '<link href="https://jlcpcb.com/help/article/pcb-assembly-price"><font color="#1f5fa8">JLCPCB assembly price</font></link> (Standard double-sided $51.12 setup, $16.42 stencil, '
    '$1.53 per component; Economic $8.18, $1.53, $3.07 per extended part). 7 Nov / 8 Nov rows: your v4.4 and v5.2 buy plans. Exchange rate: x-rates, 7 Nov.', NOTE))

def footer(c, d):
    c.saveState(); c.setFont('Sans', 7); c.setFillColor(MUTED)
    c.drawString(12 * mm, 7 * mm, 'Neuryo v6 prototype buy plan · 9 Nov 2026'); c.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, f'Page {d.page}'); c.restoreState()
doc = SimpleDocTemplate(sys.argv[1], pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm, topMargin=11 * mm, bottomMargin=12 * mm,
                        title='Neuryo v6 prototype buy plan', author='Aryan Kalra')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('domestic', DOM, 'skip', SKIP, 'FRI', FRI_V, 'JLC', JLC_V, 'JLC econ', JLCE_V, 'total VIT', TOT_V, 'w/o skip', TOT_V - SKIP, 'personal', TOT_P)
