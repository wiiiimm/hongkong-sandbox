"""Independent conservative finite-facet bound; raw diagnostics stay unchanged.

The complete source triangle and every bounding-overlapping original terrain
triangle are retained. Exact projected coverage is separately recomputed. This
proves a lower bound using finite vertex extrema, without inverting a nearly
vertical source plane. The existing -.5 m clearance limit is unchanged.
No caller receives import approval or permission to overwrite earlier metrics.
"""
import hashlib
from fractions import Fraction
import numpy as np
from exact_original_projection_coverage_20261009 import exact_coverage
def verify(face,ground):
 source=np.asarray(face,float);terrain=np.asarray(ground,float);assert source.shape==(3,3) and terrain.ndim==3 and terrain.shape[1:]==(3,3) and len(terrain) and np.isfinite(source).all() and np.isfinite(terrain).all()
 lo=source[:,[0,2]].min(axis=0);hi=source[:,[0,2]].max(axis=0);xz=terrain[:,:,[0,2]];ids=np.flatnonzero(np.all(xz.max(axis=1)>=lo,axis=1)&np.all(xz.min(axis=1)<=hi,axis=1));assert len(ids),'Missing finite drawn-ground projection'
 selected=terrain[ids];coverage=exact_coverage(source,selected)
 low=Fraction.from_float(float(source[:,1].min()));high=Fraction.from_float(float(selected[:,:,1].max()));bound=low-high
 return dict(contract='exact-original-facet-conservative-vertex-clearance-v1',completeOriginalProjectionCoverage=coverage,groundProjectionCovered=coverage['exactProjectionCovered'],allProjectedBoundingCandidateOriginalGroundFacets=list(map(int,ids)),exactMinimumOriginalSourceHeightM=str(low),exactMaximumAllCandidateOriginalGroundHeightM=str(high),exactCertifiedLowerClearanceM=str(bound),existingOrdinaryClearanceBoundProved=coverage['exactProjectionCovered'] and bound>=Fraction.from_float(-.5),sourceFaceSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeCurrentGroundSHA256=hashlib.sha256(terrain.tobytes()).hexdigest(),sourcePlaneInversionUsed=False,rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False)
