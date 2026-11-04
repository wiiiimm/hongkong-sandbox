"""Atomic descriptor and manifest invariants for two reviewed terrain replacements."""

def pair_layout(tested, planned, reviewed):
    assert len(tested)==len(planned)==len(reviewed)==2
    old=[r['url']for r in reviewed];new=[r['destination']for r in planned]
    assert len(set(old))==len(set(new))==2 and not set(old)&set(new)
    for before,after,replacement in zip(tested,planned,reviewed):
        assert before['replaces']==after['replaces']==replacement
        assert before['sha256']==after['sha256']and before['resolution']==after['resolution']
        assert not before.get('replacesMany')and not after.get('replacesMany')
    return set(old),set(new)


def manifest_pair_transition(before,after,planned):
    assert len(planned)==2
    old=[p['replaces']['url']for p in planned];new=[p['destination']for p in planned]
    assert len(set(old))==len(set(new))==2 and not set(old)&set(new)
    assert len(after['terrainPatches'])==len(before['terrainPatches'])
    for url in old:assert sum(p['url']==url for p in before['terrainPatches'])==1 and not any(p['url']==url for p in after['terrainPatches'])
    for url in new:assert sum(p['url']==url for p in after['terrainPatches'])==1
    assert [p for p in after['terrainPatches']if p['url']not in new]==[p for p in before['terrainPatches']if p['url']not in old]
    assert after['counts']==before['counts']and after['tiles']==before['tiles']
