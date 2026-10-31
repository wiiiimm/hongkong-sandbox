"""Exact lower-peer surface coverage; diagnostic only, no source acceptance."""
from fractions import Fraction
import numpy as np
from exact_convex_projection_coverage_v1_20261024 import rational,uncovered,area2
from exact_original_triangle_pair_column_gap_20261010 import verify

def floor_context(source,peers):
    source=np.asarray(source,dtype='<f8');peers=np.asarray(peers,dtype='<f8').reshape(-1,3,3)
    assert source.shape==(3,3)and np.isfinite(source).all()and np.isfinite(peers).all()
    normal=np.cross(source[1]-source[0],source[2]-source[0]);assert normal[1]>.25*np.linalg.norm(normal),'Only explicitly upward source facets'
    poly=rational(source[:,[0,2]]);projections=[rational(t[:,[0,2]])for t in peers]
    assert all(area2(p)!=0 for p in projections)
    missing=uncovered(poly,projections);missing_area=sum((abs(area2(p))/2 for p in missing),Fraction(0));proofs=[verify(source,t)for t in peers];gaps=[Fraction(v['exactGapM'])for p in proofs for v in p['allExactBasicFeasibleColumnVertices']]
    lo,hi=(min(gaps),max(gaps))if gaps else(None,None)
    within=bool(gaps)and lo>=Fraction.from_float(-.1)and hi<=1
    reasons=[]
    if not len(peers):reasons.append('no-positive-area-original-peer-floor-nomination')
    if missing_area:reasons.append('exact-projection-coverage-incomplete')
    if not within:reasons.append('outside-existing-strict-native-interface-interval')
    return dict(sourceProjectedAreaExact=str(abs(area2(poly))/2),uncoveredProjectedAreaExact=str(missing_area),entireClosedProjectionCovered=not missing,exactMinimumLowerFloorGapM=str(lo)if lo is not None else None,exactMaximumLowerFloorGapM=str(hi)if hi is not None else None,withinExistingStrictNativeInterfaceInterval=within,exactlyCoincident=bool(gaps)and all(g==0 for g in gaps),completeLowerPeerCorrespondence=not reasons,reasons=reasons,finitePairProofs=proofs,groundRootCredit=False,strictFoundationAccepted=False,physicalAcceptance=False,sourceGeometryChanges=0)
