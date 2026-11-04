"""Positive contract for atomic co-imports, retained terrain, unchanged installed entries.

This publishes nothing and does not alter independent/native-parent contracts.
Callers must authenticate exact source-specific physical/visual/terrain receipts.
"""
from copy import deepcopy
from original_supported_catalogue_scope_v1_20261024 import verify as support_contract
from original_supported_model_only_contract_v1_20261025 import REVIEW_FIELDS
MODES={'original','literal','leftF32','balancedF32'}
FORBIDDEN=['sourceWorldBounds','partialSource','partialGeometry','embeddedModel','embeddedModels','retainedBasicSupportDependencies','suppressesBuildingUids','renderGroups']

def verify_metadata(models,sources,supports,original_entries,ground_owners):
 assert 2<=len(sources)<=64 and supports and set(original_entries)==set(sources)
 assert set(ground_owners)==set(sources)-set(supports) and set(supports.values())<=set(sources)
 assert support_contract(models,sources,supports)
 group=sorted(sources)
 for model in models:
  uid=model['uid'];expected=deepcopy(original_entries[uid]);assert expected['uid']==uid and expected['sha256']==sources[uid]
  assert expected['rootTranslation']==[-834500,0,816500]and expected.get('verticalPlacementOffsetHKPD',0)==0
  assert not expected.get('supportDependencies')and not any(expected.get(k)for k in FORBIDDEN)
  expected.update(asset='assets/'+sources[uid]+'.glb.gz',priority='landmark',proceduralWindows=False,activationGroup=group)
  if uid in supports:
   parent=supports[uid];expected['supportDependencies']=[dict(uid=parent,state='installed',buildingCSUID=original_entries[parent]['buildingCSUID'],sha256=sources[parent])]
  actual=deepcopy(model)
  for field in REVIEW_FIELDS:expected.pop(field,None);actual.pop(field,None)
  assert actual==expected,'Only exact original metadata, complete atomic group and declared co-import supports are allowed'
 return True

def verify_retained_entries(current,reviewed,sources,expected_count):
 assert len(current)==expected_count and reviewed and set(reviewed)<=set(current)and not set(sources)&set(current)
 for uid,entry in reviewed.items():assert current[uid]==entry,'Installed metadata, including legacy/negative flags, must remain unchanged'
 return True

def verify_terrain(prior,successor,owners,sources,patch,current_sha,new_sha):
 # Hash arguments MUST be computed from the authenticated complete asset bytes.
 assert patch['status']=='private-nested-coordinated-surface-validator-passed'
 assert patch['candidate']['sha256']==new_sha and len(patch['replacedNativeTerrain'])==1
 replaced=patch['replacedNativeTerrain'][0];assert replaced['sha256']==current_sha
 assert set(patch['uids'])==set(owners)<set(sources)
 assert patch['sourceSHA256ByUid']=={u:sources[u]for u in owners}
 assert patch['bothEffectiveMembersRequired']and patch['retention']['bothExactMembersPresent']and patch['retention']['allParentGridValuesUnchanged']
 assert patch['newlyDerivedTerrainWorkFaces']<=25000
 assert not prior.get('nativeMesh')and not successor.get('nativeMesh')
 assert {k:v for k,v in prior.items()if k not in ['meta','patches']}=={k:v for k,v in successor.items()if k not in ['meta','patches']},'Unrelated outer terrain fields changed'
 a,b=deepcopy(prior['meta']),deepcopy(successor['meta']);oldtargets=set(a.pop('targetUids'));newtargets=set(b.pop('targetUids'))
 assert a==b and oldtargets==set(replaced['retainedUids'])and newtargets==oldtargets|set(owners)
 old=prior['patches'];new=successor['patches'];changed=patch['retention']['replacedChildIndex']
 assert type(changed)is int and 0<=changed<len(old)and len(new)==len(old)+1
 assert sum(x==y for x,y in zip(old,new))==patch['retention']['retainedChildren']==len(old)-1
 assert [i for i,(x,y)in enumerate(zip(old,new))if x!=y]==[changed]
 assert old[changed].get('nativeMesh')and new[changed].get('nativeMesh')and new[-1].get('nativeMesh')
 assert new[changed]['coarseCells']==old[changed]['coarseCells']and set(new[changed]['meta']['targetUids'])==set(old[changed]['meta']['targetUids'])|set(owners)
 assert set(new[-1]['meta']['targetUids'])==set(owners)
 return dict(changedChildIndex=changed,exactRetainedChildren=len(old)-1,appendedChildren=1,outerGridAndMetadataExceptTargetsUnchanged=True,retainedUids=sorted(oldtargets),newGroundOwners=sorted(owners),sourceGeometryChanges=0)

def verify_native_interfaces(physical,scope,contacts,current,sources):
 assert physical['sourceSpecificPhysicalInterpretationAccepted']and physical['completeNeighbourInterpretationAccepted']and physical['rawPhysicalFailuresPreserved']
 assert physical['sourceSHA256ByUid']==sources and physical['sourceGeometryChanges']==physical['sourcePoseChanges']==physical['installedMetadataChanges']==0
 assert physical['unresolvedExternalBasicContacts']==[]and scope['uids']==contacts['uids']
 expected=set()
 for row in scope['rows']:
  assert row['uid']in sources and row['sourceSHA256']==sources[row['uid']]and row['currentNativeActorsChecked']==len(current)
  for neighbour in row['nearbyNativeActors']:
   assert neighbour['sourceSHA256']==current[neighbour['uid']]['sha256'];expected.add((row['uid'],neighbour['uid']))
 assert len(contacts['rows'])==len(expected)and {(r['uid'],r['nativeUid'])for r in contacts['rows']}==expected
 accepted={(r['uid'],r['nativeUid']):r for r in physical['acceptedOriginalNativeInterfaces']}
 assert len(accepted)==len(physical['acceptedOriginalNativeInterfaces'])and set(accepted)<=expected
 for row in contacts['rows']:
  uid,nuid=row['uid'],row['nativeUid'];assert row['sourceSHA256']==sources[uid]and row['nativeSHA256']==current[nuid]['sha256']and row['rawCurrentNativeEntry']==current[nuid]
  assert len(row['modes'])==4 and {m['mode']for m in row['modes']}==MODES
  if(uid,nuid)in accepted:
   role=accepted[(uid,nuid)];assert len(role['allFourWorlds'])==4 and {r['mode']for r in role['allFourWorlds']}==MODES
   for mode in row['modes']:
    reviewed=next(r for r in role['allFourWorlds']if r['mode']==mode['mode']);assert reviewed['sourceSHA256']==sources[uid]and reviewed['nativeSHA256']==current[nuid]['sha256']and reviewed['contactCount']==mode['finiteContactPairs']
  else:assert all(m['finiteContactPairs']==m['positiveSurfaceContactPairs']==m['areaContactPairs']==0 for m in row['modes'])
 return True
