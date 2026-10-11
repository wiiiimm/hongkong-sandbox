"""Finite clearance v2: exact same-column collapsed-facet refinement.

The immutable v1 ordinary prism proof remains verbatim. Collapsed projections
are bounded by the complete exact finite two-triangle barycentric polytope,
instead of unrelated global height extrema. Full closed-facet coverage is an
independent requirement; no face, threshold, support or source geometry changes.
"""
from fractions import Fraction as F
import numpy as np
from exact_original_paired_finite_clearance_20261010 import verify as prior_verify
from exact_original_triangle_pair_column_gap_20261010 import verify as column_verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage

def refine(face,ground,prior):
    import hashlib
    source=np.asarray(face,float);terrain=np.asarray(ground,float)
    assert prior['sourceFaceSHA256']==hashlib.sha256(source.tobytes()).hexdigest()
    assert prior['completeCurrentGroundSHA256']==hashlib.sha256(terrain.tobytes()).hexdigest()
    pieces=[];gaps=[]
    for p in prior['allExactFiniteSourceGroundPieces']:
        j=p['originalGroundFace'];assert isinstance(j,int) and 0<=j<len(terrain)
        if p.get('collapsedProjectionConservative'):
            exact=column_verify(source,terrain[j])
            assert exact['exactClosedHorizontalProjectionsMeet']
            gaps.append(F(exact['exactMinimumFiniteColumnGapM']))
            pieces.append(dict(originalGroundFace=j,priorConservativeCollapsedProofVerbatim=p,
                               exactCompleteFiniteColumnProof=exact))
        else:
            pieces.append(dict(originalGroundFace=j,priorOrdinaryPrismProofVerbatim=p))
            if 'exactMinimumGapM' in p:gaps.append(F(p['exactMinimumGapM']))
    assert gaps
    coverage=exact_coverage(source,terrain);bound=min(gaps)
    return dict(contract='exact-original-source-prism-complete-finite-column-clearance-v2',
                rawPriorPairedProofVerbatim=prior,completeOriginalProjectionCoverage=coverage,
                groundProjectionCovered=coverage['exactProjectionCovered'],
                allExactFiniteSourceGroundPieces=pieces,exactCertifiedLowerClearanceM=str(bound),
                existingOrdinaryClearanceBoundProved=coverage['exactProjectionCovered'] and bound>=F(-1,2),
                sourceFaceSHA256=prior['sourceFaceSHA256'],completeCurrentGroundSHA256=prior['completeCurrentGroundSHA256'],
                sourcePlaneInversionUsed=False,noGroundOrSourceFaceOmitted=True,rawPriorDiagnosticChanged=False,
                sourceGeometryChanges=0,rootOrContactCredit=False,fullAcceptance=False,installationApproved=False)

def verify(face,ground):return refine(face,ground,prior_verify(face,ground))
