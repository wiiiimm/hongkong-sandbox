"""Saved positive-area terrain lineage classification; never overlap approval.

The caller computes only bounded ancestor comparisons using existing exact
arithmetic. These labels distinguish introduced coexistence from inheritance;
none changes a sampler, validator, terrain triplet or physical threshold.
"""
from fractions import Fraction as F

KINDS={'originalTIN','capturedCurrentRing'}

def classify(row,ancestor):
    left,right=row['leftProvenance'],row['rightProvenance'];p=row['proof']
    assert left['kind'] in KINDS and right['kind'] in KINDS
    assert left['candidateFace']==row['leftFace'] and right['candidateFace']==row['rightFace']
    assert row['leftFace']<row['rightFace']
    assert p['exactProjectedDimension']=='area' and F(p['exactDoubledAreaM2'])>0
    assert ancestor['exactCandidateProjectionDimension']=='area' and F(ancestor['exactCandidatePairAreaM2'])>0
    for key in ['exactLeftHeightRangeM','exactRightHeightRangeM','exactSignedLeftMinusRightRangeM']:
        assert len(p[key])==2 and F(p[key][0])<=F(p[key][1])
    assert len(ancestor['exactPerLineageHeightDifferenceRangesM'])==2
    for bounds in ancestor['exactPerLineageHeightDifferenceRangesM']:
        assert len(bounds)==2 and F(bounds[0])<=F(bounds[1])
    kinds={left['kind'],right['kind']};same=(left['kind'],left['originalFace'])==(right['kind'],right['originalFace'])
    oldarea=F(ancestor['exactOriginalPairAreaM2']);assert oldarea>=0
    if len(kinds)==2:
        label='introduced original-TIN/current coexistence'
    elif same:
        label='introduced packed fragments of one source facet'
    elif oldarea==0:
        label='introduced packed intersection of formerly non-area ancestors'
    elif not ancestor['projectionInherited']:
        label='ancestral layers with an expanded packed intersection'
    else:
        label='positive-area intersection contained in two ancestral surfaces'
    interval=list(map(F,p['exactSignedLeftMinusRightRangeM']))
    ordering='left never below right' if interval[0]>=0 else 'right never below left' if interval[1]<=0 else 'height order crosses'
    if interval==[F(0),F(0)]:ordering='equal ideal affine heights'
    return dict(classification=label,sameSourceFacet=same,sourcePairHasPositiveArea=oldarea>0,
                candidateProjectionContainedInBothAncestors=ancestor['projectionInherited'],
                exactIdealAffineHeightsInherited=ancestor['heightInherited'],heightOrdering=ordering,
                fullSavedCandidatePairProof=row,completeAncestorComparison=ancestor,
                notCompleteSamplerMAXOrBitwiseJSEquality=True,noCopiedApproval=True,
                validatorPassed=False,physicalAccepted=False,installationApproved=False)

def verify_complete(area_rows,classified):
    expected=[(r['leftFace'],r['rightFace']) for r in area_rows]
    actual=[(r['fullSavedCandidatePairProof']['leftFace'],r['fullSavedCandidatePairProof']['rightFace']) for r in classified]
    assert len(expected)==len(set(expected)) and actual==expected,'Missing, duplicated or reordered saved area pair'
    assert all(r['fullSavedCandidatePairProof']==old for r,old in zip(classified,area_rows)),'Saved proof changed'
    assert all(r['noCopiedApproval'] and not r['physicalAccepted'] and not r['installationApproved'] for r in classified)
    return dict(completeSavedPositiveAreaPairs=len(classified),allRowsExactlyPreserved=True,noNewAllPairsSearch=True,noApprovalWritten=True)
