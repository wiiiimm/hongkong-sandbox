"""Closed independent-original contract with exact zero-contact retained natives."""
from original_supported_catalogue_scope_v1_20261024 import verify as support_contract


def verify_metadata(models,sources):
    assert support_contract(models,sources,{})
    for m in models:
        assert m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0
        assert not any(m.get(k)for k in ['sourceWorldBounds','partialSource','partialGeometry','embeddedModel','embeddedModels','retainedBasicSupportDependencies','suppressesBuildingUids','renderGroups'])
    return True


def verify_native_scope(scope,contacts,current,sources,retained,native_count):
    assert set(scope['uids'])==set(sources)
    expected=set()
    for r in scope['rows']:
        assert r['uid']in sources and r['sourceSHA256']==sources[r['uid']]and r['currentNativeActorsChecked']==native_count
        for n in r['nearbyNativeActors']:
            assert n['uid']in retained and current[n['uid']]['sha256']==n['sourceSHA256']
            expected.add((r['uid'],n['uid']))
    assert {n for _,n in expected}==set(retained)
    rows=[r for r in contacts['rows']if r['uid']in sources]
    assert len(rows)==len({(r['uid'],r['nativeUid'])for r in rows})==len(expected)
    assert {(r['uid'],r['nativeUid'])for r in rows}==expected
    for r in rows:
        assert r['sourceSHA256']==sources[r['uid']]and r['nativeSHA256']==current[r['nativeUid']]['sha256']
        assert r['rawCurrentNativeEntry']==current[r['nativeUid']]
        assert len(r['modes'])==4 and{m['mode']for m in r['modes']}=={'original','literal','leftF32','balancedF32'}
        assert all(m['finiteContactPairs']==m['positiveSurfaceContactPairs']==m['areaContactPairs']==0 for m in r['modes'])
    return True
