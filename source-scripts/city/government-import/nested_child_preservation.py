"""Validate the scope of one source-preserving nested terrain replacement."""
import copy
import hashlib
import json


def child_sha(child):
    return hashlib.sha256(json.dumps(child,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def parent_without_retained_child(parent,replacement,child_id,proof):
    children=[c for c in parent.get('patches',[]) if c['id']==child_id]
    assert len(children)==1,'Missing or ambiguous retained child'
    child=children[0]
    assert child.get('nativeMesh') and not child.get('patches'),'Native terrain child required'
    assert proof['supersededChildId']==child_id and proof['supersededChildSHA256']==child_sha(child),'Stale retained child proof'
    assert proof['boundsOfEveryRetainedModelInsideProtectedProjection'] is True
    assert proof['sourceProjectionIntersectionM2']<1e-8,'Retained model intersects new source projection'
    assert set(child['meta']['targetUids'])<=set(replacement['meta']['targetUids']),'Declared target dropped'
    old=child['coarseCells'];new=replacement['coarseCells']
    assert new[0]<=old[0] and new[1]<=old[1] and new[2]>=old[2] and new[3]>=old[3],'Retained region omitted'
    others=[c for c in parent.get('patches',[]) if c['id']!=child_id]
    for other in others:
        c=other['coarseCells']
        assert min(new[2],c[2])<=max(new[0],c[0]) or min(new[3],c[3])<=max(new[1],c[1]),'Replacement overlaps another terrain child'
    updated=copy.deepcopy(parent)
    updated['patches']=[c for c in updated['patches'] if c['id']!=child_id]
    return updated
