"""Separate positive contract for unchanged originals on exact installed native parents.

Does not modify/call the independent zero-dependency or co-import-only contracts.
A caller must authenticate the exact source-specific physical review and all input
receipts before using these structural checks. This module publishes nothing.
"""
from copy import deepcopy
from original_supported_model_only_contract_v1_20261025 import REVIEW_FIELDS

MODES=frozenset(['original','literal','leftF32','balancedF32'])
FORBIDDEN=('sourceWorldBounds','partialSource','partialGeometry','embeddedModel','embeddedModels','retainedBasicSupportDependencies','suppressesBuildingUids','renderGroups')


def verify_metadata(models,sources,supports,original_entries,current):
    assert sources and set(supports)==set(sources)==set(original_entries)
    assert set(supports.values())<=set(current)and not set(supports.values())&set(sources)
    assert len(models)==len({m['uid']for m in models})==len(sources)
    assert {m['uid']:m['sha256']for m in models}==sources
    for model in models:
        uid=model['uid'];parent=current[supports[uid]]
        assert parent['publicationApproved']is True and parent['sourceIdentityReviewed']is True
        assert parent.get('identityReviewApproved')is not False and parent.get('placementReviewed')is not False
        assert parent['rootTranslation']==[-834500,0,816500]and parent.get('verticalPlacementOffsetHKPD',0)==0
        expected=deepcopy(original_entries[uid]);assert expected['uid']==uid and expected['sha256']==sources[uid]
        assert expected['rootTranslation']==[-834500,0,816500]and expected.get('verticalPlacementOffsetHKPD',0)==0
        assert not expected.get('supportDependencies')and not any(expected.get(k)for k in FORBIDDEN)
        expected.update(asset='assets/'+sources[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,supportDependencies=[dict(uid=parent['uid'],state='installed',buildingCSUID=parent['buildingCSUID'],sha256=parent['sha256'])])
        actual=deepcopy(model)
        for field in REVIEW_FIELDS:expected.pop(field,None);actual.pop(field,None)
        assert actual==expected,'Only exact reviewed native dependency and standard original-port metadata are permitted'
    return True


def verify_native_scope(scope,contacts,current,sources,supports,retained,native_count,review):
    assert len(current)==native_count and set(scope['uids'])==set(sources)==set(supports)
    assert set(supports.values())<=set(retained)<=set(current)and not set(sources)&set(current)
    assert review['sourceSpecificPhysicalInterpretationAccepted']is True and review['rawCanonicalFailuresPreserved']is True
    assert review['sourceGeometryChanges']==review['sourcePoseChanges']==0
    assert review['currentManifestSHA256']==scope['currentManifestSHA256']
    assert review['retainedNativeEntries']=={u:current[u]for u in retained}
    assert review['unresolvedExternalBasicContacts']==[]
    expected=set()
    assert len(scope['rows'])==len(sources)
    for row in scope['rows']:
        assert row['uid']in sources and row['sourceSHA256']==sources[row['uid']]and row['currentNativeActorsChecked']==native_count
        for native in row['nearbyNativeActors']:
            assert native['uid']in retained and native['sourceSHA256']==current[native['uid']]['sha256']
            key=(row['uid'],native['uid']);assert key not in expected;expected.add(key)
    assert {n for _,n in expected}==set(retained)
    assert {(u,p)for u,p in supports.items()}<=expected
    rows=contacts['rows'];assert len(rows)==len({(r['uid'],r['nativeUid'])for r in rows})==len(expected)
    assert {(r['uid'],r['nativeUid'])for r in rows}==expected
    accepted=review['acceptedInstalledSupportContacts'];by={(r['uid'],r['nativeUid']):r for r in accepted}
    assert len(by)==len(accepted)==len(sources)and set(by)==set(supports.items())
    for row in rows:
        uid,nuid=row['uid'],row['nativeUid']
        assert row['sourceSHA256']==sources[uid]and row['nativeSHA256']==current[nuid]['sha256']and row['rawCurrentNativeEntry']==current[nuid]
        assert len(row['modes'])==4 and{m['mode']for m in row['modes']}==MODES
        if supports[uid]==nuid:
            approved=by[(uid,nuid)]
            assert approved['physicalInterpretationAccepted']is True and approved['rawContactSummary']==row
            assert all(m['positiveSurfaceContactPairs']>0 and m['finiteContactPairs']>=m['positiveSurfaceContactPairs']and m['areaContactPairs']>=0 for m in row['modes'])
        else:
            assert all(m['finiteContactPairs']==m['positiveSurfaceContactPairs']==m['areaContactPairs']==0 for m in row['modes'])
    return True


def verify_browser_native_scope(config,sources,supports,retained,current,reports):
    assert set(supports)==set(sources)and set(supports.values())<=set(retained)
    assert config['terrain']==[]and not config.get('estimatedBaseUpdates')
    assert set(config['additionalRetainedUids'])==set(retained)
    assert config['nativeSupportUidsByModel']=={u:[p]for u,p in supports.items()}
    assert len(reports)==2
    widths=set()
    for report in reports:
        assert report['passed']and not report['errors'];views=report['retainedNativeOwnViews']
        assert len(views)==2*len(retained)and{(r['uid'],r['time'])for r in views}=={(u,t)for u in retained for t in ['15:00','22:00']}
        report_widths={view['width'] for view in views};assert len(report_widths)==1 and report_widths<={1280,390}
        assert not widths&report_widths;widths.update(report_widths)
        for view in views:
            parent=current[view['uid']]
            assert view['active']and view['visible']and view['fullyFramed']and not view['fallbackFaces']
            assert view['sourceSHA256']==parent['sha256']and view['originalTriangles']==parent['triangles']
            assert view['meshVisibility']and all(view['meshVisibility'])and not any(view['wireframeFlags'])
    assert widths=={1280,390}
    return True
