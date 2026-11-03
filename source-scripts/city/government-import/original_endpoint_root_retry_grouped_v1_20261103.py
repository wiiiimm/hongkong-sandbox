"""Batch endpoint retries against authenticated unchanged canonical roots.

Caller must bind the previous complete all-root minimax proof and exact source.
No-path rows and exact global minimum ceilings are proof bounds, not new gates.
One existing kernel invocation per tried root replaces one per target/root pair.
"""
from copy import deepcopy
from fractions import Fraction as F
import numpy as np
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from original_endpoint_root_retry_v1_20261102 import passed
from pool_incident_wall_contacts_v1_20261017 import closest


def retry_paths(triangles, previous, anchors):
    output = deepcopy(previous)
    pending = {i for i, row in enumerate(previous) if not passed(row) and row['hasUnrestrictedFiniteAttachment']}
    attempts = []
    if not pending:
        return output, attempts
    tri = np.asarray(triangles, dtype=float)
    # Keep the same source-incidence/strict-gap requirements for every root,
    # including a root excluded later by the exact height lower bound.
    for root in anchors:
        point = np.asarray(root['position'], dtype=float)
        assert point.shape == (3,) and np.isfinite(point).all()
        assert root['strictAccepted'] is True and root['gap'] == point[1]-root['supportHeight']
        assert -.1 <= root['gap'] <= 1
        assert root['incidentFaces']
        for face in root['incidentFaces']:
            assert 0 <= face < len(tri)
            assert np.linalg.norm(np.cross(tri[face, 1]-tri[face, 0], tri[face, 2]-tri[face, 0])) > 0
            assert np.linalg.norm(closest(point, tri[face])-point) <= .001
    # A higher existing endpoint is more likely to meet the unchanged ceiling;
    # success still requires the complete original kernel's actual path proof.
    ordered = sorted(enumerate(anchors), key=lambda pair: (-F(float(pair[1]['position'][1])), pair[0]))
    for anchor_index, anchor in ordered:
        height = F(float(anchor['position'][1]))
        eligible = [i for i in sorted(pending) if max(F(float(previous[i]['witness']['position'][1])), height) >= F(previous[i]['exactMinimumAttachmentCeilingM'])]
        if not eligible:
            continue
        targets = [dict(witness=previous[i]['witness'], incidentFaces=previous[i]['incidentFaces']) for i in eligible]
        candidates = attachment_paths(tri, dict(targets=targets, proof=dict(contacts=[])), [], strict_anchors=[anchor])
        assert len(candidates) == len(eligible)
        for i, candidate in zip(eligible, candidates):
            assert candidate['witness'] == previous[i]['witness'] and candidate['incidentFaces'] == previous[i]['incidentFaces']
            ok = passed(candidate)
            attempts.append(dict(sampleIndex=previous[i]['witness']['sampleIndex'], anchorIndex=anchor_index, passed=ok))
            if ok:
                output[i] = candidate
                pending.remove(i)
        if not pending:
            break
    return output, attempts
