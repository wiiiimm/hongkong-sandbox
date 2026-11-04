"""Exact retained-parent proof for one disjoint appended native terrain child.

Old grid values, child bodies/order and unrelated metadata must be identical.
Existing coordinated-boundary proofs validate against their exact old parent;
this adapter grants no new boundary, geometry, support or publication approval.
"""
from copy import deepcopy
from contextlib import contextmanager
from nested_coordinated_parent_contract_v1_20261027 import targets
import nested_coordinated_native_boundary_v1_20261027 as boundary
POLICY='exact-retained-parent-disjoint-native-child-append-v1'
FIELD='disjointNativeChildAppend'
ORIGINAL=boundary.coordinated_boundary

def overlaps(a,b):
    return min(a[2],b[2])>max(a[0],b[0])and min(a[3],b[3])>max(a[1],b[1])

def verify_append(parent,reference=boundary.reference):
    marker=parent['meta'][FIELD]
    assert set(marker)=={'policy','proof'}and marker['policy']==POLICY
    proof=reference(marker['proof']);assert set(proof)=={'policy','beforeParent','child','newTargetUids'}and proof['policy']==POLICY
    prior=reference(proof['beforeParent']);child=reference(proof['child']);uids=proof['newTargetUids']
    assert isinstance(uids,list)and 0<len(uids)==len(set(uids))<=20 and all(isinstance(u,str)and u.startswith('landsd/')for u in uids)
    assert not set(uids)&targets(prior),'Target already belongs to retained parent'
    assert prior.get('patches')and not prior.get('nativeMesh')and not prior.get('hydro')
    assert child.get('nativeMesh')and not child.get('patches')and not child.get('hydro')
    assert 'coordinatedBoundary'not in child['nativeMesh']['source'],'New child needs ordinary parent boundaries'
    assert set(child['meta']['targetUids'])==set(uids)
    c=child['coarseCells'];assert len(c)==4 and all(type(v)is int for v in c)
    assert 0<=c[0]<c[2]<prior['w']and 0<=c[1]<c[3]<prior['h']
    assert not any(overlaps(c,p['coarseCells'])for p in prior['patches']),'New child overlaps retained child'
    assert not any(overlaps(c,e)for e in prior.get('patchExclusions',[])),'New child intersects prior exclusion'
    expected=deepcopy(prior);expected['patches'].append(child);expected['meta']['targetUids']=sorted(targets(prior)|set(uids));expected['meta'][FIELD]=deepcopy(marker)
    assert expected==parent,'Retained grid, child, order, metadata or exact new child changed'
    return prior

def coordinated_boundary(patch,parent):
    seen=set()
    while FIELD in parent.get('meta',{}):
        marker=parent['meta'][FIELD];key=(marker['proof']['path'],marker['proof']['sha256']);assert key not in seen and len(seen)<32,'Cyclic or excessive append chain';seen.add(key)
        prior=verify_append(parent)
        if not any(patch==old for old in prior['patches']):break
        parent=prior
    return ORIGINAL(patch,parent)

@contextmanager
def private_validator():
    assert boundary.coordinated_boundary is ORIGINAL
    boundary.coordinated_boundary=coordinated_boundary
    try:yield
    finally:boundary.coordinated_boundary=ORIGINAL
