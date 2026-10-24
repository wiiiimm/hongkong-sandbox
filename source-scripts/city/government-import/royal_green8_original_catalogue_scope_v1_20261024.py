"""Closed five-source Royal Green scope; no installed actor may be a hidden peer."""
from original_supported_catalogue_scope_v1_20261024 import verify as verify_supports
from royal_green8_five_physical_review_v1_20261024 import SOURCES, SUPPORTS
PARENT='landsd/233190:0'
RETAINED=set()

def verify_metadata(models):
 assert verify_supports(models,SOURCES,SUPPORTS)
 for m in models:
  assert m['rootTranslation']==[-834500,0,816500]and m.get('verticalPlacementOffsetHKPD',0)==0
  for k in ['retainedBasicSupportDependencies','sourceWorldBounds','partialSource','partialGeometry','embeddedModel','embeddedModels','renderGroups','suppressesBuildingUids']:assert not m.get(k)
 return True

def verify_native_scope(scope,native,current):
 assert len(current)==6902 and not set(SOURCES)&set(current)
 assert set(scope['uids'])==set(SOURCES)and len(scope['rows'])==5
 assert not native['nativeCompleteFourWorldSeparation']and not native['independentlyMeasuredOverlappingNativePairs']
 for r in scope['rows']:
  assert r['sourceSHA256']==SOURCES[r['uid']]and r['currentNativeActorsChecked']==6902
  assert not r['nearbyNativeActors'],'Any nearby installed actor requires a separate full regression, outside this closed case'
 return True
