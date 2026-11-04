"""Check the same represented planar partition in an exactly translated frame.

Only union arithmetic is conditioned. Input/output mesh vertices are never edited,
and both established area gates remain strictly below 1e-6 square metres.
"""
from fractions import Fraction
import numpy as np
import shapely


def qualify(parts, expected_parts):
    parts=np.asarray(parts,dtype=object);expected_parts=np.asarray(expected_parts,dtype=object)
    assert len(parts)>0 and len(expected_parts)>0
    all_parts=np.concatenate([parts,expected_parts]);assert shapely.is_valid(all_parts).all()
    coordinates=shapely.get_coordinates(all_parts);assert np.isfinite(coordinates).all()
    anchor=np.zeros(2)
    for axis in range(2):
        values=coordinates[:,axis];first=values[0]
        if first and np.all(values*first>0)and np.min(np.abs(values))>=abs(first)/2 and np.max(np.abs(values))<=abs(first)*2:anchor[axis]=first
    shifted=coordinates-anchor
    for axis in range(2):
        for value in np.unique(coordinates[:,axis]):
            assert Fraction(float(value))-Fraction(float(anchor[axis]))==Fraction(float(value-anchor[axis])), 'Translation must be mathematically exact for every represented coordinate'
    assert np.array_equal(shifted+anchor,coordinates)
    local=shapely.set_coordinates(all_parts.copy(),shifted);cut=len(parts)
    actual=shapely.union_all(local[:cut]);expected=shapely.union_all(local[cut:])
    assert actual.is_valid and expected.is_valid
    area_sum=float(shapely.area(parts).sum());local_sum=float(shapely.area(local[:cut]).sum())
    assert abs(area_sum-local_sum)<1e-6, 'Coordinate conditioning changed represented triangle area'
    overlap=abs(local_sum-actual.area);coverage=float(actual.symmetric_difference(expected).area)
    assert overlap<1e-6, 'Actual partition overlap exceeds established area gate'
    assert coverage<1e-6, 'Actual partition coverage changed beyond established area gate'
    return dict(coordinateAnchor=anchor.tolist(),everyInputTranslationExact=True,everyInputCoordinateRoundtripExact=True,meshGeometryChanged=False,representedAreaSumM2=area_sum,conditionedAreaSumM2=local_sum,conditionedUnionAreaM2=float(actual.area),conditionedOverlapAreaM2=float(overlap),conditionedCoverageDifferenceAreaM2=coverage,rawWorldUnionOverlapAreaM2=abs(area_sum-float(shapely.union_all(parts).area)),rawWorldCoverageDifferenceAreaM2=float(shapely.union_all(parts).symmetric_difference(shapely.union_all(expected_parts)).area),unchangedAreaGateM2=1e-6,qualification='Same source triangle coordinates checked after exact reversible translation. Neither a tolerance increase nor geometry snapping, simplification, approval or publication.')
