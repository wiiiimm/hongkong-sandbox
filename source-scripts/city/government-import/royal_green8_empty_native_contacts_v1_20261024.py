"""Emit the native-contact schema for an authenticated empty spatial candidate set.

The catalogue-validation loop remains unchanged. This proof is valid only while
all 6902 current native entries and the current manifest match the bound scope.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from royal_green8_original_catalogue_scope_v1_20261024 import SOURCES
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-royal-green8-five-empty-native-contacts-v1-20261024'
SCOPE='government-xl-royal-green8-five-current-scope-v1-20261024'

def main():
 out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/SCOPE);refs=[Path(__file__),HERE/'royal_green8_original_catalogue_scope_v1_20261024.py',BASE/SCOPE/'result.json']
 # Revalidate all inputs, not just the empty summary. Every current catalogue is bound.
 for key,sha in pins.items():
  p=ROOT/key;assert digest(p.read_bytes())==sha,key;refs.append(p)
 scope=read(BASE/SCOPE/'summary.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert scope['currentManifestSHA256']==digest(manifest.read_bytes())
 current=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
 assert len(current)==len({m['uid']for m in current})==6902 and not set(SOURCES)&{m['uid']for m in current}
 assert set(scope['uids'])==set(SOURCES)and len(scope['rows'])==5
 for r in scope['rows']:assert r['sourceSHA256']==SOURCES[r['uid']]and r['currentNativeActorsChecked']==6902 and not r['nearbyNativeActors']
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,rows=[],nativeCompleteFourWorldSeparation=[],independentlyMeasuredOverlappingNativePairs=[],currentNativeActorsChecked=6902,currentManifestSHA256=digest(manifest.read_bytes()),sourceGeometryChanges=0,installationApproved=False,physicalAcceptance=False,qualification='All current native catalogue hashes and all five complete four-world source bounds are authenticated by the spatial-scope producer. No installed native actor intersects the candidate region; zero native contact pairs are therefore required. The unchanged catalogue-validation loop consumes this empty native-contact schema. Any newly nominated native actor invalidates this exact case and requires separate full contact/regression evidence.')
 save(out/'summary.json',result)
 module('empty_native_schema_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'authenticated-empty-current-native-contact-candidate-set',refs,result)
if __name__=='__main__':main()
