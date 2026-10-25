"""Closed source/retained-native contract for the exact PolyU two-original proposal.

No approval is granted here. Existing independent/co-import contracts are unchanged.
Source-specific physical/visual evidence and publisher leases remain mandatory.
"""
from copy import deepcopy
MAIN='landsd/305600:0';SMALL='landsd/257998:0';LIB='landsd/305793:0';SPORT='landsd/305582:0'
SOURCES={MAIN:'bf063175904023d34a2668b86f4a9be42beac1efbfc280fd969179c7b333787d',SMALL:'1ffdd32f700c9dfaabf8290e602430f4d2fbe120eb81cfeaaddc65e4a0899f6a'}
SUPPORTS={SMALL:LIB}
RETAINED={LIB:'c45253aeb258f6ffa8e56a069a7ed03e2ecf153a75ad0435370a008e525703f5',SPORT:'ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15'}
MODES={'original','literal','leftF32','balancedF32'}
REVIEW_FIELDS={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','aiGeometryModelling','sourceEvidenceInterpretationUsedAI','placementReview'}


def verify_support_scope(models,sources,supports):
 assert sources==SOURCES and supports==SUPPORTS
 assert len(models)==2 and {m['uid']:m['sha256']for m in models}==SOURCES
 for model in models:
  expected=[]if model['uid']==MAIN else[dict(uid=LIB,state='installed',buildingCSUID='3655618355P20060311',sha256=RETAINED[LIB])]
  assert model.get('supportDependencies',[])==expected,'Only the companion has an evidenced library support'
 return True


def verify_metadata(models,original_entries):
 assert verify_support_scope(models,SOURCES,SUPPORTS)and set(original_entries)==set(SOURCES)
 for model in models:
  old=deepcopy(original_entries[model['uid']]);actual=deepcopy(model)
  assert old['uid']==model['uid']and old['sha256']==SOURCES[model['uid']]
  assert old['rootTranslation']==[-834500,0,816500]and old.get('verticalPlacementOffsetHKPD',0)==0
  assert not any(old.get(k)for k in ['supportDependencies','retainedBasicSupportDependencies','sourceWorldBounds','partialSource','partialGeometry','embeddedModel','embeddedModels','renderGroups','suppressesBuildingUids'])
  old.update(asset='assets/'+SOURCES[model['uid']]+'.glb.gz',priority='landmark',proceduralWindows=False)
  if model['uid']==SMALL:old['supportDependencies']=[dict(uid=LIB,state='installed',buildingCSUID='3655618355P20060311',sha256=RETAINED[LIB])]
  for key in REVIEW_FIELDS:old.pop(key,None);actual.pop(key,None)
  assert actual==old,'Source rendering metadata or original pose changed'
 return True


def verify_native_scope(scope,native,current):
 assert len(current)==6929 and not set(SOURCES)&current.keys()
 assert set(scope['uids'])==set(SOURCES)
 expected={(MAIN,LIB),(MAIN,SPORT),(SMALL,LIB)};seen=set()
 for row in scope['rows']:
  assert row['sourceSHA256']==SOURCES[row['uid']]and row['currentNativeActorsChecked']==len(current)
  for n in row['nearbyNativeActors']:
   assert n['sourceSHA256']==RETAINED[n['uid']]==current[n['uid']]['sha256'];seen.add((row['uid'],n['uid']))
 assert seen==expected
 rows=[r for r in native['rows']if r['uid']in SOURCES]
 assert len(rows)==len(expected)and{(r['uid'],r['nativeUid'])for r in rows}==expected
 for row in rows:
  uid,parent=row['uid'],row['nativeUid']
  assert row['sourceSHA256']==SOURCES[uid]and row['nativeSHA256']==RETAINED[parent]
  assert row['rawCurrentNativeEntry']==current[parent]and not current[parent].get('supportDependencies')
  assert len(row['modes'])==4 and{r['mode']for r in row['modes']}==MODES
  for mode in row['modes']:
   fp32=mode['mode']in {'leftF32','balancedF32'}
   contacts=(4338 if fp32 else 468)if uid==MAIN and parent==LIB else(211 if fp32 else 0)if uid==SMALL else 0
   positive=(834 if fp32 else 386)if uid==MAIN and parent==LIB else(8 if fp32 else 0)if uid==SMALL else 0
   assert mode['finiteContactPairs']==contacts and mode['positiveSurfaceContactPairs']==positive and mode['areaContactPairs']==0
   assert mode['sourceFaces']==(10575 if uid==MAIN else 147)and mode['nativeFaces']==(59527 if parent==LIB else 10536)
 assert current[LIB]['publicationApproved']is False and current[SPORT]['publicationApproved']is True
 assert {MAIN,SMALL}<=set(current[LIB]['suppressesBuildingUids'])
 return True
