"""Exact Yoho podium/junction pair scope; no general geometry or clearance exception.

The upper original requires the tested lower original and atomic availability.
Only the lower original owns derived ground. Raw interface/compound warnings
remain part of the named source review; old installed models are not reaccepted.
"""
from original_supported_catalogue_scope_v1_20261024 import verify as verify_graph
SOURCES={'landsd/273672:0':'7f0845f30d9f51b2e15b35e39a8be73cfe650bd08a995c290eaed4e3f4812887','landsd/3007:0':'0d07a1036de51674287e9c6b970b257d15fc98af127e67b92bc37b74144affb7'}
SUPPORTS={'landsd/3007:0':'landsd/273672:0'}
GROUND_OWNERS={'landsd/273672:0'}
FACES={'landsd/273672:0':24004,'landsd/3007:0':59}
MODES={'original','literal','leftF32','balancedF32'}
TERRAIN_SHA='087dd7ea4595e574bde13a99a966388620e655ee2608765c3803ef1622616238'
OLD_TERRAIN_SHA='88b282777932ffd64d9414bf86b27f10142c62475e8aa2a34e03719c758d942a'

def verify_models(models):
 assert {m['uid']:m['sha256']for m in models}==SOURCES and len(models)==2
 assert verify_graph(models,SOURCES,SUPPORTS)
 for m in models:
  assert m['triangles']==FACES[m['uid']]and m['activationGroup']==sorted(SOURCES)
  assert m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0
  assert not m.get('retainedBasicSupportDependencies')and not m.get('suppressesBuildingUids')
 assert set(SOURCES)-set(SUPPORTS)==GROUND_OWNERS
 return True

def verify_targets(prior,candidate):
 assert set(prior['meta']['targetUids'])=={'landsd/189427:0'}
 assert set(candidate['meta']['targetUids'])==set(prior['meta']['targetUids'])|GROUND_OWNERS
 assert candidate['coarseCells']==prior['coarseCells']and candidate['meta']['parentTerrain']==prior['meta']['parentTerrain']and candidate['meta']['parentSha256']==prior['meta']['parentSha256']
 return True

def by_mode(rows):
 assert len(rows)==4 and {r['mode']for r in rows}==MODES
 return {r['mode']:r for r in rows}

def verify_authored_junction(strict,roots,census,pairs):
 for r in [strict,roots,census,pairs]:assert r['sourceSHA256ByUid']==SOURCES
 assert strict['supportedUid']=='landsd/3007:0'and strict['supportUid']=='landsd/273672:0'
 s,rt,c,p=map(lambda r:by_mode(r['rows']),[strict,roots,census,pairs])
 for mode in MODES:
  support=s[mode]['support'];foundation=s[mode]['compoundFoundation'];path=rt[mode];faces=c[mode]
  assert support['samples']==40 and support['strictContacts']==6 and len(support['unresolved'])==34
  assert foundation['triangles']==foundation['completeTerrainTriangles']==59 and foundation['fullyBuriedTriangles']==1 and foundation['fullyBuriedUpwardTriangles']==0
  assert path['targets']==path['finiteAttachmentPaths']==34 and path['disconnected']==path['aboveExistingEndpointCeiling']==0 and path['riseAboveEndpointRangeM']==[0.,0.]
  assert faces['fullyBuriedFaceIds']==[10]and faces['fullyBuriedUpwardFaceIds']==[]
  assert faces['sourceWorldSHA256ByUid']==s[mode]['sourceWorldSHA256ByUid']
  pair=p[mode];assert pair['uid']=='landsd/273672:0'and pair['peerUid']=='landsd/3007:0'
  expected=214 if mode in ['original','literal'] else 217
  assert pair['contactDimensions']=={'1':expected}and pair['positiveSurfaceContacts']==expected
 # This binds the specific original wall classification; it never converts a
 # buried floor, changed face, different asset or arbitrary embedding into approval.
 assert census['countsAndAreaExactlyReproduced']is True
 return True

def verify_atomic(report,models):
 assert verify_models(models);ids=sorted(SOURCES);expected={m['uid']:(m['sha256'],m['triangles'])for m in models};cases=report['cases']
 assert report['passed']and not report['pageErrors']and len(cases)==3
 assert {(c['width'],c['failedUid'])for c in cases}=={(1280,None),(390,ids[0]),(390,ids[1])}
 for c in cases:
  assert c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and c['audit']['frames']>0 and not c['audit']['violations']
  transitions=c['audit']['transitions'];assert transitions[0]['active']==transitions[-1]['active']==[]and any(t['active']==ids for t in transitions)
  assert all(t['active']in [[],ids]for t in transitions)
  assert {s['uid']:(s['sha256'],s['triangles'])for s in c['sources']}==expected and all(s['active']for s in c['sources'])
  if c['failedUid']:assert c['failureKeptAllBasics']
 return True

def verify_review(review,models,atomic_report,prior,candidate):
 assert verify_models(models)and verify_atomic(atomic_report,models)and verify_targets(prior,candidate)
 assert review['sourceSHA256ByUid']==review['requiredOriginalAssembly']==SOURCES
 assert review['supportByUid']==SUPPORTS and set(review['terrainOwnerUids'])==GROUND_OWNERS and review['requiredAtomicGroup']==sorted(SOURCES)
 assert review['sourceGeometryChanges']==review['sourcePoseChanges']==0 and review['installedMetadataChanges']is False
 assert all(review[k]is True for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance','completeFourWorldFoundations'])
 assert verify_authored_junction(review['rawCompoundSupport'],review['canonicalRootPaths'],review['compoundFaceCensus'],review['rawOriginalPairContacts'])
 n=review['retainedNativeRegression'];assert n['forms']==review['completeCurrentNeighbourChecks']==259
 assert n['basicFlags']==[]and n['rawBasicFlags']==[dict(uid='landsd/3007:0',reasons=['increased-neighbour-ground-gap'])]
 assert n['coimportRequiredSources']==SOURCES and n['coimportRequiredAtomicGroup']==sorted(SOURCES)and n['coimportedBasicUid']=='landsd/3007:0'
 assert n['legacySupportFailuresReapproved']is False and n['nonregressionOnly']is True
 assert len(n['nativeRows'])==len(n['requiredNativeUids'])==15 and {r['uid']for r in n['nativeRows']}==set(n['requiredNativeUids'])==set(n['nativeResolved'])
 failures={r['uid']for r in n['rawNativeRows']if not r['passed']};assert failures=={'landsd/294858:0','landsd/300857:0'}
 for r in n['nativeRows']:
  assert r['passed']and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0
  if r['uid']in failures:
   assert r['rawNativeRegression']==next(x for x in n['rawNativeRows']if x['uid']==r['uid'])
   assert r['existingNativeReaccepted']is False and r['rawSupportPolicyPassed']is False and r['exactWholeTerrainUnchanged']is True
 return True
