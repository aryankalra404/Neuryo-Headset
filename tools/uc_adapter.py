"""Neuryo pod adapter for the OpenBCI Ultracortex Mark IV frame (mock-up test rig).

Builds four print files in designs/uc-adapter/stl/:
  node-ring.stl  - glues into a Mark IV frame node (25.4 mm hole) instead of OpenBCI's insert; M20 x 2 internal thread
  pod-tube.stl   - screws into the ring; 14.8 mm bore for the pod, spring seat, knurled knob, fill and lead holes, pin slots
  pod-body.stl   - 14.2 x 11 mm pod with lid, 26.5 mm fill tube (force mark), lead hole and two 1.75 mm pin holes
  tip-collar.stl - press-fits into the pod's open bottom and holds a 10 mm foam tip

Geometry is original (signed distance fields + marching cubes), sized only to the Mark IV node hole
(25.4 mm, measured from OpenBCI's GPL-3.0 DevKit STLs; no OpenBCI geometry is copied).

Run: python3 tools/uc_adapter.py
"""
import os
import struct
import numpy as np
from skimage.measure import marching_cubes

OUT = os.path.join(os.path.dirname(__file__), '..', 'designs', 'uc-adapter', 'stl')
RES = 0.08  # mm voxel
CELL = 0.3  # mm decimation cell

# ---------------------------------------------------------------- dimensions (mm)
P = 2.0                    # thread pitch
EXT_MAJ, EXT_MIN = 9.85, 8.75    # tube external thread radii
INT_MAJ, INT_MIN = 10.25, 9.15   # ring internal thread radii (0.4 radial clearance)
RING_R, RING_H = 12.6, 6.4       # ring: 25.2 OD in the 25.4 node hole, frame thickness
BORE = 7.4                       # tube bore radius (14.8 ID)
THREAD_Z = (2.0, 30.0)           # threaded length of the tube
KNOB_Z = (30.0, 36.0)
KNOB_R, KNURLS, KNURL_D = 12.4, 24, 0.6
SEAT_Z = 31.0                    # spring seat (top of the bore)
FILL_R = 2.3                     # knob hole for the 4 mm fill tube
LEAD_R, LEAD_X = 1.2, 5.8        # knob lead hole (off-centre, outside an 8 mm spring)
SLOT_W, SLOT_Z = 2.1, (2.0, 11.0)  # two pin slots, opposite
POD_R, POD_H = 7.1, 11.0         # pod body 14.2 x 11 (taller than v4's 9 so the pins sit in the wall)
POD_IN, LID_T = 5.8, 1.5         # cup inner radius, lid thickness
TUBE_RO, TUBE_RI, TUBE_L = 2.0, 1.25, 26.5   # fill tube on the lid: top flush with the knob at 1 N
MARK_DOWN = 3.5                  # groove 3.5 mm below fill-tube top = 1.5 N mark
PIN_R, PIN_Z, PIN_DEPTH = 0.88, 8.0, 3.0     # pin holes for 1.75 mm filament pins
COLLAR = dict(ro=5.75, ri=5.0, h=3.0, flange_r=7.1, flange_h=0.8)


# ---------------------------------------------------------------- SDF helpers
def grid(lo, hi):
    xs = [np.arange(a, b + RES, RES, dtype=np.float32) for a, b in zip(lo, hi)]
    X, Y, Z = np.meshgrid(*xs, indexing='ij')
    return X, Y, Z, np.array(lo, np.float32)


def cyl(R, z0, z1, r, Z):
    return np.maximum(r - R, np.maximum(z0 - Z, Z - z1))


def union(*a):
    return np.minimum.reduce(a)


def sub(a, b):
    return np.maximum(a, -b)


def thread_radius(theta, Z, rmin, rmaj, external=True):
    """Trapezoidal 60-degree profile along a right-hand helix."""
    u = np.mod(Z - P * theta / (2 * np.pi), P) / P   # 0..1 along one pitch
    tri = 1 - np.abs(2 * u - 1)                     # 0 at root, 1 at crest
    tri = np.clip((tri - 0.15) / 0.7, 0, 1)         # flat crest and root
    # Same phase for both parts: the ring's groove (large hole radius) sits where the tube's crest is.
    return rmin + (rmaj - rmin) * tri


def slot(X, Y, Z, angle, w, z0, z1, r_in, r_out):
    """Radial slot with round ends at the given angle."""
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
        fh.write(b'Neuryo uc-adapter'.ljust(80, b' '))
        fh.write(struct.pack('<I', len(f)))
        rec = np.zeros(len(f), dtype=[('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')])
        rec['n'] = n
        rec['v'] = tri.reshape(-1, 9)
        fh.write(rec.tobytes())
    print(f'{name}: {len(f)} triangles, size {np.ptp(v, 0).round(2)} mm')


# ---------------------------------------------------------------- parts
def node_ring():
    X, Y, Z, lo = grid((-13, -13, -0.2), (13, 13, RING_H + 0.2))
    r, th = np.hypot(X, Y), np.arctan2(Y, X)
    outer = cyl(RING_R, 0, RING_H, r, Z)
    hole = r - thread_radius(th, Z, INT_MIN, INT_MAJ, external=False)
    cham = r + np.minimum(Z, RING_H - Z) - (INT_MIN + 0.7)   # 0.7 mm lead-in both faces
    save('node-ring.stl', sub(outer, union(hole, cham)), lo)


def pod_tube():
    X, Y, Z, lo = grid((-12.8, -12.8, -0.2), (12.8, 12.8, KNOB_Z[1] + 0.2))
    r, th = np.hypot(X, Y), np.arctan2(Y, X)
    z0, z1 = THREAD_Z
    plain = cyl(EXT_MIN, 0, z0 + 0.01, r, Z)
    thr = np.maximum(r - thread_radius(th, Z, EXT_MIN, EXT_MAJ), np.maximum(z0 - Z, Z - z1))
    knurl_r = KNOB_R - KNURL_D * 0.5 * (1 + np.cos(KNURLS * th))
    knob = np.maximum(r - knurl_r, np.maximum(KNOB_Z[0] - Z, Z - KNOB_Z[1]))
    body = union(plain, thr, knob)
    body = np.maximum(body, r - Z - (EXT_MIN - 0.5))                    # bottom outer chamfer
    bore = cyl(BORE, -1, SEAT_Z, r, Z)
    bore = union(bore, r + Z - (BORE + 0.6))                             # bottom lead-in
    fill = cyl(FILL_R, SEAT_Z - 1, KNOB_Z[1] + 1, r, Z)
    lead = cyl(LEAD_R, SEAT_Z - 1, KNOB_Z[1] + 1, np.hypot(X - LEAD_X, Y), Z)
    slots = union(slot(X, Y, Z, np.pi / 2, SLOT_W, *SLOT_Z, 0, 11),
                  slot(X, Y, Z, -np.pi / 2, SLOT_W, *SLOT_Z, 0, 11))
    save('pod-tube.stl', sub(body, union(bore, fill, lead, slots)), lo)


def pod_body():
    top = POD_H + TUBE_L
    X, Y, Z, lo = grid((-7.4, -7.4, -0.2), (7.4, 7.4, top + 0.2))
    r = np.hypot(X, Y)
    cup = cyl(POD_R, 0, POD_H, r, Z)
    cup = np.maximum(cup, r - Z - (POD_R - 0.4))                         # small bottom chamfer
    tube = cyl(TUBE_RO, POD_H - 0.5, top, r, Z)
    groove_z = top - MARK_DOWN
    groove = np.maximum((TUBE_RO - 0.35) - r, np.abs(Z - groove_z) - 0.3)
    tube = sub(tube, groove)                                             # 0.35 mm deep ring groove
    solid = union(cup, tube)
    cavity = cyl(POD_IN, -1, POD_H - LID_T, r, Z)
    fill = cyl(TUBE_RI, POD_H - LID_T - 0.5, top + 1, r, Z)
    lead = cyl(0.8, POD_H - LID_T - 0.5, POD_H + 0.5, np.hypot(X - (POD_IN - 0.9), Y), Z)
    pins = union(slot(X, Y, Z, np.pi / 2, 2 * PIN_R, PIN_Z - PIN_R, PIN_Z + PIN_R, POD_R - PIN_DEPTH, POD_R + 1),
                 slot(X, Y, Z, -np.pi / 2, 2 * PIN_R, PIN_Z - PIN_R, PIN_Z + PIN_R, POD_R - PIN_DEPTH, POD_R + 1))
    save('pod-body.stl', sub(solid, union(cavity, fill, lead, pins)), lo)


def tip_collar():
    c = COLLAR
    X, Y, Z, lo = grid((-7.4, -7.4, -0.2), (7.4, 7.4, c['h'] + 0.2))
    r = np.hypot(X, Y)
    solid = union(cyl(c['ro'], 0, c['h'], r, Z), cyl(c['flange_r'], 0, c['flange_h'], r, Z))
    solid = np.maximum(solid, r - (c['h'] - Z) - (c['ro'] - 0.3))      # top lead-in for the press fit
    save('tip-collar.stl', sub(solid, cyl(c['ri'], -1, c['h'] + 1, r, Z)), lo)


if __name__ == '__main__':
    node_ring()
    pod_tube()
    pod_body()
    tip_collar()
