"""Exact Yoho source/support/native scope; never authorises publication itself."""
from original_supported_catalogue_scope_v1_20261024 import verify as verify_supports

SOURCES={'landsd/61738:0':'40cf48f2e506dc4aba5b8a28816b99078ae7f7d1b91252c9bae75c03a3ab0928','landsd/231756:0':'d716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167','landsd/122702:0':'0c2d1237e415884793e62fe74685a07ae936d877d535bf89ff5eb0273ff7398b','landsd/56771:0':'f96ce65998446a8de280c071a9e367bfbe58bbc17969857c4fa7dd4acae19a45','landsd/60281:0':'5af938ed04770f6b4826c796d88d9e259e82e0f1a9152cbfe0e6063790478542'}
PARENT='landsd/231756:0';SUPPORTS={u:PARENT for u in ['landsd/122702:0','landsd/60281:0','landsd/56771:0']}
RETAINED={'landsd/58849:0','landsd/121143:0','landsd/146396:0'}
PAIRS={('landsd/61738:0','landsd/58849:0'),(PARENT,'landsd/121143:0'),(PARENT,'landsd/58849:0'),(PARENT,'landsd/146396:0')}

def verify_metadata(models):
    assert verify_supports(models,SOURCES,SUPPORTS)
    for m in models:
        assert m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0
        assert not m.get('retainedBasicSupportDependencies')and not m.get('sourceWorldBounds')
        for field in ['partialSource','partialGeometry','embeddedModel','embeddedModels','renderGroups','suppressesBuildingUids']:assert not m.get(field)
    return True

def verify_native_scope(scope,native,current):
    assert len(current)==6876 and not set(SOURCES)&set(current)
    assert set(scope['uids'])==set(SOURCES)and len(scope['rows'])==5
    nominated=set()
    for row in scope['rows']:
        assert row['uid']in SOURCES and row['sourceSHA256']==SOURCES[row['uid']]and row['currentNativeActorsChecked']==6876
        for n in row['nearbyNativeActors']:
            assert n['uid']in RETAINED and current[n['uid']]['sha256']==n['sourceSHA256'];nominated.add(n['uid'])
    assert nominated==RETAINED
    assert len(native['rows'])==4 and{(r['uid'],r['nativeUid'])for r in native['rows']}==PAIRS
    for row in native['rows']:
        entry=current[row['nativeUid']];assert entry==row['rawCurrentNativeEntry']and entry['sha256']==row['nativeSHA256']
        assert row['sourceSHA256']==SOURCES[row['uid']]and not entry.get('supportDependencies')and not entry.get('retainedBasicSupportDependencies')
        assert len(row['modes'])==4 and{m['mode']for m in row['modes']}=={'original','literal','leftF32','balancedF32'}
    return True

def verify_terrain(patch,expected_sha,actual_sha):
    assert actual_sha==expected_sha and patch['meta']['targetUids']==[PARENT]
    assert len(patch['nativeMesh']['index'])==412*3 and not patch['meta'].get('replaces')
    return True
