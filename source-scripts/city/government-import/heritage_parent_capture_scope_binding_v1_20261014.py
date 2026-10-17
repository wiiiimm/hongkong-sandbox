"""Exact saved scope/certificate binding, no geographic arithmetic."""
import json

def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def bind_scope(scope,certificate,uid):
    forms=scope['scope']['currentProjectedFormsTouching'];actors=[r['building']['uid']for r in forms]
    assert len(forms)==len(set(actors))==23 and uid in actors
    assert all(r['existingNative']is False for r in forms)
    assert certificate['fullParentClosedDomain']==scope['region']
    assert certificate['completeCurrentNativeActors']==6653 and certificate['wholeCurrentNativeTouchingUIDs']==[]
    assert certificate['touchingNativeOutsideNominationScope']==[]
    assert len(certificate['all22PriorUnknownUIDsRetained'])==22
    assert certificate['priorUnknownUIDsProvedOutside']==certificate['all22PriorUnknownUIDsRetained']
    assert len(certificate['rows'])==6653 and len({r['uid']for r in certificate['rows']})==6653
    assert all(r['strictAllFourClosedDomainDisjoint']is True and r['nativeInstallationApprovalTransferred']is False for r in certificate['rows'])
    return forms,sorted(actors)
def bind_current_forms(forms,tiles):
    for r in forms:
        matches=[b for b in tiles[r['tile']]['buildings']if b['uid']==r['building']['uid']]
        assert len(matches)==1 and encoded(matches[0])==encoded(r['building'])
