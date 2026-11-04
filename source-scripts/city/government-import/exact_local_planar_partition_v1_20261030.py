"""Evaluate unchanged planar partition limits in an exactly reversible local frame."""
import numpy as np
import shapely


def verify(polygons,reference,tolerance=1e-6):
    assert tolerance==1e-6
    polygons=np.asarray(polygons,dtype=object)
    assert len(polygons) and bool(shapely.is_valid(polygons).all()) and reference.is_valid
    bounds=shapely.total_bounds(polygons)
    origin=np.floor(np.minimum(bounds[:2],np.asarray(reference.bounds[:2])))
    def shifted(geometry):
        original=shapely.get_coordinates(geometry)
        local=original-origin
        assert np.array_equal(local+origin,original),'Local arithmetic must preserve every input coordinate'
        result=shapely.transform(geometry,lambda coordinates:coordinates-origin)
        assert np.array_equal(shapely.get_coordinates(result),local)
        return result
    local=shifted(polygons);expected=shifted(reference)
    combined=shapely.union_all(local)
    area_sum=float(shapely.area(local).sum())
    area_error=abs(area_sum-float(combined.area))
    coverage_error=float(combined.symmetric_difference(expected).area)
    assert abs(area_sum-float(shapely.area(polygons).sum()))<tolerance
    assert area_error<tolerance,'Derived terrain overlaps in exact reversible local frame'
    assert coverage_error<tolerance,'Derived terrain does not cover original terrain union'
    return dict(origin=origin.tolist(),inputCoordinateRoundTripExact=True,areaExcessM2=area_error,coverageDifferenceM2=coverage_error,unchangedAreaToleranceM2=tolerance,sourceGeometryChanges=0,tolerancesChanged=False)
