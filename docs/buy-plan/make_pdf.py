from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from urllib.parse import urlparse
import sys
from data import *

D = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('Sans', D + 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('SansB', D + 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Cond', D + 'DejaVuSansCondensed.ttf'))
pdfmetrics.registerFont(TTFont('CondB', D + 'DejaVuSansCondensed-Bold.ttf'))
from reportlab.lib.fonts import addMapping
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
CELLB = st('cb', font='CondB', fontSize=8, leading=10)
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
    s = [('LINEBELOW', (0, 0), (-1, 0), 0.8, INK), ('BACKGROUND', (0, 0), (-1, 0), HEAD),
         ('LINEBELOW', (0, 1), (-1, -1), 0.3, LINE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
         ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
         ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3)]
    for r in est_rows: s.append(('BACKGROUND', (0, r), (-1, r), EST))
    for r in bold_rows: s.append(('LINEABOVE', (0, r), (-1, r), 0.8, INK))
    t.setStyle(TableStyle(s)); return t

# ---------- numbers ----------
dom = {o['store']: sum(q * p for _, _, q, p, _, _, _ in o['items']) for o in orders}
DOM = sum(dom.values())
SKIP = sum(q * p for o in orders for _, _, q, p, _, _, f in o['items'] if f == 'skip')
fg = fri['usd_goods'] * CARD; fs = fri['ship_inr']
FRI_V = round((fg + fs) * 1.10 + 500); FRI_P = round((fg + fs) * 1.4208 + 500)
JU = sum(x[1] for x in jlc); JI = JU * CARD; JLC_V = round(JI * 1.10 + 500); JLC_P = round(JI * 1.4208 + 500)
TOT_V = DOM + FRI_V + JLC_V; TOT_P = DOM + FRI_P + JLC_P
GOLD = 2999

story = []
story.append(Paragraph('Neuryo v5.2 prototype buy plan', H1))
story.append(Paragraph('7 Nov 2026 · one order, ₹50,000 grant · prices read on the seller pages on 7 Nov unless marked est. (yellow rows) · '
                       f'USD at ₹{RATE_MID} mid-market (x-rates, 7 Nov 16:25 UTC), ₹{CARD} on the card (about 3.5% markup)', SUB))

summ = [[Paragraph('<b>What</b>', CELL), Paragraph('<b>When</b>', CELL), Paragraph('<b>Total</b>', CELLR)],
        [Paragraph('Domestic orders: Upside Down Labs, Robu, Robocraze, Amazon, ToolBuy, chemist (frame mock-up, electrodes, consumables, bench electronics)', CELL), Paragraph('Order now', CELL), Paragraph(rs(DOM), CELLR)],
        [Paragraph('FRI TDE-211 Ag/AgCl pod cores × 4 (import, through VIT)', CELL), Paragraph('After the headphone mock-up passes on 10 heads', CELL), Paragraph(rs(FRI_V), CELLR)],
        [Paragraph('ADS1299 rev B board × 2, assembled at JLCPCB (import, through VIT)', CELL), Paragraph('After the schematic is reviewed by your professor', CELL), Paragraph(rs(JLC_V), CELLR)],
        [Paragraph('<b>Total, imports through VIT</b>', CELL), Paragraph('', CELL), Paragraph(f'<b>{rs(TOT_V)}</b>', CELLRB)],
        [Paragraph(f'If the lab already has PETG, a 0.01 g scale and a caliper (−{rs(SKIP)})', CELL), Paragraph('', CELL), Paragraph(rs(TOT_V - SKIP), CELLR)],
        [Paragraph('If both imports go as personal imports instead (42.08% duty)', CELL), Paragraph('', CELL), Paragraph(rs(TOT_P), CELLR)]]
story.append(table(summ, [W * 0.62, W * 0.26, W * 0.12], bold_rows=(4,)))
story.append(Spacer(1, 5))
story.append(Paragraph(f'<b>Recommendation.</b> Order the domestic lists now ({rs(DOM)}), run the mock-up test, then place the two imports through VIT. '
    f'That lands at about {rs(TOT_V)}, {rs(50000 - TOT_V)} under the grant. The board is 55% of the money and the only line that is still an estimate in parts; '
    'get the real JLCPCB quote the day the Gerbers are ready. If the board goes as a personal import, you are about '
    f'{rs(TOT_P - 50000)} over; the fallback below (gold cups instead of FRI) claws back about {rs(FRI_P - GOLD)}.', BODY))

def order_block(o):
    rows = [[Paragraph('<b>Item</b>', CELL), Paragraph('<b>For</b>', CELL), Paragraph('<b>Qty</b>', CELLR), Paragraph('<b>Price</b>', CELLR), Paragraph('<b>Line</b>', CELLR), Paragraph('<b>Link</b>', CELL)]]
    est = []
    for i, (n, why, q, p, u, e, f) in enumerate(o['items'], start=1):
        nm = n + (' <font color="#8a5a00">(skip if you have)</font>' if f == 'skip' else '') + (' <font color="#8a5a00">est.</font>' if e else '')
        rows.append([Paragraph(nm, CELL), Paragraph(why, CELL), Paragraph(str(q), CELLR), Paragraph(rs(p), CELLR), Paragraph(rs(q * p), CELLR), link(u)])
        if e: est.append(i)
    rows.append([Paragraph(f'<b>{o["store"]} total</b>', CELL), Paragraph(o['note'], NOTE), '', '', Paragraph(f'<b>{rs(dom[o["store"]])}</b>', CELLRB), ''])
    return KeepTogether([Paragraph(o['store'], H2), table(rows, [W * .27, W * .33, W * .04, W * .07, W * .08, W * .21], est_rows=est, bold_rows=(len(rows) - 1,))])

story.append(Paragraph('1 · Order now: domestic', H2))
story.append(Paragraph('Grouped by shop so each order clears its free-delivery limit where there is one.', NOTE))
for o in orders: story.append(order_block(o))

story.append(Paragraph('2 · Hold: imports (route both through VIT purchase)', H2))
fri_rows = [[Paragraph('<b>FRI TDE-211 reusable Ag/AgCl snap electrode</b>', CELL), Paragraph('<b>Amount</b>', CELLR), Paragraph('<b>Link</b>', CELL)],
    [Paragraph('4 × $4.95 (3 pods + 1 spare; the 20-pack is sold out)', CELL), Paragraph(rs(fg), CELLR), link('https://www.fri-fl-shop.com/products/reusable-snap-ag-agcl-electrode-tde-211')],
    [Paragraph('DHL shipping (from your 29 Oct cart; FRI calculates it at checkout) est.', CELL), Paragraph(rs(fs), CELLR), Paragraph('', CELL)],
    [Paragraph('Duty and clearance through VIT (~10% + ₹500, 7 Nov plan assumption)', CELL), Paragraph(rs(FRI_V - fg - fs), CELLR), Paragraph('', CELL)],
    [Paragraph('<b>FRI total through VIT</b> (personal import: ' + rs(FRI_P) + ')', CELL), Paragraph(f'<b>{rs(FRI_V)}</b>', CELLRB), Paragraph('', CELL)]]
story.append(KeepTogether([Paragraph('Gate: the headphone mock-up passes the 10-head test (each pod 0.7–1.5 N on the scale, no sore spots).', NOTE), Spacer(1, 2),
    table(fri_rows, [W * .62, W * .12, W * .26], est_rows=(2, 3), bold_rows=(4,))]))
story.append(Spacer(1, 6))
jrows = [[Paragraph('<b>ADS1299 rev B, 2 boards assembled (JLCPCB minimum)</b>', CELL), Paragraph('<b>USD</b>', CELLR), Paragraph('<b>Link</b>', CELL)]]
jest = []
for i, (n, u, e, l) in enumerate(jlc, start=1):
    jrows.append([Paragraph(n + (' <font color="#8a5a00">est.</font>' if e else ''), CELL), Paragraph(f'${u:,.2f}', CELLR), link(l)])
    if e: jest.append(i)
jrows.append([Paragraph(f'<b>Board total</b> ${JU:,.2f} × ₹{CARD} = {rs(JI)}; through VIT (~10% + ₹500) <b>{rs(JLC_V)}</b>; personal import {rs(JLC_P)}', CELL), Paragraph(f'<b>${JU:,.2f}</b>', CELLRB), Paragraph('', CELL)])
story.append(KeepTogether([Paragraph('Gate: rev B schematic and layout done and reviewed. Economic PCBA is fine because the XIAO is hand-soldered (no ESP32 module on the JLCPCB BOM). '
    'Leave the electrode input headers off the BOM: the leads are soldered in by hand.', NOTE), Spacer(1, 2),
    table(jrows, [W * .62, W * .12, W * .26], est_rows=jest, bold_rows=(len(jrows) - 1,))]))

story.append(Paragraph('3 · Cheaper options and what not to buy', H2))
alts = [[Paragraph('<b>Option</b>', CELL), Paragraph('<b>Effect</b>', CELL), Paragraph('<b>Link</b>', CELL)],
    [Paragraph('UDL gold cup electrodes, pack of 10 (₹2,999, 10 mm, 1 m lead, 75 in stock) instead of FRI', CELL),
     Paragraph(f'Saves about {rs(FRI_V - GOLD)} through VIT ({rs(FRI_P - GOLD)} vs a personal import), ships free in the UDL order. Trade-off: gold-plated, not Ag/AgCl, so more slow drift with saline; '
               'your semi-dry evidence is for Ag/AgCl. Use only if the board comes in over budget.', CELL),
     link('https://store.upsidedownlabs.tech/product/gold-cup-electrodes-pack-of-10/')],
    [Paragraph('Midline strap, webbing, elastic and steel strip: not needed', CELL), Paragraph('v5.2 holds Fz, Cz and Pz in spring carriages on a rigid PETG spine clipped to the arch at Cz, one soft spring per pod (from the assortment). Spine, saddle clip and carriages are PETG prints.', CELL), Paragraph('', CELL)],
    [Paragraph('TPU filament (₹2,149 in the old plan): drop it', CELL), Paragraph('The 2 mm silicone sheet (₹459) covers temple pads, hook pad and linings.', CELL), Paragraph('', CELL)],
    [Paragraph('ESP32-S3 DevKitC (₹1,299): drop it', CELL), Paragraph('The second XIAO does the bench firmware on the same chip and pins as the board.', CELL), Paragraph('', CELL)],
    [Paragraph('Also not needed', CELL), Paragraph('PA12 midline band (v4 only), brass heat-set insert kits (₹1,129+; use M3 nuts in printed pockets), torsion-spring kit (₹1,734; reuse a binder-clip or clothes-peg spring for the ear clip), '
               'separate BMI270 breakout (on the board), NuPrep and Micropore (alcohol swab prep only), PVA powder and glycerol for the hydrogel tip (only if the damp foam tip fails the drying test).', CELL), Paragraph('', CELL)],
    [Paragraph('Only if a test fails', CELL), Paragraph('Weaver Ten20 paste, 228 g, ₹1,890 on Amazon: only if Neo Gel on the mastoids fails the impedance check. Check the seal and expiry on arrival.', CELL), link('https://www.amazon.in/dp/B075C3M2M7')]]
story.append(table(alts, [W * .30, W * .52, W * .18]))

story.append(Paragraph('4 · Checks before paying', H2))
for c in [
    'Re-open each link on the day you pay; pay if the price is within 15% of this plan. Prices and stock change daily.',
    'Koss KPH7: the listing gives "Metal, Plastic". Before cutting, confirm the band is spring steel with sliders; if it is plastic, return it and use another headphone with a visible steel band.',
    'Witty Fox 1000 mAh: the page gives no size or connector. Check it fits the right pod and add a JST-PH 2.0 lead if it has bare wires.',
    'Pod springs: squeeze each on the pocket scale; keep three that give about 1 N (102 g) at 7.5 mm. Fitting: slide the arch sliders until the Cz fill tube band meets its port, and save the setting per patient.',
    'Ask VIT purchase whether the JLCPCB and FRI orders can go through the institute import route; the ~10% duty here is the 7 Nov plan\'s assumption, not a quote.',
    'Recheck ADS1299 stock and price at JLCPCB on the day you order ($70.817, 419 in stock on 7 Nov). The extended-part count (12) and PCB price are estimates until the BOM exists.',
    'Robu: the 1000–1500 mAh LiPo cells (WLY803040, WLY102050, WLY103048) were all out of stock on 7 Nov, which is why the battery is from Robocraze.']:
    story.append(Paragraph('• ' + c, BODY))

story.append(Paragraph('Sources opened 7 Nov 2026', H2))
story.append(Paragraph('Seller pages linked in each row. JLCPCB fees: <link href="https://jlcpcb.com/solutions/pcb-prototype-assembly"><font color="#1f5fa8">PCB prototype assembly</font></link> ($8.18 economic setup, $0.0016 per joint, 2-board minimum) and '
    '<link href="https://jlcpcb.com/help/article/98-pcb-assembly-faqs"><font color="#1f5fa8">PCB assembly FAQs</font></link> ($3 per extended part). '
    'Exchange rate: <link href="https://www.x-rates.com/calculator/?from=USD&to=INR&amount=1"><font color="#1f5fa8">x-rates</font></link>. '
    'Robocraze free delivery: <link href="https://robocraze.com/pages/shipping-policy"><font color="#1f5fa8">shipping policy</font></link>. '
    'Import duty, clearance and the FRI shipping figure carry over from your 7 Nov v4.4 buy plan.', NOTE))

def footer(c, d):
    c.saveState(); c.setFont('Sans', 7); c.setFillColor(MUTED)
    c.drawString(12 * mm, 7 * mm, 'Neuryo v5.2 prototype buy plan · 8 Nov 2026')
    c.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, f'Page {d.page}'); c.restoreState()

doc = SimpleDocTemplate(sys.argv[1], pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm, topMargin=11 * mm, bottomMargin=12 * mm,
                        title='Neuryo v5.2 prototype buy plan', author='Aryan Kalra')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(DOM, FRI_V, JLC_V, TOT_V, TOT_P)
