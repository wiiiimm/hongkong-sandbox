"""Exact whole-finite-mesh clearance lower bound; no source-plane inversion."""
from fractions import Fraction
import numpy as np

def verify(source_position,ground_triangles):
    source=np.asarray(source_position,dtype='<f8').reshape(-1,3)
    ground=np.asarray(ground_triangles,dtype='<f8').reshape(-1,3)
    assert len(source)and len(ground)and np.isfinite(source).all()and np.isfinite(ground).all()
    low=Fraction.from_float(float(source[:,1].min()));high=Fraction.from_float(float(ground[:,1].max()));bound=low-high
    return dict(method='exact-complete-source-minimum-minus-complete-ground-maximum',completeSourceVertices=len(source),completeGroundVertices=len(ground),exactSourceMinimumY=str(low),exactGroundMaximumY=str(high),exactClearanceLowerBoundM=str(bound),clearanceLowerBoundM=float(bound),ordinaryClearanceBoundProved=bound>=Fraction(-1,2),allFiniteSourceAndGroundCoordinatesAccounted=True,sourcePlaneInversionUsed=False,projectionCoverageOrContactCredit=False,installationApproved=False)
