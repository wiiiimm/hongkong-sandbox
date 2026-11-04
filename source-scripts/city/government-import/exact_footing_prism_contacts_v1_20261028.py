"""Exact foreign surface clipping against a rendered vertical BASIC footing.

This detects surface-in-volume contacts, including wholly contained triangles.
It does not establish whether the footing is inside a foreign closed solid.
"""
from fractions import Fraction as F
import numpy as np


def clip(points, plane):
    if not points:
        return []
    out = []
    for a, b in zip(points, points[1:] + points[:1]):
        da, db = plane(a), plane(b)
        if da >= 0:
            out.append(a)
        if (da < 0 < db) or (db < 0 < da):
            t = da / (da - db)
            out.append(tuple(x + t * (y - x) for x, y in zip(a, b)))
    return list(dict.fromkeys(out))


def prism_planes(cap, bottom, top):
    cap = [tuple(F(float(v)) for v in p) for p in cap]
    area = ((cap[1][0]-cap[0][0])*(cap[2][2]-cap[0][2])
            - (cap[1][2]-cap[0][2])*(cap[2][0]-cap[0][0]))
    assert area
    sign = 1 if area > 0 else -1
    planes = []
    for a, b in zip(cap, cap[1:] + cap[:1]):
        planes.append(lambda p, a=a, b=b: sign * (
            (b[0]-a[0])*(p[2]-a[2])-(b[2]-a[2])*(p[0]-a[0])))
    lo, hi = F(float(bottom)), F(float(top))
    assert lo < hi
    return planes + [lambda p: p[1]-lo, lambda p: hi-p[1]]


def surface_contacts(triangles, caps, bottom, top):
    triangles, caps = np.asarray(triangles), np.asarray(caps)
    assert triangles.ndim == caps.ndim == 3 and triangles.shape[1:] == caps.shape[1:] == (3, 3)
    assert np.isfinite(triangles).all() and np.isfinite(caps).all()
    bounds_lo, bounds_hi = triangles.min(1), triangles.max(1)
    records, tested = [], 0
    for cap_id, cap in enumerate(caps):
        lo, hi = cap.min(0), cap.max(0)
        lo[1], hi[1] = bottom, top
        ids = np.flatnonzero(np.all(bounds_hi >= lo, axis=1) & np.all(bounds_lo <= hi, axis=1))
        planes = prism_planes(cap, bottom, top)
        for face in ids:
            tested += 1
            points = [tuple(F(float(v)) for v in p) for p in triangles[face]]
            for plane in planes:
                points = clip(points, plane)
                if not points:
                    break
            if points:
                records.append(dict(sourceFace=int(face), capFace=cap_id,
                                    exactClippedPoints=[[str(v) for v in p] for p in points]))
    return dict(contacts=records, completeForeignFaces=len(triangles),
                closedPrisms=len(caps), exactClipsTested=tested,
                allForeignFacesExamined=True, sourceFacesOmitted=0,
                reverseSolidContainmentProved=False, collisionApproved=False)
