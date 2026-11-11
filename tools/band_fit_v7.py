"""v7 midline band check (11 Nov 2026): tools/band_fit.py (v6.3) with v7's band: one short Fz window (20 mm, the pod fixed at
69 mm behind the band's zero, 0.2 x 345 mm) and the zero set by the nasion gauge in three steps (31.5, 34.5, 37.5 mm above the nasion
for sizes 1-3, 4-6, 7-9) instead of exactly 0.1 x NI. Everything else as v6.3. The v6.3 docstring follows.

v6.3 midline band check (11 Nov 2026).
Does the printed midline band still lie on the head with two pods (Fz, Pz) and one long solid section where the Cz window was,
and how far do Fz and Pz land from their sites, over nasion-inion 300-390 mm and front-back vs height x0.92-1.08?

Sagittal-plane model of the shared head (designs/shared/head/head.json), same profile and head scaling as tools/strap_force.py.
The band is a beam printed in this head's midline curve (stress-free curvature = this head's), clamped at the front anchor,
pulled by the TPU tail with tension T, lying on a compression-only foundation (lining + hair), and pushed off the head at each
carriage by its pod spring F (spread over the 10 mm shoes). Windows are two 7 x 3 mm rails, solid sections 30 x 1.8 mm, the tail
22 x 2 mm TPU. Small deflections, finite differences, active-set contact. Linear beam: no creep, no twist, no friction.

Equation (w = outward gap from the band's nominal lie, u = distance along the band from the anchor):
  (EI (w'' + d))'' - T w'' + k w [w < 0] = F - T kh,   d = k0 - kh (printed minus head curvature)
Pod position error = size-notch rounding (f - 0.1)(NI_notch - NI) minus the extra band length used up by lift, integral(kh w).

Everything here is a MODEL ESTIMATE: E, foundation stiffness, tension and spring force are assumed, not measured.
Usage: python3 tools/band_fit.py designs/shared/head/head.json [--csv out.csv]   (numpy only)"""
import sys, json, base64, numpy as np

d = json.load(open(sys.argv[1])); f = d['field']
r = (np.frombuffer(base64.b64decode(f['u16_base64']), dtype='<u2').astype(float) * f['scale']).reshape(f['nel'], f['naz'])
def R(az, el):
    i = el + 90; j = az % 360; i0, j0 = int(i), int(j); di, dj = i - i0, j - j0; i1 = min(i0 + 1, 180); j1 = j0 + 1
    return r[i0, j0]*(1-di)*(1-dj) + r[i1, j0]*di*(1-dj) + r[i0, j1]*(1-di)*dj + r[i1, j1]*di*dj
def prof(th):
    rr = R(0, th) if th <= 90 else R(180, 180 - th); a = np.radians(th); return np.array([rr*np.cos(a), rr*np.sin(a)])
S = d['sites']; NI0 = d['nasion_inion_mm']
TH = np.linspace(-5, 200, 8201); P0 = np.array([prof(t) for t in TH])

def geom(sz, sy):
    """arc length and signed curvature (convex > 0) of the scaled profile, lightly smoothed (the band cannot follow 1 mm bumps)"""
    Q = P0 * [sz, sy]; s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
    su = np.linspace(0, s[-1], 6001); x = np.interp(su, s, Q[:, 0]); y = np.interp(su, s, Q[:, 1])
    ang = np.unwrap(np.arctan2(np.gradient(y), np.gradient(x))); k = np.gradient(ang, su)
    nw = int(30 / (su[1] - su[0])) | 1; w = np.hanning(nw); w /= w.sum(); k = np.convolve(k, w, 'same')   # 30 mm smoothing: the scan's 1-degree grid is noisy and the band cannot follow short bumps
    return su, k, s, Q
def s_at(s, th): return np.interp(th, TH, s)

# mannequin: band from the anchor (EL_A + 5.2 = 44.7 deg) to where the tail lifts into the cam lock (176 - 14 = 162 deg)
s0, k0all, s0th, _ = geom(1.0, 1.0)
sNz, sFpz = s_at(s0th, S['Nz']['el']), s_at(s0th, S['Fpz']['el'])
sA, sEnd = s_at(s0th, 44.7), s_at(s0th, 162.0)
NIm = s_at(s0th, 180 - S['Iz']['el']) - sNz                        # the profile's own nasion-inion (scales with the head)
site_u = {'fz': s_at(s0th, S['Fz']['el']) - sA, 'cz': s_at(s0th, 180 - S['Cz']['el']) - sA, 'pz': s_at(s0th, 180 - S['Pz']['el']) - sA}
FRAC = {'fz': 0.3, 'cz': 0.5, 'pz': 0.7}
FZ_NI = 345.0                                                         # v7: Fz fixed where it sits for a 345 mm head
GAUGE = [((1, 2, 3), 31.5), ((4, 5, 6), 34.5), ((7, 8, 9), 37.5)]       # v7: gauge step per size number (mm from the nasion to the zero)
# size notches. v6.2: sizes centred 304..384 (size = floor((NI - 299) / 10) + 1), which leaves NI 390 6 mm from size 9 (Pz 3.6 mm off).
# v6.3: centred 305..385 (size = floor((NI - 300) / 10) + 1, 390 counts as 9), so every NI from 300 to 390 is within 5 mm of its size.
NOTCH = {'v6.2': (np.arange(304, 385, 10.), 299, [((1, 2), 309.), ((3, 4), 329.), ((5, 6), 349.), ((7, 8), 369.), ((9,), 384.)]),
         'v6.3': (np.arange(305, 386, 10.), 300, [((1, 2), 310.), ((3, 4), 330.), ((5, 6), 350.), ((7, 8), 370.), ((9,), 385.)])}
SIZE_NI = NOTCH['v6.2'][0]   # windows: the band's travel (the 1 mm shift between tables moves a window end by under 1 mm)
def window(key):
    if key == 'fz7': c = site_u['fz'] + 0.2 * (FZ_NI - NI0); return (c - 10, c + 10)   # v7: 20 mm, just the pod
    c = site_u[key]; return (c + (FRAC[key]-0.1)*(SIZE_NI[0]-NI0) - 8, c + (FRAC[key]-0.1)*(SIZE_NI[-1]-NI0) + 8)
def size_for(ni, notch): return int(max(1, min(9, np.floor((ni - NOTCH[notch][1]) / 10) + 1)))
def hole_ni(key, ni, notch='v6.3'):
    sz = size_for(ni, notch)
    if key == 'fz': return next(h for g, h in NOTCH[notch][2] if sz in g)
    return NOTCH[notch][0][sz - 1]

def zero_err(ni, gauge):
    if not gauge: return 0.0
    sz = size_for(ni, 'v6.3'); g = next(v for ks, v in GAUGE if sz in ks); return g - 0.1 * ni

def solve(design, sz, sy, ni, T=6.0, F=1.0, E=2000.0, k=3.0, h=0.5, rib=None, notch='v6.3', print_ni=None, thick=1.8, splice_extra=0.0, v7=False):
    """design: windows in the band (pods are always Fz and Pz). Returns dict with lift, pod error, max stress."""
    su, kh_all, s, Q = geom(sz, sy)
    z0 = zero_err(ni, v7)
    sA_v = (s_at(s, S['Nz']['el']) + 0.1 * ni + z0) + (sA - sFpz) * ni / NI0   # anchor: strip centre at 0.1 NI (v7: the gauge step), anchor offset scales with the head
    L = sEnd - sA                                                        # band + tail length on the mannequin, to the tail's lift point
    u = np.arange(0, L + h/2, h); n = len(u)
    kh = np.interp(sA_v + u, su, kh_all)                                 # head curvature under band point u (if it lay flat)
    if print_ni is None: kb0 = np.interp(sA + u, s0, k0all)              # printed curvature: this head's (the mannequin, NI 324)
    else: c = print_ni / NI0; kb0 = np.interp(sA * c + u, s0 * c, k0all / c)   # printed in the curve of this head scaled to print_ni
    wins = [window(kk) for kk in design]
    splice = window('pz')[1] + 12 + splice_extra
    EI = np.full(n, E * 30 * thick**3 / 12)
    if rib: EI[(u > rib[0]) & (u < rib[1])] = E * rib[2]
    for a, b in wins: EI[(u > a) & (u < b)] = E * 2 * 7 * 3.0**3 / 12
    EI[u > splice] = 30.0 * 22 * 2**3 / 12                              # TPU tail
    dlt = kb0 - kh; dlt[u > splice] = 0                                   # the tail is not pre-curved
    # pod loads at the carriage for this head's size notch
    Fv = np.zeros(n); pods = {}
    for kk in ('fz', 'pz'):                                              # product: two pods (v6.2's Cz window left empty)
        hn = FZ_NI if (v7 and kk == 'fz') else hole_ni(kk, ni, notch)
        up = site_u[kk] + (FRAC[kk]-0.1) * (hn - NI0); pods[kk] = up
        m = np.abs(u - up) <= 5; Fv[m] += F / (m.sum() * h)
    # operators
    D2 = (np.diag(np.ones(n-1), 1) - 2*np.eye(n) + np.diag(np.ones(n-1), -1)) / h**2
    A0 = D2 @ np.diag(EI) @ D2 - T * D2
    rhs0 = Fv - T * kh - D2 @ (EI * dlt)
    contact = np.ones(n, bool)
    for it in range(60):
        A = A0 + np.diag(np.where(contact, k, 0.0)); rhs = rhs0.copy()
        # BCs: anchor clamped (w0 = w1 = 0); tail end pinned w = 0 and moment-free
        for i in (0, 1): A[i] = 0; A[i, i] = 1; rhs[i] = 0
        A[1] = 0; A[1, 0] = -1; A[1, 1] = 1; rhs[1] = 0
        A[-1] = 0; A[-1, -1] = 1; rhs[-1] = 0
        A[-2] = 0; A[-2, -3] = 1; A[-2, -2] = -2; A[-2, -1] = 1; rhs[-2] = -dlt[-2] * h**2
        w = np.linalg.solve(A, rhs)
        new = w < 0; new[:2] = True
        if (new == contact).all(): break
        contact = new
    lift = np.maximum(w, 0)
    shift = np.cumsum(kh * w) * h                                       # extra band length used by lift: pod lands this much forward
    M = EI * (D2 @ w + dlt); M[[0, -1]] = M[[1, -2]]
    c = np.where(EI > E * 20, 1.5, thick / 2); I = EI / E
    sig = np.abs(M) * c / I; sig[u > splice] = 0
    out = {'maxlift': lift[u < splice].max(), 'u_maxlift': u[u < splice][np.argmax(lift[u < splice])], 'sig': sig.max()}
    for kk, up in pods.items():
        i = np.argmin(abs(u - up)); m = np.abs(u - up) <= 6
        out[kk + '_lift'] = lift[m].max()
        hn = FZ_NI if (v7 and kk == 'fz') else hole_ni(kk, ni, notch)
        out[kk + '_err'] = (FRAC[kk] - 0.1) * (hn - ni) + z0 - shift[i]
        out[kk + '_round'] = (FRAC[kk] - 0.1) * (hn - ni) + z0
    return out, (u, w, EI, wins, splice)

def heads():
    for shape in (0.92, 1.0, 1.08):
        for ni in range(300, 391, 1):
            sz0, sy0 = np.sqrt(shape), 1/np.sqrt(shape)
            # scale so the profile's own nasion-inion equals ni
            su, _, s, _ = geom(sz0, sy0); ni1 = s_at(s, 180 - S['Iz']['el']) - s_at(s, S['Nz']['el'])
            kk = ni / ni1; yield shape, ni, sz0 * kk, sy0 * kk

if __name__ == '__main__':
    print(f'Mannequin NI {NI0} mm (profile {NIm:.1f}); band from the anchor, sites along the band: ' + ', '.join(f'{k} {v:.0f} mm' for k, v in site_u.items()))
    print('Windows (mm from the anchor): ' + ', '.join(f'{k} {a:.0f}-{b:.0f}' for k, (a, b) in ((k, window(k)) for k in ('fz', 'fz7', 'pz'))))
    a, b = window('fz7')[1], window('pz')[0]
    print(f'v7 solid section between the Fz and Pz windows: {a:.0f}-{b:.0f} mm, {b - a:.0f} mm long')
    print(f'Section bending stiffness (per E): solid 30 x 1.8 = {30*1.8**3/12:.1f} mm^4, two 7 x 3 rails = {2*7*27/12:.1f} mm^4')
    cases = {'v6.3 band (Fz, Pz windows, 1.8 mm between)': (['fz', 'pz'], {}),
             'v7 band (short Fz window, fixed Fz, gauge zero)': (['fz7', 'pz'], dict(v7=True)),
             'v7 printed in a 345 mm head curve (still open)': (['fz7', 'pz'], dict(v7=True, print_ni=345))}
    HS = list(heads())
    rows = []
    for T, F, E, k in [(4, 1, 2000, 3), (4, 3, 2000, 3), (6, 1, 2000, 3), (6, 3, 2000, 3), (10, 3, 2000, 3), (6, 3, 1700, 3), (6, 3, 2000, 30)]:
        print(f'\nTail tension {T} N, pod spring {F} N, E {E} MPa (PETG ~2000, PA12 ~1700), foundation {k} N/mm^2 (all assumed)')
        for name, (des, kw) in cases.items():
            res = [solve(des, sz, sy, ni, T, F, E, k, **kw)[0] for shape, ni, sz, sy in HS]
            g = lambda key: np.array([q[key] for q in res])
            print(f'  {name}: lift at Fz carriage {g("fz_lift").max():.2f}, at Pz {g("pz_lift").max():.2f} mm (band max {g("maxlift").max():.2f}); '
                  f'worst Fz {np.abs(g("fz_err")).max():.1f} mm (size rounding {np.abs(g("fz_round")).max():.1f}), Pz {np.abs(g("pz_err")).max():.1f} (rounding {np.abs(g("pz_round")).max():.1f}); '
                  f'peak bending stress {g("sig").max():.0f} MPa')
            rows.append((T, F, E, k, name, g('maxlift').max(), g('fz_lift').max(), g('pz_lift').max(), np.abs(g('fz_err')).max(), np.abs(g('pz_err')).max(), g('sig').max()))
    if '--csv' in sys.argv:
        import csv; w = csv.writer(open(sys.argv[sys.argv.index('--csv') + 1], 'w')); w.writerow(['T', 'F', 'E', 'k', 'design', 'maxlift', 'fz_lift', 'pz_lift', 'fz_err', 'pz_err', 'sigma'])
        w.writerows(rows)
