"""Exact metadata for two original ground-root actors with atomic availability.

No physical support relationship is invented; no source/visual approval is given.
"""
from copy import deepcopy
from original_supported_model_only_contract_v1_20261025 import REVIEW_FIELDS
from original_coordinated_retained_contract_v1_20261027 import FORBIDDEN

def verify_metadata(models,sources,original_entries,ground_owners):
    assert len(sources)==2 and set(original_entries)==set(ground_owners)==set(sources)
    assert len(models)==2 and {m['uid']for m in models}==set(sources)
    return _verify_new_originals(models,sources,original_entries,sorted(sources))

def _verify_new_originals(models,sources,original_entries,group):
    assert len(models)==2 and {m['uid']for m in models}==set(sources)
    assert len(group)==len(set(group)) and set(sources)<=set(group)
    for model in models:
        uid=model['uid'];expected=deepcopy(original_entries[uid])
        assert expected['uid']==uid and expected['sha256']==sources[uid]
        assert expected['rootTranslation']==[-834500,0,816500] and expected.get('verticalPlacementOffsetHKPD',0)==0
        assert not expected.get('supportDependencies') and not any(expected.get(k)for k in FORBIDDEN)
        expected.update(asset='assets/'+sources[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,activationGroup=group)
        actual=deepcopy(model)
        for field in REVIEW_FIELDS:expected.pop(field,None);actual.pop(field,None)
        assert actual==expected,'Only exact originals and complete atomic availability are permitted'
        assert not model.get('supportDependencies'),'Independent original roots cannot acquire invented supports'
    return True

def verify_existing_atomic_group(models,sources,original_entries,ground_owners,before_existing,after_existing):
    assert len(sources)==2 and set(original_entries)==set(ground_owners)==set(sources)
    assert len(before_existing)==len(after_existing)==1 and set(before_existing)==set(after_existing)
    assert not set(before_existing)&set(sources)
    group=sorted(set(sources)|set(before_existing))
    assert _verify_new_originals(models,sources,original_entries,group)
    for uid,before in before_existing.items():
        assert before['uid']==uid and (not before.get('activationGroup') or before['activationGroup']==[uid]), 'Existing atomic group cannot be broken'
        expected=deepcopy(before);expected['activationGroup']=group
        assert after_existing[uid]==expected,'Only atomic availability may change on the existing original'
        assert after_existing[uid]['sha256']==before['sha256']
    return True

def triple_layout(tested,planned,reviewed):
    assert len(tested)==len(planned)==len(reviewed)==3
    old=[r['url']for r in reviewed];new=[r['destination']for r in planned]
    assert len(set(old))==len(set(new))==3 and not set(old)&set(new)
    for before,after,replacement in zip(tested,planned,reviewed):
        assert before['replaces']==after['replaces']==replacement
        assert before['sha256']==after['sha256'] and before['resolution']==after['resolution']
        assert not before.get('replacesMany') and not after.get('replacesMany')
    return set(old),set(new)

def manifest_triple_transition(before,after,planned):
    assert len(planned)==3
    old=[p['replaces']['url']for p in planned];new=[p['destination']for p in planned]
    assert len(set(old))==len(set(new))==3 and not set(old)&set(new)
    assert len(after['terrainPatches'])==len(before['terrainPatches'])
    for url in old:assert sum(p['url']==url for p in before['terrainPatches'])==1 and not any(p['url']==url for p in after['terrainPatches'])
    for url in new:assert sum(p['url']==url for p in after['terrainPatches'])==1
    assert [p for p in after['terrainPatches']if p['url']not in new]==[p for p in before['terrainPatches']if p['url']not in old]
    assert after['counts']==before['counts'] and after['tiles']==before['tiles']
