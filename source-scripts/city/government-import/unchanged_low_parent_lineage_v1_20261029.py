"""Prove complete low parent facets survive a derived inset unchanged.

The nominal return envelope may touch an unchanged low facet. This proof uses
complete output lineage and Float32 facet multiplicity, rather than inferring
that any facet touched by that envelope must have been edited.
"""
from collections import Counter
import numpy as np
from unchanged_low_parent_faces_v1_20261024 import face_key, verify


def qualify(before, after, lineage):
    before = np.asarray(before, dtype='<f8')
    after = np.asarray(after, dtype='<f8')
    assert before.ndim == after.ndim == 3
    assert before.shape[1:] == after.shape[1:] == (3, 3)
    assert np.isfinite(before).all() and np.isfinite(after).all()
    rows = lineage['outputLineage']
    assert len(rows) == len(after)
    low_ids = np.flatnonzero(before.astype('<f4')[:, :, 1].min(1) < 1.2).tolist()
    low_set = set(low_ids)
    changed = lineage['changedParentFaces']
    assert len(changed) == len(set(changed))
    assert all(type(i) is int and 0 <= i < len(before) for i in changed)
    assert not low_set.intersection(changed), 'A low parent facet was edited'
    retained = Counter()
    for face, item in zip(after, rows):
        parent = item['parentFace']
        assert type(parent) is int and 0 <= parent < len(before)
        assert item['kind'] in {'unchanged', 'parent-fragment', 'original-inset-or-return'}
        if parent in low_set:
            assert item['kind'] == 'unchanged'
            assert np.array_equal(face, before[parent]), 'Low parent coordinates changed'
            retained[parent] += 1
        elif item['kind'] != 'unchanged':
            assert parent in changed and face[:, 1].min() >= 1.2, 'New surface below clamp'
        if item['kind'] == 'unchanged':
            assert np.array_equal(face, before[parent])
    assert retained == Counter(low_ids), 'Low parent removed or duplicated'
    binding = dict(faceIds=low_ids, keys=Counter(face_key(before[i]) for i in low_ids))
    proof = verify(after, binding)
    return dict(**proof, completeOutputLineageChecked=True,
                lowParentFaces=low_ids, changedLowParentFaces=[],
                everyLowParentRetainedWholeExactlyOnce=True,
                originalCoordinateEquality=True,
                editDefinition='Actual changed parent-facet lineage; nominal buffer is not treated as evidence of deformation.',
                productionGuardChanged=False, terrainPatchValidationPassed=False)
