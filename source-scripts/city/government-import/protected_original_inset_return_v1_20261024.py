"""Constrain a private terrain return outside exact protected current footprints.

This selects a construction domain, not acceptance. All final terrain/Float32 and
neighbour checks remain mandatory; no building geometry or core is changed.
"""
import shapely


def constrain(core, outer, footprints):
    assert core.is_valid and outer.is_valid and not core.is_empty and not outer.is_empty
    assert outer.covers(core) and core.distance(outer.boundary)>0
    assert footprints and all(p.is_valid and not p.is_empty and p.area>0 for p in footprints)
    protected=shapely.union_all(footprints)
    assert core.disjoint(protected), 'Required authentic inset overlaps a protected current footprint'
    result=outer.difference(protected)
    assert not result.is_empty and result.is_valid and result.covers(core)
    assert core.distance(result.boundary)>0, 'Protected return has no positive width'
    assert result.intersection(protected).area==0
    return result
