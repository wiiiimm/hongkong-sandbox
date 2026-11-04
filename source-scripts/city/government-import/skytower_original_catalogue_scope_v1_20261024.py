"""Closed unchanged Skytower source with Elements support and retained Suntower.
These checks bind exact reviewed metadata; they do not approve or publish it.
"""
UID,PARENT,NEIGHBOUR='landsd/204146:0','landsd/273061:0','landsd/204145:0'
SOURCES={UID:'c68e73329b0aa5a6fa5dd00e303f772eafb24b0c6d9bfbf89f28e7e34d806f44'}
SUPPORTS={UID:PARENT};RETAINED={PARENT,NEIGHBOUR}
PARENT_SHA='029934eb9578d41e7ca13b6c1e4583715819749587f1334948cd357da623c21a';PARENT_CSUID='3469118345P20050809'
RETAINED_SHA={PARENT:PARENT_SHA,NEIGHBOUR:'7015f9c5489eb757589cbd5876955dba3f8ffd99187d42bda8661e857493dce3'}
RETAINED_FACES={PARENT:203738,NEIGHBOUR:12129};MODES={'original','literal','leftF32','balancedF32'}
COUNTS={PARENT:{'original':(1663,311,0),'literal':(164,152,0),'leftF32':(1663,311,0),'balancedF32':(1663,311,0)},NEIGHBOUR:{'original':(3625,1342,660),'literal':(3528,1370,680),'leftF32':(3829,1360,644),'balancedF32':(3829,1360,644)}}
def verify_support_scope(models,sources,supports):
 assert sources==SOURCES and supports==SUPPORTS
 assert len(models)==1 and models[0]['uid']==UID and models[0]['sha256']==SOURCES[UID]
 assert models[0].get('supportDependencies')==[dict(uid=PARENT,state='installed',buildingCSUID=PARENT_CSUID,sha256=PARENT_SHA)]
 return True

def verify_metadata(models):
 assert verify_support_scope(models,SOURCES,SUPPORTS);m=models[0]
 assert m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0 and m['proceduralWindows']is False
 for field in ['retainedBasicSupportDependencies','sourceWorldBounds','partialSource','partialGeometry','embeddedModel','embeddedModels','renderGroups','suppressesBuildingUids']:assert not m.get(field)
 return True

def verify_native_scope(scope,native,current):
 assert len(current)==6907 and UID not in current and RETAINED<=set(current)
 for u in RETAINED:assert current[u]['sha256']==RETAINED_SHA[u]and not current[u].get('retainedBasicSupportDependencies')
 assert current[PARENT]['buildingCSUID']==PARENT_CSUID and not current[PARENT].get('supportDependencies')
 assert current[NEIGHBOUR]['supportDependencies']==[dict(uid=PARENT,state='installed',csuid=PARENT_CSUID,sha256=PARENT_SHA)]
 matching=[r for r in scope['rows']if r['uid']==UID];assert len(matching)==1;r=matching[0]
 assert r['sourceSHA256']==SOURCES[UID]and r['currentNativeActorsChecked']==len(current)
 actors=r['nearbyNativeActors'];assert len(actors)==2 and {n['uid']for n in actors}==RETAINED
 for n in actors:assert n['sourceSHA256']==RETAINED_SHA[n['uid']]
 rows=[r for r in native['rows']if r['uid']==UID];assert len(rows)==2 and {r['nativeUid']for r in rows}==RETAINED
 for r in rows:
  u=r['nativeUid'];assert r['sourceSHA256']==SOURCES[UID]and r['nativeSHA256']==RETAINED_SHA[u]and r['rawCurrentNativeEntry']==current[u]
  assert len(r['modes'])==4 and {m['mode']for m in r['modes']}==MODES
  for m in r['modes']:
   assert m['sourceFaces']==10887 and m['nativeFaces']==RETAINED_FACES[u]
   assert (m['finiteContactPairs'],m['positiveSurfaceContactPairs'],m['areaContactPairs'])==COUNTS[u][m['mode']]
 return True
