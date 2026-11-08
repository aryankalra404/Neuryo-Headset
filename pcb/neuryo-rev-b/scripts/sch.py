"""Schematic helpers: pin endpoint positions of symbol instances, item search."""
import sys, math, uuid as _uuid
sys.path.insert(0, '/home/claude/kw')
from sx import *


def ref_of(sy):
    for p in kids(sy, 'property'):
        if p[1] == 'Reference':
            return p[2]


def lib_pins(lib, lib_id, unit):
    """pins of a lib symbol for given unit (unit 0 = common)."""
    ls = None
    for s in kids(kid(lib, 'lib_symbols'), 'symbol'):
        if s[1] == lib_id:
            ls = s
    out = []
    base = lib_id.split(':')[-1]
    for sub in kids(ls, 'symbol'):
        parts = sub[1].rsplit('_', 2)
        u = int(parts[-2])
        if u not in (0, int(unit)):
            continue
        for p in kids(sub, 'pin'):
            a = kid(p, 'at')
            out.append((str(val(p, 'number')), str(val(p, 'name')), float(a[1]), float(a[2]), float(a[3]) if len(a) > 3 else 0.0, float(val(p, 'length') or 0)))
    return out


def xform(sy, px, py):
    a = kid(sy, 'at')
    X, Y, rot = float(a[1]), float(a[2]), float(a[3]) if len(a) > 3 else 0.0
    mir = val(sy, 'mirror')
    x, y = px, py
    if mir == 'y':
        x = -x
    if mir == 'x':
        y = -y
    r = math.radians(rot)
    xr = x * math.cos(r) - y * math.sin(r)
    yr = x * math.sin(r) + y * math.cos(r)
    return (round(X + xr, 3), round(Y - yr, 3))


def pin_points(s, sy):
    """{pin number: (x, y)} connection points in sheet coordinates"""
    out = {}
    for num, name, px, py, ang, ln in lib_pins(s, val(sy, 'lib_id'), val(sy, 'unit') or 1):
        out[num] = xform(sy, px, py) + (name,)
    return out


def new_uuid():
    return str(_uuid.uuid4())
