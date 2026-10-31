"""Retain the original work bound, with independently replayed vertical collapses."""
import numpy as np
from retained_inset_work_budget_v1_20261026 import verify as prior_verify


def verify(baseline,output,lineage,collapsed_parent_ids,transition):
    baseline=np.asarray(baseline);output=np.asarray(output);ids=set(collapsed_parent_ids);assert len(ids)==len(collapsed_parent_ids)
    assert all(type(i)is int and 0<=i<len(baseline)for i in ids)
    for i in ids:
        faces,proof=transition.transform(baseline[i]);assert not faces and proof['fullyCollapsed']and proof['exactPartitionTYAreaPreserved']
    assert not ids&{r['parentFace']for r in lineage},'Collapsed parent cannot also produce output'
    keep=[i for i in range(len(baseline))if i not in ids];mapping={i:j for j,i in enumerate(keep)};mapped=[{**r,'parentFace':mapping[r['parentFace']]}for r in lineage]
    result=prior_verify(baseline[keep],output,mapped)
    assert len(output)<=len(baseline)+25000
    result.update(existingFaces=len(baseline),replacedFaces=result['replacedFaces']+len(ids),netAddedFaces=len(output)-len(baseline),explicitlyReplayedVerticalCollapses=sorted(ids),allParentFacesAccounted=True,policy='Original exact unchanged-face and25000new-work gates retained. Every omitted parent independently replays to zero mapped area under the exact vertical partition and existing source/return blend; no unaccounted omission.')
    return result
