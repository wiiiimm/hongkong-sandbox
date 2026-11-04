"""Every original sample under existing ordinary limits; no geometry-role credit.

Ordinary clearance remains -.5 m, rim maximum1 m and genuine anchors ±.1 m.
Full-facet clearance, complete component support, all foreign actors and runtime/
source/current bindings remain separate mandatory application checks.
"""
import numpy as np
from original_wall_rim_accounting_20261009 import original_samples

def verify(position,index,bottom,all_samples,*,expected_metric):
    expected=original_samples(position,index,bottom)
    assert len(all_samples)==len(expected)==expected_metric['checks'],'Incomplete original sample inventory'
    low=[]
    for actual,source in zip(all_samples,expected):
        assert all(actual[k]==v for k,v in source.items()),'Misattributed original sample'
        assert source['originalIncidentFaces'],'Unreferenced original vertex'
        assert np.isfinite([actual['ground'],actual['gap']]).all(),'Missing drawn ground'
        assert actual['gap']==actual['point'][1]-actual['ground'],'Changed drawn-ground gap'
        assert actual['gap']>=-.5,'Ordinary original clearance failure'
        if actual['point'][1]<=bottom+.35:
            low.append(actual)
            assert actual['gap']<=1,'Ordinary original rim maximum failure'
    assert low and len(low)==expected_metric['lowRimChecks'],'Incomplete original low rim'
    assert min(r['gap'] for r in all_samples)==expected_metric['minSurfaceGap']
    assert min(r['gap'] for r in low)==expected_metric['minLowGap']
    assert max(r['gap'] for r in low)==expected_metric['maxLowGap']
    anchors=[r for r in low if -.1<=r['gap']<=.1]
    assert anchors,'Missing genuine strict original support anchor'
    assert min(r['gap'] for r in low)<=.1
    return {'contract':'unchanged-original-ordinary-rim-accounting-v1','verified':True,
            'wholeOriginalRuntimeSamples':len(all_samples),'originalLowRimSamples':len(low),
            'strictOriginalAnchorSamples':len(anchors),
            'ordinaryClearanceMinimumM':min(r['gap'] for r in all_samples),
            'ordinaryLowRimMinimumM':min(r['gap'] for r in low),
            'ordinaryLowRimMaximumM':max(r['gap'] for r in low),
            'rawStricterResolverLowerRimSamplesRetained':sum(r['gap']<-.1 for r in low),
            'ordinaryClearanceMinimumLimitM':-.5,'contactMinimumUpperLimitM':.1,
            'rimMaximumLimitM':1,'strictAnchorBandM':[-.1,.1],
            'wallRoleCredit':False,'belowGradeRoleCredit':False,'installationApproved':False}
