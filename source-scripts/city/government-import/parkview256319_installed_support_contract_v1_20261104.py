"""Positive exact-source Parkview16 route; generic installed-parent gates stay unchanged.

Caller authenticates the fresh parent audit, bounded context review and complete
whole-source review. No geometry, raw flags, contacts or numeric limits change.
"""
from copy import deepcopy
from original_installed_support_model_only_contract_v1_20261027 import MODES, FORBIDDEN, verify_browser_native_scope
from original_supported_model_only_contract_v1_20261025 import REVIEW_FIELDS

UID='landsd/256319:0';PARENT='landsd/254491:0';PEER='landsd/256116:0'
SHA='b57eab82a53c67a40eb0f94e64215ca5acbd8f4808fb90610c15425aa21c4193'
PARENT_SHA='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77'
PEER_SHA='d53efca53ef9693232a9ae6ffbf1f3a4596028ad444ed539d96fe1afb407cfb5'

def verify_parent(audit,parent):
    assert audit['uid']==PARENT and audit['sourceSHA256']==PARENT_SHA==parent['sha256']
    assert audit['catalogueSHA256']=='b6847cf99be9220c54a48589b579d22d4191e035b6cd85c67d5cf5507450dcf9'
    assert audit['reviewState']=='installed-verified' and audit['legacyCatalogueFlagFalse'] is True
    assert all(audit[k] is True for k in ['sameCatalogueAsInstalledAcceptance','noLaterHoldOrRejection','evidenceBackedOriginalApprovalReconciliation'])
    assert audit['catalogueChanged'] is False and audit['optimisationApproval'] is False
    assert [e['state']for e in audit['reviewHistory']]==['held','approved-for-integration','installed-verified']
    assert [e['id']for e in audit['reviewHistory']]==[1021,1031,1032]
    assert parent['publicationApproved'] is False and parent['sourceIdentityReviewed'] is True
    assert parent['identityReviewApproved'] is True and parent['placementReviewed'] is True
    assert parent['rootTranslation']==[-834500,0,816500] and parent.get('verticalPlacementOffsetHKPD',0)==0
    return True

def verify_metadata(models,sources,supports,original_entries,current,audit):
    assert sources=={UID:SHA} and supports=={UID:PARENT} and set(original_entries)=={UID}
    assert PARENT in current and UID not in current and verify_parent(audit,current[PARENT])
    assert len(models)==1 and models[0]['uid']==UID and models[0]['sha256']==SHA
    expected=deepcopy(original_entries[UID]);assert expected['uid']==UID and expected['sha256']==SHA
    assert expected['rootTranslation']==[-834500,0,816500] and expected.get('verticalPlacementOffsetHKPD',0)==0
    assert not expected.get('supportDependencies') and not any(expected.get(k)for k in FORBIDDEN)
    expected.update(asset='assets/'+SHA+'.glb.gz',priority='landmark',proceduralWindows=False,
        supportDependencies=[dict(uid=PARENT,state='installed',buildingCSUID=current[PARENT]['buildingCSUID'],sha256=PARENT_SHA)])
    actual=deepcopy(models[0])
    for field in REVIEW_FIELDS:expected.pop(field,None);actual.pop(field,None)
    assert actual==expected,'Only the exact unchanged original and reviewed installed-parent dependency are allowed'
    return True

def verify_native_scope(scope,contacts,current,sources,supports,retained,native_count,review):
    assert sources=={UID:SHA} and supports=={UID:PARENT} and retained=={PARENT,PEER}
    assert len(current)==native_count==7108 and UID not in current and retained<=set(current)
    assert current[PARENT]['sha256']==PARENT_SHA and current[PEER]['sha256']==PEER_SHA
    assert review['sourceSpecificPhysicalInterpretationAccepted'] is True and review['rawCanonicalFailuresPreserved'] is True
    assert review['sourceSHA256ByUid']==sources and review['supportByUid']==supports
    assert review['sourceGeometryChanges']==review['sourcePoseChanges']==0
    assert review['currentManifestSHA256']==scope['currentManifestSHA256']
    assert review['retainedNativeEntries']=={u:current[u]for u in retained}
    assert review['unresolvedExternalBasicContacts']==[]
    context=review['boundedSourceContext']
    assert context['sourceSHA256']==SHA and context['currentManifestSHA256']==scope['currentManifestSHA256']
    assert all(context[k] is True for k in ['sourceSpecificSupportInterpretationAccepted','sourceSpecificBuriedWallInterpretationAccepted','sourceSpecificAdjacentSeamInterpretationAccepted','rawCanonicalFailuresPreserved','negativeParentFlagPreserved'])
    assert context['sourceGeometryChanges']==context['sourcePoseChanges']==0
    assert verify_parent(review['supportEligibilityAudit'],current[PARENT])
    assert scope['uids']==[UID] and len(scope['rows'])==1
    row=scope['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SHA and row['currentNativeActorsChecked']==native_count
    nominated=row['nearbyNativeActors'];assert len(nominated)==2 and{r['uid']for r in nominated}==retained
    assert all(r['sourceSHA256']==current[r['uid']]['sha256']for r in nominated)
    rows=contacts['rows'];assert len(rows)==2 and{(r['uid'],r['nativeUid'])for r in rows}=={(UID,PARENT),(UID,PEER)}
    approved=review['acceptedInstalledSupportContacts']+review['acceptedAdjacentNativeContacts']
    assert len(approved)==2 and{(r['uid'],r['nativeUid'])for r in approved}=={(UID,PARENT),(UID,PEER)}
    for row in rows:
        nuid=row['nativeUid'];assert row['sourceSHA256']==SHA and row['nativeSHA256']==current[nuid]['sha256']
        assert row['rawCurrentNativeEntry']==current[nuid]
        accepted=next(r for r in approved if r['uid']==UID and r['nativeUid']==nuid)
        assert accepted['physicalInterpretationAccepted'] is True and accepted['rawContactSummary']==row
        assert len(row['modes'])==4 and{m['mode']for m in row['modes']}==MODES
        expected=(144,112,0)if nuid==PARENT else(91,73,9)
        assert all((m['finiteContactPairs'],m['positiveSurfaceContactPairs'],m['areaContactPairs'])==expected for m in row['modes'])
    roles=review['completeCurrentNativeContactRoles'];assert len(roles)==8
    assert {(r['nativeUid'],r['mode'])for r in roles}=={(u,m)for u in retained for m in MODES}
    for row in roles:
        assert row['uid']==UID and row['sourceSHA256']==SHA and row['nativeSHA256']==current[row['nativeUid']]['sha256']
        if row['nativeUid']==PEER:
            assert row['contactCount']==91 and row['roles']=={'shared-plane-area-contact':9,'source-edge-surface-contact':16,'surface-point-contact':18,'transverse-surface-crossing':48}
            assert row['contactBounds'][1][2]-row['contactBounds'][0][2]<.008
        else:assert row['contactCount']==144
    return True
