"""Seek a passing existing strict endpoint; preserve failed minimax diagnostics.

Minimising absolute path height can prefer a low terminal whose route exceeds
its endpoints, even when another authenticated terminal has a valid route.
No root, geometry, incidence or endpoint limit is created or changed here.
"""
from copy import deepcopy
from original_face_attachment_minimax_v2_20261024 import attachment_paths


def passed(row):
    return (row.get('hasUnrestrictedFiniteAttachment') is True
            and row.get('passesExistingEndpointHeight') is True
            and row.get('riseAboveEndpointsM') == 0
            and row.get('maximumResidualM', float('inf')) <= .001)


def retry_paths(triangles, previous, anchors):
    output, attempts = [], []
    for old in previous:
        row = deepcopy(old)
        if not passed(old):
            incident = set(old['incidentFaces'])
            # Try direct same-face contacts first, then other existing roots.
            ordered = sorted(enumerate(anchors), key=lambda pair:
                             (not bool(incident & set(pair[1]['incidentFaces'])), pair[0]))
            target = dict(witness=old['witness'], incidentFaces=old['incidentFaces'])
            for index, anchor in ordered:
                candidate, = attachment_paths(triangles, dict(targets=[target],
                    proof=dict(contacts=[])), [], strict_anchors=[anchor])
                attempts.append(dict(sampleIndex=old['witness']['sampleIndex'],
                                     anchorIndex=index, passed=passed(candidate)))
                if passed(candidate):
                    row = candidate
                    break  # One complete witness is sufficient; no exhaustive search.
        output.append(row)
    return output, attempts
