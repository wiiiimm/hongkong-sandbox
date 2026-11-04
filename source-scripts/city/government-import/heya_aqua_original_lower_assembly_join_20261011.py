"""Exact named Heya original lower-assembly interpretation, never a collision exemption.
All85 proper relative-interior crossings remain. This contract applies only to
these two byte-bound authored meshes and reviewed lowest-façade/perimeter context.
No boundary-only, closed-solid clearance, legal ownership or engineering claim.
"""
import hashlib,json
import numpy as np
from heya_aqua_58_original_terminal_visual_placement_20261011 import UID as T,PODIUM as P
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
SOURCE={T:'f9c73a61b679ebc18df1741c01c7e98463a4269928a38b882e3a41d268646155',P:'46add0484e7cedd20b7de12c9843a2cba8bb419f5824dde27fb9b41fb8efa1b2'}
T_FACES=[17260,17262,17263,17264,17266,17268,17270,17271,17281,17302,17303,17460,17461,17546,17555,17561,17562,17563,17566,17572]
P_FACES=[1203,1204,1207,1208,1209,1210,1211,1212,1214,1215,1218,1219,1220,1221,1222,1223,1224,1225,1228,1229,1230,1231,1232,1233,1234,1235,1238,1239,1240,1241,1242,1243,1246,1247,1254,1255,1258,1259,1260,1261,1264,1265,1266,1267,1268,1269,1271,1272,1275,1276,1277,1278,1280]
RECORD_SHA=['9556d16852ff8d1268a959c90d40538e25f7be92930a26f16136004276db0589','c2831aa59af67fb5a8dff196e0ab1dc4191227a335a070cfafed1eb4c502981b','f3ca2b3f2de0cb4141cfc950f7f9a23ec98e89eadc95c855a5f0e47a17d6d9cd','b6e3816b8e91a388bbf0702dd627b6bcce88795492656f3657176fb36722dcea']
WORLDS={T:['64083b7a54fc708319aa92abb8948beacf689c0b8928dd431ef470d50540c18d','edfb8f6d83f7360e3fc4e0767541456f5d914afe31e59737a13991cb53d162f7','1d1b88106f8f236eceb6763000dfca42e404e32d71e01342155d393fb9bb439f','1d1b88106f8f236eceb6763000dfca42e404e32d71e01342155d393fb9bb439f'],P:['65937caa244bc03136c29d5dd2162efba58a6ccadc54039c26ec303cec3484f3','10cd1f1d9427553ca19210f7849ac8f3318d627bfa46db44103be8ba0d88fe1e','ee70c0d10fa0af8667613decc565c1ed83e34c8de2e7382ae038aedc64a8f90b','ee70c0d10fa0af8667613decc565c1ed83e34c8de2e7382ae038aedc64a8f90b']}
MODEL={T:('3396822186T20151008','B339682218601063C0'),P:('3394422191P20151008','B339442219102063C0')}
def canonical_sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def verify(*,actual,interfaces,native,context,current_forms,provider_sources,identity):
 assert set(actual)=={T,P} and len(current_forms)==14 and len({f['uid']for f in current_forms})==14
 own={u:next(f for f in current_forms if f['uid']==u)for u in [T,P]}
 source={r['uid']:r for r in provider_sources if r['uid']in [T,P]}
 assert set(source)=={T,P} and len([r for r in provider_sources if r['uid']in [T,P]])==2
 for u in [T,P]:
  r=source[u];assert r['sourceSHA256']==SOURCE[u] and r['modelId']==MODEL[u][1]
  assert own[u]==r['source']['building']
  assert own[u]['buildingCSUID']==MODEL[u][0] and own[u]['parent']=='way/1550810360'
  assert own[u]['sourceDataset']=='landsd-territory' and not own[u]['geometryRepaired']
  assert r['native']['cacheKey']=='29d8e67bc139e44d08188938cc2eda2eeb5dc132772d370980aca9b6cd2a3bc1'
  assert r['native']['resultSha']=='e2ed125cbfbdd2ab0bfc72eeab54297e878343e71bd0d92336d4a7673863a101'
  assert r['native']['sheet']=='11-NW-8D' and r['native']['model']['modelId']==MODEL[u][1]
  assert r['native']['model']['asset']['sha256']==SOURCE[u]
  assert actual[u]['sourceSHA256']==SOURCE[u] and actual[u]['sourceGeometryChanges']==actual[u]['terrainGeometryChanges']==0
 assert own[T]['structureType']=='Tower' and own[P]['structureType']=='Podium'
 assert own[T]['baseHeightHKPD']==own[P]['topHeightHKPD']==35.1 # recorded relationship, not fitted actual elevation
 assert identity['uid']==T and identity['sourceSHA256']==SOURCE[T] and identity['passed'] and identity['reasons']==[]
 assert identity['originalOwnership']['fullProjection']['target']['parent']==own[T]['parent']
 assert context['sourceGeometryChanges']==context['terrainGeometryChanges']==0 and context['currentAcceptance'] is False
 assert context['installationApproved'] is False and len(context['rows'])==4 and len(context['images'])==1
 assert len(native['completeCoupledOriginalPrimitiveContext'])==4 and len(interfaces['rows'])==4
 rows=[]
 for k,mode in enumerate(MODES):
  n=next(r for r in native['completeCoupledOriginalPrimitiveContext']if r['arithmetic']==mode)
  i=next(r for r in interfaces['rows']if r['arithmetic']==mode)
  c=next(r for r in context['rows']if r['arithmetic']==mode)
  assert canonical_sha(n)==RECORD_SHA[k] and n['properTriangleInteriorCrossings']==list(range(85))
  records=n['completeTowerPodiumPrimitiveClassifications'];assert len(records)==85
  assert [r['contact']for r in records]==i['allCrossPrimitiveRecordsWithRealComponentBindings']
  assert c['completeContacts']==85 and c['completeAffectedSourceFaceIds']=={T:T_FACES,P:P_FACES}
  assert c['completeCrossComponentCounts']=={'(4, 0)':74,'(4, 9)':11} and c['noBoundaryOnlyContactOrEngineeringConclusion']
  for u,ids in [(T,T_FACES),(P,P_FACES)]:
   a=actual[u]['completeWorldStreams'][mode];w=np.asarray(a['completeWorldTriangles'],dtype='<f8')
   assert len(w)==(17910 if u==T else 3844) and np.isfinite(w).all()
   assert sha(w)==a['completeWorldTriangleSHA256']==i['completeWorldHashes'][u]==WORLDS[u][k]
   assert c['completeAffectedWholeFacetBounds'][u]==[w[ids].min((0,1)).tolist(),w[ids].max((0,1)).tolist()]
   parts=i['completeActualTopologies'][u]['sharedEdgeConnectedComponents']
   assert all(f in (parts[4] if u==T else parts[0]+parts[9])for f in ids)
  for r in records:
   contact=r['contact'];classification=r['exactFiniteContactClassification']
   assert contact['towerComponent']==4 and contact['podiumComponent']in [0,9]
   assert classification['properTriangleInteriorCrossing'] and not classification['coplanarExact']
   assert not classification['structuralSupportCredit'] and not classification['volumetricCollisionProved']
  rows.append(dict(arithmetic=mode,completeExactContactRecordSHA256=RECORD_SHA[k],completeProperCrossingsRetained=85,completeAffectedTowerFaceIds=T_FACES,completeAffectedPodiumFaceIds=P_FACES,sourceRole='unchanged source-owned tower lower-façade / podium upper-perimeter assembly join',boundaryOnlyClaim=False,solidClearanceClaim=False,engineeringClaim=False,legalOwnershipClaim=False,foreignCollisionExemption=False))
 return dict(rows=rows,originalProperCrossingsRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,terrainGeometryChanges=0,engineeringSupportCertified=False,installedPodiumReapproved=False,otherForeignActorsExcludedFromInterpretation=True)
