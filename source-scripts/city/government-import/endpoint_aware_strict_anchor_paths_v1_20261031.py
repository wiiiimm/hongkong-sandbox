"""Choose among existing strict anchors without relaxing the endpoint ceiling.

An absolute minimax search can discard a higher terminal on the same face even
when that terminal admits a path below both endpoints' maximum. Search each
exact terminal-height class separately. Original edges, incidence checks, root
gap limits and the exact zero-rise condition remain in the existing kernel.
"""
from collections import defaultdict
from fractions import Fraction

from original_face_attachment_minimax_v2_20261024 import attachment_paths


def choose_paths(triangles, targets, strict_anchors):
    anchors = list(strict_anchors)
    report = dict(proof=dict(contacts=[]), targets=targets)
    baseline = attachment_paths(triangles, report, [], strict_anchors=anchors)
    selected = list(baseline)
    pending = [i for i, row in enumerate(selected)
               if not row.get('passesExistingEndpointHeight', False)]
    groups = defaultdict(list)
    for anchor in anchors:
        groups[Fraction(float(anchor['position'][1]))].append(anchor)
    searched = []
    for height, group in sorted(groups.items()):
        if not pending:
            break
        rows = attachment_paths(
            triangles,
            dict(proof=dict(contacts=[]), targets=[targets[i] for i in pending]),
            [], strict_anchors=group)
        searched.append(dict(exactTerminalHeight=str(height), anchors=len(group),
                             targets=len(pending)))
        unresolved = []
        for index, row in zip(pending, rows, strict=True):
            assert row['witness'] == baseline[index]['witness']
            assert row['incidentFaces'] == baseline[index]['incidentFaces']
            if row.get('passesExistingEndpointHeight', False):
                assert row['riseAboveEndpointsM'] == 0
                assert row['maximumResidualM'] <= .001
                assert row['terminal']['kind'] == 'canonical-strict-vertical-support-anchor'
                assert row['supportApproved'] is False
                selected[index] = row
            else:
                unresolved.append(index)
        pending = unresolved
    return dict(baseline=baseline, selected=selected, searches=searched,
                remainingIndices=pending, sourceGeometryChanges=0,
                supportApproved=False, endpointToleranceChanged=False,
                newAnchorsCreated=0)
