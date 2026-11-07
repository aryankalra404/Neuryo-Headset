"""v5 midline bar check (7 Nov 2026).
Gap from the bar to the scalp at the Fz and Pz carriages, minus the nominal, for heads of nasion-inion 300-390 mm and
front-back vs height ratio x0.92-1.08, after the Cz pivot balances Fz and Pz. Compares a bar that follows this head's curve
with one that runs straight along the Cz-Fz / Cz-Pz chords through the size holes. Sagittal-plane model of the shared head.
Usage: python3 tools/bar_gap.py designs/shared/head/head.json [--rigid]   (numpy only)
--rigid (v5.2, 8 Nov): spine clipped rigidly at Cz, no pivot; prints the worse of Fz and Pz."""
import json, base64, numpy as np, sys
d = json.load(open(sys.argv[1])); f = d['field']
r = np.frombuffer(base64.b64decode(f['u16_base64']), dtype='<u2').astype(float) * f['scale']
r = r.reshape(f['nel'], f['naz']) if r.size == f['nel']*f['naz'] else None
assert r is not None
def R(az, el):   # bilinear, az 0..360, el -90..90
    i = el + 90; j = az % 360
    i0, j0 = int(np.floor(i)), int(np.floor(j)); di, dj = i - i0, j - j0
    i1, j1 = min(i0+1, 180), j0+1
    return (r[i0,j0]*(1-di)*(1-dj) + r[i1,j0]*di*(1-dj) + r[i0,j1]*(1-di)*dj + r[i1,j1]*di*dj)
def prof(th):     # sagittal profile, th from front (0) over the top (90) to back (180); returns (z, y)
    rr = R(0, th) if th <= 90 else R(180, 180 - th)
    a = np.radians(th); return np.array([rr*np.cos(a), rr*np.sin(a)])
S = d['sites']; NI0 = d['nasion_inion_mm']
thF = S['Fz']['el']; thC = 180 - S['Cz']['el']; thP = 180 - S['Pz']['el']
TH = np.linspace(-5, 185, 19001); P = np.array([prof(t) for t in TH])
seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
N = np.stack([T[:, 1], -T[:, 0]], 1)        # outward normal (check sign below)
iC = np.argmin(abs(TH - thC))
if np.dot(N[iC], P[iC]) < 0: N = -N
OFF = 22.0
def at(cum): i = np.argmin(abs(seg - cum)); return P[i], N[i]
cC = seg[iC]
def gaps(sz, sy, ni_size):
    # new head: profile scaled (z by sz, y by sy); its Cz is the scaled reference Cz (sites scale with the head)
    Q = P * [sz, sy]
    Tq = np.gradient(Q, axis=0); Tq /= np.linalg.norm(Tq, axis=1)[:, None]; Nq = np.stack([Tq[:, 1], -Tq[:, 0]], 1)
    if np.dot(Nq[iC], Q[iC]) < 0: Nq = -Nq
    # bar (reference shape) pinned with its Cz point 22 mm above the new Cz, along the new normal; free to rotate by phi
    piv_ref = P[iC] + OFF * N[iC]; piv_new = Q[iC] + OFF * Nq[iC]
    base_ang = np.arctan2(Nq[iC][1], Nq[iC][0]) - np.arctan2(N[iC][1], N[iC][0])
    def gap_at(cum, phi):
        p, n = at(cum); top = p + OFF * n
        a = base_ang + phi; Rm = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        top_n = piv_new + Rm @ (top - piv_ref); dirn = -(Rm @ n)
        # march along the carriage axis to the new scalp
        v = Q - top_n; along = v @ dirn; perp = np.abs(v[:, 0]*dirn[1] - v[:, 1]*dirn[0])
        ok = along > 0; k = np.argmin(np.where(ok, perp, 1e9)); return along[k]
    dF = 0.2 * (ni_size - NI0)
    cF, cP = seg[np.argmin(abs(TH - thF))] - dF, seg[np.argmin(abs(TH - thP))] + dF
    best = min((abs(gap_at(cF, ph) - gap_at(cP, ph)), ph) for ph in np.radians(np.linspace(-8, 8, 321)))[1]
    return gap_at(cF, 0), gap_at(cP, 0), gap_at(cF, best), np.degrees(best)
def ni_of(sz, sy):
    Q = P * [sz, sy]; s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
    return s[np.argmin(abs(TH - (180 - S['Iz']['el'] if 'Iz' in S else 175)))] - s[np.argmin(abs(TH - S['Nz']['el']))]
thF, thP = S['Fz']['el'], 180 - S['Pz']['el']
iF, iP = np.argmin(abs(TH - thF)), np.argmin(abs(TH - thP))
SIZE_NI = [304, 314, 324, 334, 344, 354, 364, 374, 384]
GROUPS = [[1, 2], [3, 4], [5, 6], [7, 8], [9]]
gmean = lambda sz: np.mean([SIZE_NI[k-1] for k in next(gr for gr in GROUPS if sz in gr)])
def run(OFF, straight):
    def holes(ni_h):
        out = []
        for i in (iF, iP):
            if straight:   # bar section along the Cz->site chord: the point 26 mm above the site of the head scaled to ni_h
                s = ni_h / NI0; top = P[iC] + s * (P[i] - P[iC]) + OFF * N[i]; n = N[i]
            else:          # bar follows this head at a constant offset; hole at 0.2*(ni_h-NI0) along the scalp from the site
                d = 0.2 * (ni_h - NI0) * (-1 if i == iF else 1); j = np.argmin(abs(seg - (seg[i] + d))); top = P[j] + OFF * N[j]; n = N[j]
            out.append((top, n))
        return out
    def gaps(sz, sy, ni_h):
        Q = P * [sz, sy]
        Tq = np.gradient(Q, axis=0); Tq /= np.linalg.norm(Tq, axis=1)[:, None]; Nq = np.stack([Tq[:, 1], -Tq[:, 0]], 1)
        if np.dot(Nq[iC], Q[iC]) < 0: Nq = -Nq
        piv_ref = P[iC] + OFF * N[iC]; piv_new = Q[iC] + OFF * Nq[iC]
        base = np.arctan2(Nq[iC][1], Nq[iC][0]) - np.arctan2(N[iC][1], N[iC][0])
        H = holes(ni_h)
        def gap(k, phi):
            top, n = H[k]; a = base + phi; Rm = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
            t = piv_new + Rm @ (top - piv_ref); dn = -(Rm @ n); v = Q - t; al = v @ dn; pe = np.abs(v[:, 0]*dn[1] - v[:, 1]*dn[0])
            return al[np.argmin(np.where(al > 0, pe, 1e9))]
        if '--rigid' in sys.argv:
            return max((gap(0, 0.0), gap(1, 0.0)), key=lambda g: abs(g - OFF))
        ph = min((abs(gap(0, p) - gap(1, p)), p) for p in np.radians(np.linspace(-8, 8, 161)))[1]
        return (gap(0, ph) + gap(1, ph)) / 2
    def nir(sz, sy):
        Q = P * [sz, sy]; s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
        a, b = np.argmin(abs(TH - S['Nz']['el'])), np.argmin(abs(TH - 175)); return (s[b]-s[a]) / (seg[b]-seg[a])
    rows = []
    for shape in [0.92, 1.0, 1.08]:
        row = []
        for target in [300, 324, 345, 368, 390]:
            sz0, sy0 = np.sqrt(shape), 1/np.sqrt(shape); k = target / (NI0 * nir(sz0, sy0))
            size = max(1, min(9, int((target - 299) // 10) + 1))
            row.append(gaps(sz0*k, sy0*k, gmean(size)) - OFF)
        rows.append(row); print(f'  shape x{shape:.2f}: ' + '  '.join(f'{x:+5.1f}' for x in row))
    return np.array(rows)
for OFF in [22, 26]:
    for st in [False, True]:
        print(f'OFF {OFF} {"straight chord bar" if st else "bar follows head (before the fix)"}: gap minus nominal at NI 300/324/345/368/390')
        run(OFF, st)
