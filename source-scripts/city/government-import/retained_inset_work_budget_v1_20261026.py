"""Account existing exact terrain separately from at most25,000 new work facets.

This is a private candidate work bound, never source/physical/publication approval.
No output can omit, duplicate or alter a face declared unchanged in its lineage.
"""
import numpy as np


def verify(baseline, output, lineage):
    baseline=np.asarray(baseline);output=np.asarray(output)
    assert baseline.ndim==output.ndim==3 and baseline.shape[1:]==output.shape[1:]==(3,3)
    assert np.isfinite(baseline).all() and np.isfinite(output).all()
    assert len(output)==len(lineage)
    unchanged=set();changed=set();new_count=0
    for face,record in zip(output,lineage):
        i=record['parentFace'];assert type(i)is int and 0<=i<len(baseline)
        if record['kind']=='unchanged':
            assert i not in unchanged and np.array_equal(face,baseline[i]), 'Retained face changed or duplicated'
            unchanged.add(i)
        else:
            assert record['kind']in ['parent-fragment','original-inset-or-return']
            changed.add(i);new_count+=1
    assert not unchanged&changed, 'An unchanged face cannot also be replaced'
    assert unchanged|changed==set(range(len(baseline))), 'Parent facet omitted from lineage'
    assert new_count<=25000, 'new-terrain-work-budget'
    assert len(output)<=len(baseline)+25000, 'retained-plus-new-work-budget'
    return dict(existingFaces=len(baseline),unchangedFaces=len(unchanged),replacedFaces=len(changed),newWorkFaces=new_count,
                newWorkFaceLimit=25000,outputFaces=len(output),netAddedFaces=len(output)-len(baseline),
                allDeclaredUnchangedFacesExact=True,allParentFacesAccounted=True,
                physicalAcceptance=False,installationApproved=False,
                policy='Existing complete installed face multiset is inherited, not newly generated. At most25000 replacement/return facets; ordinary geometry/coverage/edge/clearance/neighbour/device gates remain separate.')
