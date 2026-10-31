"""Exact single-entry availability annotation; no asset or review-flag updates."""
from copy import deepcopy

def verify(before,after,uid,group):
    assert len(group)==3 and len(set(group))==3 and group==sorted(group) and uid in group
    assert len(before['models'])==len({m['uid']for m in before['models']})
    assert sum(m['uid']==uid for m in before['models'])==1
    expected=deepcopy(before);entry=next(m for m in expected['models']if m['uid']==uid)
    assert not entry.get('activationGroup') or entry['activationGroup']==[uid], 'Existing activation group cannot be broken'
    entry['activationGroup']=group
    assert after==expected,'Only activationGroup on the exact existing entry may change'
    return dict(uid=uid,sourceSHA256=entry['sha256'],existingGeometryAndReviewFieldsUnchanged=True,activationGroup=group)
