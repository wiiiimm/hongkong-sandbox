"""Combine individually verified private canopy experiments without approval transfer."""
from copy import deepcopy
from private_canopy_preview_catalogue_v1_20261029 import apply as apply_one


def apply(models, sources, forms, reviews):
    assert 1 < len(reviews) <= 8
    basics = [r['basicUid'] for r in reviews]
    assert len(basics) == len(set(basics))
    manifests = [r['currentManifest'] for r in reviews]
    assert all(m == manifests[0] for m in manifests)
    out = deepcopy(models)
    by = {m['uid']: m for m in out}
    assert len(by) == len(models)
    for review in reviews:
        # Each scalar guard sees the unchanged, unsuppressed input catalogue.
        checked = apply_one(models, sources, forms, review)
        uid = review['sourceUid']
        verified = next(m for m in checked if m['uid'] == uid)
        assert verified['suppressesBuildingUids'] == [review['basicUid']]
        by[uid].setdefault('suppressesBuildingUids', []).append(review['basicUid'])
    return out
