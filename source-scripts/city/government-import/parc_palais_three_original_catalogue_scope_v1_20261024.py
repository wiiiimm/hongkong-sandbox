"""Closed three-original Parc Palais dependency on its unchanged installed podium."""
PARENT='landsd/266063:0'
SOURCES={'landsd/238669:0':'ff0f3b80ffb448a3c2a800e723dcd905b71bef82d68ebd527fe5347e0ccc1bb0','landsd/238671:0':'e5cb9cd513a1fb3882a9f21e07d7b1ba8a151a360d9c996fd2fb5349ca7253d4','landsd/238856:0':'e9d01d1a9b88d9ee1494ef64997ed633e1bfc574344a666e23cae4f5904319ef'}
SUPPORTS={u:PARENT for u in SOURCES};RETAINED={PARENT}
PARENT_SHA='6d53e1cc0aac1942b22783e5416ac75de039e0d50df118a8e7b5b3afd1541586';PARENT_CSUID='3627319038P20060311'
MODES={'original','literal','leftF32','balancedF32'}
COUNTS={'landsd/238669:0':(8391,519,412,242,239),'landsd/238671:0':(10149,445,350,246,246),'landsd/238856:0':(8273,273,230,164,162)}
def verify_support_scope(models,sources,supports):
 assert sources==SOURCES and supports==SUPPORTS
 assert len(models)==3 and{m['uid']:m['sha256']for m in models}==SOURCES
 expected=[dict(uid=PARENT,state='installed',buildingCSUID=PARENT_CSUID,sha256=PARENT_SHA)]
 assert all(m.get('supportDependencies')==expected for m in models)
 return True
def verify_metadata(models):
 assert verify_support_scope(models,SOURCES,SUPPORTS)
 for m in models:
  assert m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0 and m.get('scale',1)==1
  assert m['proceduralWindows']is False
  for field in ['retainedBasicSupportDependencies','sourceWorldBounds','partialSource','partialGeometry','embeddedModel','embeddedModels','renderGroups','suppressesBuildingUids']:assert not m.get(field)
 return True
def verify_native_scope(scope,native,current):
 assert len(current)==6896 and not set(SOURCES)&set(current)
 assert current[PARENT]['sha256']==PARENT_SHA and current[PARENT]['buildingCSUID']==PARENT_CSUID
 assert not current[PARENT].get('supportDependencies')and not current[PARENT].get('retainedBasicSupportDependencies')
 assert len(scope['rows'])==3 and{r['uid']for r in scope['rows']}==set(SOURCES)
 assert len(native['rows'])==3 and{r['uid']for r in native['rows']}==set(SOURCES)
 for r in scope['rows']:
  uid=r['uid'];assert r['sourceSHA256']==SOURCES[uid]and r['currentNativeActorsChecked']==len(current)
  actors=r['nearbyNativeActors'];assert len(actors)==1 and actors[0]['uid']==PARENT and actors[0]['sourceSHA256']==PARENT_SHA
  n=next(n for n in native['rows']if n['uid']==uid);assert n['nativeUid']==PARENT and n['sourceSHA256']==SOURCES[uid]and n['nativeSHA256']==PARENT_SHA and n['rawCurrentNativeEntry']==current[PARENT]
  assert len(n['modes'])==4 and{v['mode']for v in n['modes']}==MODES
  faces,total,positive,literal_total,literal_positive=COUNTS[uid]
  for v in n['modes']:
   assert v['sourceFaces']==faces and v['nativeFaces']==35028 and v['areaContactPairs']==0
   assert v['finiteContactPairs']==(literal_total if v['mode']=='literal'else total)
   assert v['positiveSurfaceContactPairs']==(literal_positive if v['mode']=='literal'else positive)
 return True
