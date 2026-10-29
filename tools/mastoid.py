# Finds the mastoid-bone points M1 (left) and M2 (right) on the shared head and prints them in head.json "extra" format.
# Mastoid process: behind the ear, between ear-canal and earlobe height. The point is placed so a 25 mm wide
# adhesive pad (Neo Gel 32 x 25 mm, long side vertical) clears the back edge of the ear by 3 mm.
# Run from the repo root: python3 tools/mastoid.py [--write]
import json, base64, numpy as np, trimesh
from scipy.ndimage import map_coordinates, spline_filter
H = json.load(open('designs/shared/head/head.json'))
f = H['field']; R = np.frombuffer(base64.b64decode(f['u16_base64']), dtype='<u2').reshape(f['nel'], f['naz']) * f['scale']
RC = spline_filter(R, order=3, mode='nearest')
def rad(az, el):   # skull radius (ears masked and filled), bicubic like the pages
    return float(map_coordinates(RC, [[el + 90], [az % 360]], order=3, mode='nearest', prefilter=False)[0])
def ang(p):
    p = np.asarray(p, float); r = np.linalg.norm(p)
    return np.degrees(np.arctan2(p[0], p[2])) % 360, np.degrees(np.arcsin(p[1] / r))
def surf(az, el):
    A, E = np.radians(az), np.radians(el); u = np.array([np.sin(A) * np.cos(E), np.sin(E), np.cos(A) * np.cos(E)])
    return u * rad(az, el)
m = trimesh.load('designs/shared/head/head.glb').geometry['head']
V = m.vertices
# ear vertices: left side, stick out more than 3 mm beyond the filled skull surface
cand = V[(V[:, 0] > 35) & (V[:, 1] > -60) & (V[:, 1] < 40) & (np.abs(V[:, 2]) < 60)]
out = np.array([np.linalg.norm(p) - rad(*ang(p)) for p in cand])
ear = cand[out > 3]
lobe = np.array(H['lobe']['p']); lpa = np.array(H['sites']['LPA']['xyz'])
y = round((lpa[1] + lobe[1]) / 2, 1)                       # halfway between ear-canal and earlobe height
band = ear[np.abs(ear[:, 1] - y) < 8]
z_back = band[:, 2].min()                                   # back edge of the ear at that height
z = z_back - (12.5 + 3)                                     # pad half-width + clearance
# walk along the skull at height y until the surface point reaches that z
def at_y(az):
    a, b = -60.0, 30.0
    for _ in range(30):
        mid = (a + b) / 2
        if surf(az, mid)[1] < y: a = mid
        else: b = mid
    return (a + b) / 2
azs = np.arange(95, 175, 0.1)
pts = [(az, at_y(az)) for az in azs]
az, el = min(pts, key=lambda t: abs(surf(*t)[2] - z))
p = surf(az, el)
dmin = np.min(np.linalg.norm(ear - p, axis=1))
print('ear back edge z %.1f at y %.1f; target z %.1f' % (z_back, y, z))
print('M1 az %.3f el %.3f xyz %s; nearest ear vertex %.1f mm' % (az, el, p.round(1).tolist(), dmin))
tp9 = np.array(H['extra']['TP9_clear']['xyz']); print('distance to v2 TP9_clear %.1f mm, to TP9 %.1f mm' % (np.linalg.norm(p - tp9), np.linalg.norm(p - np.array(H['sites']['TP9']['xyz']))))
q = p * np.array([-1, 1, 1]); a2, e2 = ang(q)
print(json.dumps({'M1': {'az': round(az, 3), 'el': round(el, 3), 'xyz': p.round(1).tolist()},
                  'M2': {'az': round(a2, 3), 'el': round(e2, 3), 'xyz': q.round(1).tolist()}}))
import sys
if '--write' in sys.argv:   # add M1/M2 to head.json (run again after export.py rebuilds the head)
    H['extra']['M1'] = {'az': round(az, 3), 'el': round(el, 3), 'xyz': p.round(1).tolist()}
    H['extra']['M2'] = {'az': round(a2, 3), 'el': round(e2, 3), 'xyz': q.round(1).tolist()}
    H['extra_notes']['M1'] = 'Left mastoid bone, halfway between ear-canal and earlobe height, %.0f mm behind the back edge of the ear so a 25 mm wide pad clears it (tools/mastoid.py).' % (z_back - z)
    H['extra_notes']['M2'] = 'Mirror of M1.'
    json.dump(H, open('designs/shared/head/head.json', 'w'))
    print('wrote M1, M2 to head.json')
