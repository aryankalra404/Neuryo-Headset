"""v5.1 midline strap check (7 Nov 2026).
Force on the Fz, Cz and Pz pods per newton of strap tension, for an elastic strap that runs from a front anchor on the midline
(the Y junction, angle thJ from the front) over the three pods to the rear band (thB), on heads of nasion-inion 300-390 mm and
front-back vs height ratio x0.92-1.08. The strap rides h mm above the scalp on each pod and is straight between pods.
Sagittal-plane model of the shared head. Usage: python3 tools/strap_force.py designs/shared/head/head.json   (numpy only)"""
import sys, json, base64, numpy as np
d = json.load(open(sys.argv[1])); f = d['field']
r = (np.frombuffer(base64.b64decode(f['u16_base64']), dtype='<u2').astype(float) * f['scale']).reshape(f['nel'], f['naz'])
def R(az, el):
    i = el + 90; j = az % 360; i0, j0 = int(i), int(j); di, dj = i - i0, j - j0; i1 = min(i0 + 1, 180); j1 = j0 + 1
    return r[i0, j0]*(1-di)*(1-dj) + r[i1, j0]*di*(1-dj) + r[i0, j1]*(1-di)*dj + r[i1, j1]*di*dj
def prof(th):
    rr = R(0, th) if th <= 90 else R(180, 180 - th); a = np.radians(th); return np.array([rr*np.cos(a), rr*np.sin(a)])
S = d['sites']; TH = np.linspace(-5, 200, 20501); P = np.array([prof(t) for t in TH])
thF, thC, thP = S['Fz']['el'], 180 - S['Cz']['el'], 180 - S['Pz']['el']
def run(sz, sy, thJ, thB, h, hC=None, hP=None):
    hC = h if hC is None else hC; hP = h if hP is None else hP
    Q = P * [sz, sy]; T = np.gradient(Q, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.stack([T[:, 1], -T[:, 0]], 1)
    k = np.argmin(abs(TH - 90)); N = N if np.dot(N[k], Q[k]) > 0 else -N
    pt = lambda th, l: (Q[np.argmin(abs(TH - th))] + l * N[np.argmin(abs(TH - th))], N[np.argmin(abs(TH - th))])
    pts = [pt(thJ, 1)[0], pt(thF, h)[0], pt(thC, hC)[0], pt(thP, hP)[0], pt(thB, 1)[0]]
    out = []
    for i, th in zip((1, 2, 3), (thF, thC, thP)):
        a = pts[i] - pts[i-1]; b = pts[i+1] - pts[i]; a /= np.linalg.norm(a); b /= np.linalg.norm(b); out.append(np.dot(a - b, pt(th, 0)[1]))
    return np.array(out)
def nir(sz, sy):
    Q = P * [sz, sy]; s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
    s0 = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    a, b = np.argmin(abs(TH - S['Nz']['el'])), np.argmin(abs(TH - 175)); return (s[b]-s[a]) / (s0[b]-s0[a])
if __name__ == '__main__':
    print('Front clip at 55 deg, back clip at 150 deg (both on the scalp; a straight line from Pz to the rear band at 188 deg')
    print('would pass about 12 mm inside the scalp, so the strap ends at a back clip whose legs run down to the rear band).')
    for h, hC, hP in [(16, 28, 16), (16, 28, 22)]:
        rows = []
        for shape in [0.92, 1.0, 1.08]:
            for target in [300, 345, 390]:
                sz0, sy0 = np.sqrt(shape), 1/np.sqrt(shape); kk = target / (d['nasion_inion_mm'] * nir(sz0, sy0))
                rows.append(run(sz0*kk, sy0*kk, 55, 150, h, hC, hP))
        a = np.array(rows)
        print(f'  caps Fz {h} / Cz {hC} / Pz {hP} mm: N per N of tension  Fz {a[:,0].min():.2f}-{a[:,0].max():.2f}  Cz {a[:,1].min():.2f}-{a[:,1].max():.2f}  Pz {a[:,2].min():.2f}-{a[:,2].max():.2f}')
