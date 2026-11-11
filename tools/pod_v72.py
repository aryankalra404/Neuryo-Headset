"""Neuryo v7.2 hair pod print files (docs/v7.md, v7.2). Model estimates, nothing printed.

Builds five print files in designs/v7/stl/:
  pod-body.stl     - one-piece pod body: 14.2 x 8.5 mm, open cavity underneath, solid top, fill tube (top 24.5 mm above
                     the body's bottom face), Ag/AgCl pin socket, pocket and wire channel on the lead side (+x), two blind
                     holes for the 1.75 mm guide pins
  pod-body-rig.stl - the same body with the fill tube's top at 37.5 mm, the height of the uc-adapter pod, so it fits the
                     Ultracortex rig (designs/uc-adapter) and its "flush = 1 N" mark still works. The body is 2.5 mm
                     shorter than the uc pod: put a 2.5 mm printed washer under the rig's spring
  tip-collar.stl   - single-use collar: 0.8 mm flange chamfered to a 12.6 mm nose, 2.2 mm sleeve that presses into the
                     cavity, 10 mm bore for the foam (or felt) plug
  stud-puck.stl    - removable puck for the carriage top: 3 mm peg, recess for a 4 mm snap stud, wire groove
  bore-test.stl    - three test rings (14.6, 14.8 and 15.0 mm bores) on a base strip, marked by 1, 2 and 3 notches

Part-local z = 0 at each part's lowest face. +x is the lead side (the pin and the pigtail). Seen from the tube end,
the guide-pin holes are at 300 and 120 degrees counterclockwise from +x: the first is 60 degrees clockwise from the
lead side, as in the headset model. Mirrored, the pigtail misses the carriage's slit.

Same method as tools/uc_adapter.py (signed distance fields + marching cubes + clustered decimation); the helpers are
copied, not imported. Numbers come from the POD object in designs/v7/index.html.

Run: python3 tools/pod_v72.py
"""
import os
import struct
import numpy as np
from skimage.measure import marching_cubes

OUT = os.path.join(os.path.dirname(__file__), '..', 'designs', 'v7', 'stl')
RES = 0.08  # mm voxel
CELL = 0.3  # mm decimation cell

# ---------------------------------------------------------------- dimensions (mm), from POD in designs/v7/index.html
Y0 = 3.3                       # body bottom face above the scalp in the headset (part z = y - Y0)
BODY_R, BODY_H = 7.1, 8.5      # body 14.2 x 8.5 (y 3.3 to 11.8)
CHAMFER = 0.4                  # bottom outer chamfer
CAV_R, CAV_H = 5.8, 4.7        # cavity 11.6 x 4.7 (ceiling at y 8.0)
TUBE_RO, TUBE_RI = 2.0, 1.25   # fill tube
TUBE_TOP = 24.5                # y 27.8: 4 mm above the carriage top at the 1 N position
TUBE_TOP_RIG = 37.5            # uc-adapter pod height
CSINK_R, CSINK_D = 1.8, 0.9    # countersink at the tube's top
PIN_X, SOCK_R, SOCK_Z = 3.8, 1.1, (CAV_H, 7.3)            # Ag/AgCl pin socket (2 mm pin; hole 2.2 mm)
POCKET = dict(x=(3.2, 6.2), y=(-1.5, 1.5), z=(7.3, BODY_H))
CHANNEL = dict(x=(6.2, 7.2), w=1.4, z=(7.5, BODY_H))
GPIN_R, GPIN_Z, GPIN_RIN = 0.88, 7.0, 4.1                 # guide-pin holes (y 10.3 in the headset)
GPIN_ANG = (np.radians(300.0), np.radians(120.0))          # counterclockwise from +x, seen from the tube end
COLLAR = dict(nose_r=6.3, flange_r=7.1, flange_h=0.8, ro=5.75, ri=5.0, h=3.0, lead=0.3)
PUCK = dict(r=5.5, z=(4.0, 6.5), peg_r=1.5, recess_r=2.6, recess_d=0.8, groove_w=1.4, groove_d=1.0)
BORE_TEST = dict(bores=(14.6, 14.8, 15.0), wall=2.0, h=6.0, base_t=1.0, pitch=21.0)


# ---------------------------------------------------------------- SDF helpers (copied from tools/uc_adapter.py)
def grid(lo, hi):
    xs = [np.arange(a, b + RES, RES, dtype=np.float32) for a, b in zip(lo, hi)]
    X, Y, Z = np.meshgrid(*xs, indexing='ij')
    return X, Y, Z, np.array(lo, np.float32)


def cyl(R, z0, z1, r, Z):
    return np.maximum(r - R, np.maximum(z0 - Z, Z - z1))


def box(X, Y, Z, x, y, z):
    return np.maximum.reduce([x[0] - X, X - x[1], y[0] - Y, Y - y[1], z[0] - Z, Z - z[1]])


def union(*a):
    return np.minimum.reduce(a)


def sub(a, b):
    return np.maximum(a, -b)


def slot(X, Y, Z, angle, w, z0, z1, r_in, r_out):
    """Radial slot with round ends at the given angle (a radial cylinder when z1 - z0 = w)."""
    c, s = np.cos(angle), np.sin(angle)
    along = X * c + Y * s
    side = -X * s + Y * c
    zc = np.clip(Z, z0 + w / 2, z1 - w / 2)
    d2d = np.hypot(side, Z - zc) - w / 2
    return np.maximum(d2d, np.maximum(r_in - along, along - r_out))


def decimate(v, f, cell=CELL):
    """Clustered quadric decimation: one vertex per cell, placed to keep edges sharp."""
    n = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    area = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / (area + 1e-12)
    d = -np.einsum('ij,ij->i', n, v[f[:, 0]])
    plane = np.hstack([n, d[:, None]]) * np.sqrt(area)            # area-weighted planes
    Kf = plane[:, :, None] * plane[:, None, :]                    # 4x4 quadric per face
    key = np.floor((v - v.min(0)) / cell).astype(np.int64)
    _, cid = np.unique(key, axis=0, return_inverse=True)
    cid = cid.ravel()
    nc = cid.max() + 1
    Q = np.zeros((nc, 4, 4))
    for k in range(3):
        np.add.at(Q, cid[f[:, k]], Kf)
    cnt = np.bincount(cid, minlength=nc)[:, None]
    mean = np.zeros((nc, 3))
    np.add.at(mean, cid, v)
    mean /= cnt
    A, bvec = Q[:, :3, :3], -Q[:, :3, 3]
    # regularise toward the cell mean so flat or ill-posed cells stay put
    lam = 1e-3 * np.trace(A, axis1=1, axis2=2)[:, None, None] + 1e-9
    pos = np.linalg.solve(A + lam * np.eye(3), (bvec + lam[:, 0] * mean)[..., None])[..., 0]
    far = np.linalg.norm(pos - mean, axis=1) > cell
    pos[far] = mean[far]
    nf = cid[f]
    keep = (nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2])
    nf = nf[keep]
    nf = np.unique(np.sort(nf, axis=1), axis=0, return_index=True)[1]
    nf = cid[f][keep][np.sort(nf)]
    return pos, nf


def save(name, sdf, lo):
    v, f, _, _ = marching_cubes(np.pad(sdf, 1, constant_values=1.0), 0.0, spacing=(RES,) * 3)
    v = v - RES + lo
    v, f = decimate(v, f)
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, 'wb') as fh:
        fh.write(b'Neuryo v7.2 pod'.ljust(80, b' '))
        fh.write(struct.pack('<I', len(f)))
        rec = np.zeros(len(f), dtype=[('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')])
        rec['n'] = n
        rec['v'] = tri.reshape(-1, 9)
        fh.write(rec.tobytes())
    lo_, hi_ = v.min(0), v.max(0)
    print(f'{name}: {len(f)} triangles, bounding box {np.round(lo_, 2).tolist()} to {np.round(hi_, 2).tolist()} mm, size {np.round(hi_ - lo_, 2).tolist()} mm')
    return len(f), lo_, hi_


# ---------------------------------------------------------------- wall checks (exact distances between the features)
def guide_hole_surface(angle, n_t=60, n_phi=72):
    """Points on one guide-pin hole: its side wall from r 4.1 to the body's outside, and its flat inner end."""
    u = np.array([np.cos(angle), np.sin(angle), 0.0])
    v1 = np.array([-np.sin(angle), np.cos(angle), 0.0])
    v2 = np.array([0.0, 0.0, 1.0])
    phi = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
    ring = np.cos(phi)[:, None] * v1 + np.sin(phi)[:, None] * v2
    c0 = np.array([0, 0, GPIN_Z])
    side = [c0 + t * u + GPIN_R * ring for t in np.linspace(GPIN_RIN, BODY_R, n_t)]
    end = [c0 + GPIN_RIN * u + rho * ring for rho in np.linspace(0, GPIN_R, 12)]
    return np.vstack(side + end)


def dist_vcyl(p, cx, cy, R, z0, z1):
    dr = np.maximum(np.hypot(p[:, 0] - cx, p[:, 1] - cy) - R, 0)
    dz = np.maximum.reduce([z0 - p[:, 2], p[:, 2] - z1, np.zeros(len(p))])
    return np.hypot(dr, dz)


def dist_box(p, x, y, z):
    d = [np.maximum.reduce([lo - p[:, k], p[:, k] - hi, np.zeros(len(p))]) for k, (lo, hi) in enumerate((x, y, z))]
    return np.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)


def wall_checks():
    pts = np.vstack([guide_hole_surface(a) for a in GPIN_ANG])
    socket = dist_vcyl(pts, PIN_X, 0.0, SOCK_R, *SOCK_Z).min()
    pocket = dist_box(pts, POCKET['x'], POCKET['y'], POCKET['z']).min()
    top = BODY_H - (GPIN_Z + GPIN_R)
    ceiling = (GPIN_Z - GPIN_R) - CAV_H
    print(f'walls: socket to pin hole {socket:.2f} mm (needs 1.5), pocket to pin hole {pocket:.2f} mm (needs 1.0), '
          f'pin hole to top face {top:.2f} mm (needs 0.6), pin hole to ceiling {ceiling:.2f} mm (needs 1.2)')
    assert socket >= 1.5, socket
    assert pocket >= 1.0, pocket
    assert top >= 0.6, top
    assert ceiling >= 1.2, ceiling
    return dict(socket=socket, pocket=pocket, top=top, ceiling=ceiling)


# ---------------------------------------------------------------- parts
def pod_body(name, tube_top):
    X, Y, Z, lo = grid((-7.4, -7.4, -0.2), (7.4, 7.4, tube_top + 0.2))
    r = np.hypot(X, Y)
    body = cyl(BODY_R, 0, BODY_H, r, Z)
    body = np.maximum(body, r - Z - (BODY_R - CHAMFER))                   # bottom outer chamfer
    tube = cyl(TUBE_RO, BODY_H - 0.5, tube_top, r, Z)
    solid = union(body, tube)
    cavity = cyl(CAV_R, -1, CAV_H, r, Z)
    bore = cyl(TUBE_RI, CAV_H - 0.5, tube_top + 1, r, Z)
    csink = np.maximum(r - (TUBE_RI + (Z - (tube_top - CSINK_D)) * (CSINK_R - TUBE_RI) / CSINK_D), (tube_top - CSINK_D) - Z)
    socket = cyl(SOCK_R, CAV_H - 0.5, SOCK_Z[1] + 0.01, np.hypot(X - PIN_X, Y), Z)
    pocket = box(X, Y, Z, POCKET['x'], POCKET['y'], (POCKET['z'][0], BODY_H + 1))
    channel = box(X, Y, Z, (CHANNEL['x'][0] - 0.01, CHANNEL['x'][1] + 1), (-CHANNEL['w'] / 2, CHANNEL['w'] / 2), (CHANNEL['z'][0], BODY_H + 1))
    pins = union(*[slot(X, Y, Z, a, 2 * GPIN_R, GPIN_Z - GPIN_R, GPIN_Z + GPIN_R, GPIN_RIN, BODY_R + 1) for a in GPIN_ANG])
    return save(name, sub(solid, union(cavity, bore, csink, socket, pocket, channel, pins)), lo)


def tip_collar():
    c = COLLAR
    X, Y, Z, lo = grid((-7.4, -7.4, -0.2), (7.4, 7.4, c['h'] + 0.2))
    r = np.hypot(X, Y)
    flange = np.maximum(r - (c['nose_r'] + Z * (c['flange_r'] - c['nose_r']) / c['flange_h']), np.maximum(-Z, Z - c['flange_h']))
    sleeve = cyl(c['ro'], c['flange_h'] - 0.01, c['h'], r, Z)
    sleeve = np.maximum(sleeve, r - (c['h'] - Z) - (c['ro'] - c['lead']))   # top lead-in for the press fit
    return save('tip-collar.stl', sub(union(flange, sleeve), cyl(c['ri'], -1, c['h'] + 1, r, Z)), lo)


def stud_puck():
    p = PUCK
    X, Y, Z, lo = grid((-5.8, -5.8, -0.2), (5.8, 5.8, p['z'][1] + 0.2))
    r = np.hypot(X, Y)
    solid = union(cyl(p['r'], *p['z'], r, Z), cyl(p['peg_r'], 0, p['z'][0] + 0.01, r, Z))
    recess = cyl(p['recess_r'], p['z'][1] - p['recess_d'], p['z'][1] + 1, r, Z)
    groove = box(X, Y, Z, (0, p['r'] + 1), (-p['groove_w'] / 2, p['groove_w'] / 2), (p['z'][1] - p['groove_d'], p['z'][1] + 1))
    return save('stud-puck.stl', sub(solid, union(recess, groove)), lo)


def bore_test():
    b = BORE_TEST
    n = len(b['bores'])
    ro_max = max(b['bores']) / 2 + b['wall']
    X, Y, Z, lo = grid((-ro_max - 0.4, -ro_max - 0.4, -0.2), ((n - 1) * b['pitch'] + ro_max + 0.4, ro_max + 0.4, b['h'] + 0.2))
    rings, holes, notches = [], [], []
    for k, d in enumerate(b['bores']):
        cx = k * b['pitch']
        r = np.hypot(X - cx, Y)
        rings.append(cyl(d / 2 + b['wall'], 0, b['h'], r, Z))
        holes.append(cyl(d / 2, -1, b['h'] + 1, r, Z))
        for j in range(k + 1):                                           # 1, 2 or 3 notches on the outer top edge (-y side)
            a = np.radians(-90 + (j - k / 2) * 14)
            px, py = cx + np.cos(a) * (d / 2 + b['wall']), np.sin(a) * (d / 2 + b['wall'])
            notches.append(np.maximum(np.hypot(X - px, Y - py) - 0.6, (b['h'] - 1.0) - Z))
    strip = box(X, Y, Z, (0, (n - 1) * b['pitch']), (-2.0, 2.0), (0, b['base_t']))
    return save('bore-test.stl', sub(union(*rings, strip), union(*holes, *notches)), lo)


if __name__ == '__main__':
    walls = wall_checks()
    pod_body('pod-body.stl', TUBE_TOP)
    pod_body('pod-body-rig.stl', TUBE_TOP_RIG)
    tip_collar()
    stud_puck()
    bore_test()
