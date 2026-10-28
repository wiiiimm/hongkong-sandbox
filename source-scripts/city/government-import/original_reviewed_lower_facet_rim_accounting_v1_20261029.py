"""Account for every unchanged sample with explicitly reviewed lower-facet roles.

The ordinary limits and genuine ordinary anchor remain unchanged. This function
does not approve the supplied roles or replace complete foundation/face checks.
"""
import numpy as np
from original_wall_rim_accounting_20261009 import original_samples


def verify(position, index, bottom, all_samples, *, approved_roles,
           source_role_review_approved, expected_metric):
    assert source_role_review_approved is True and approved_roles
    triangles = np.asarray(position).reshape(-1, 3)[np.asarray(index).reshape(-1, 3)]
    for face, role in approved_roles.items():
        assert type(face) is int and 0 <= face < len(triangles)
        t = triangles[face]
        n = np.cross(t[1] - t[0], t[2] - t[0])
        length = float(np.linalg.norm(n))
        assert length > 0
        ratio = float(n[1] / length)
        assert role in {'wall', 'downward-skin'}
        assert abs(ratio) < .25 if role == 'wall' else ratio < -.25
    expected = original_samples(position, index, bottom)
    assert len(all_samples) == len(expected) == expected_metric['checks']
    low, ordinary, retained = [], [], []
    for actual, source in zip(all_samples, expected):
        assert all(actual[k] == value for k, value in source.items())
        incident = source['originalIncidentFaces']
        assert incident and np.isfinite([actual['ground'], actual['gap']]).all()
        assert actual['gap'] == actual['point'][1] - actual['ground']
        wholly_reviewed = all(f in approved_roles for f in incident)
        if actual['gap'] < -.5:
            assert wholly_reviewed, 'Unreviewed source clearance failure'
            retained.append(actual)
        if actual['point'][1] <= bottom + .35:
            low.append(actual)
            assert actual['gap'] <= 1, 'Original rim maximum exceeded'
            if not wholly_reviewed:
                ordinary.append(actual)
                assert -.5 <= actual['gap'] <= 1
    assert low and ordinary and len(low) == expected_metric['lowRimChecks']
    assert min(r['gap'] for r in all_samples) == expected_metric['minSurfaceGap']
    assert min(r['gap'] for r in low) == expected_metric['minLowGap']
    assert max(r['gap'] for r in low) == expected_metric['maxLowGap']
    anchors = [r for r in ordinary if -.1 <= r['gap'] <= .1]
    assert anchors, 'Missing genuine ordinary source anchor'
    assert min(r['gap'] for r in ordinary) <= .1
    return dict(contract='unchanged-reviewed-lower-facet-rim-accounting-v1',
                verified=True, wholeOriginalRuntimeSamples=len(all_samples),
                originalLowRimSamples=len(low), ordinaryRimSamples=len(ordinary),
                strictOrdinaryAnchorSamples=len(anchors), rawReviewedClearanceFailuresRetained=len(retained),
                approvedRoleByFace=approved_roles, ordinaryClearanceMinimumLimitM=-.5,
                contactMinimumUpperLimitM=.1, rimMaximumLimitM=1, strictAnchorBandM=[-.1, .1],
                roleApprovalGranted=False, physicalAcceptance=False, installationApproved=False)
