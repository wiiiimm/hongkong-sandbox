"""Attribute reviewed intersecting walls using the actual import contact policy.

The policy requires minLowGap<=.1, not an ordinary sample in[-.1,.1].
Every ordinary sample retains the -.5m clearance bound and every low sample
retains the1m maximum. Exact current wall/ground crossings and cap eligibility
must be authenticated independently by the caller; no approval is granted here.
"""
import numpy as np
from original_wall_rim_accounting_20261009 import original_samples


def verify(position,index,bottom,all_samples,*,approved_wall_faces,
           wall_role_review_approved,positive_finite_grade_faces,expected_metric):
    assert wall_role_review_approved is True
    walls=set(approved_wall_faces)
    assert walls and len(walls)==len(approved_wall_faces)
    assert all(type(i)is int for i in walls)
    grade=list(positive_finite_grade_faces)
    assert all(type(i)is int for i in grade)and len(set(grade))==len(grade)
    assert set(grade)==walls,'Every reviewed wall needs independent exact grade evidence'
    triangles=np.asarray(position).reshape(-1,3)[np.asarray(index).reshape(-1,3)]
    for i in walls:
        assert 0<=i<len(triangles)
        t=triangles[i];normal=np.cross(t[1]-t[0],t[2]-t[0]);size=float(np.linalg.norm(normal))
        assert size>0 and abs(normal[1])<.25*size
    expected=original_samples(position,index,bottom)
    assert len(all_samples)==len(expected)==expected_metric['checks']
    low=[];ordinary=[];retained=[]
    for actual,source in zip(all_samples,expected):
        assert all(actual[k]==v for k,v in source.items())
        incident=source['originalIncidentFaces'];assert incident
        assert np.isfinite([actual['ground'],actual['gap']]).all()
        assert actual['gap']==actual['point'][1]-actual['ground']
        exclusively_wall=all(i in walls for i in incident)
        if actual['gap']<-.5:
            assert exclusively_wall,'Unreviewed source clearance failure'
            retained.append(actual)
        if source['point'][1]<=bottom+.35:
            low.append(actual)
            assert actual['gap']<=1,'Original low-rim maximum exceeded'
            if not exclusively_wall:
                ordinary.append(actual);assert -.5<=actual['gap']<=1
    assert low and len(low)==expected_metric['lowRimChecks']
    assert min(r['gap']for r in all_samples)==expected_metric['minSurfaceGap']
    assert min(r['gap']for r in low)==expected_metric['minLowGap']
    assert max(r['gap']for r in low)==expected_metric['maxLowGap']
    assert min(r['gap']for r in low)<=.1,'Canonical minimum low-rim contact exceeded'
    return dict(contract='canonical-contact-reviewed-intersecting-wall-rim-accounting-v1',verified=True,
                wholeOriginalRuntimeSamples=len(all_samples),originalLowRimSamples=len(low),ordinaryRimSamples=len(ordinary),
                strictOrdinaryAnchorSamples=sum(-.1<=r['gap']<=.1 for r in ordinary),
                nearZeroOrdinarySampleRequired=False,canonicalMinimumLowGapM=min(r['gap']for r in low),
                rawReviewedClearanceFailuresRetained=len(retained),approvedWallFaces=sorted(walls),
                independentPositiveFiniteGradeFaces=sorted(walls),ordinaryClearanceMinimumLimitM=-.5,
                contactMinimumUpperLimitM=.1,rimMaximumLimitM=1,roleApprovalGranted=False,
                physicalAcceptance=False,installationApproved=False)
