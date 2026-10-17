import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'source-scripts/city/government-import'))
from run import ROOT,read,save,digest
from heritage_saved_native_bounds_binding_v1_20261014 import bind_record,closed_disjoint
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
base=ROOT/'docs/astra-city/government-import'
old=base/'government-xl-complete-current-native-actual-position-matrix-bounds-v6-20261015'
p=read(old/'input.json.gz');inv=read(old/'inventory.json.gz');manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
models={};assets={}
for url in manifest['officialModelCatalogues']:
 path=ROOT/'3d-viewer'/url
 for e in read(path)['models']:
  assert e['uid'] not in models
  models[e['uid']]=e;assets[e['uid']]=path.parent/e['asset']
forms={}
for tile in manifest['tiles']:
 for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
  if b['uid'] in models:forms[b['uid']]=b
rows={r['uid']:r for r in inv['rows']};domain=[1432.5,-942.5,1607.5,-832.5];touch=[];errors=[]
for d in p['rows']:
 uid=d['uid']
 try:
  assert d['currentBuilding']==forms[uid],'form changed'
  assert digest(assets[uid].read_bytes())==d['source']['sha256'],'source changed'
  boxes=bind_record(models[uid],d,rows[uid])
  if not closed_disjoint(boxes,domain):touch.append(uid)
 except (AssertionError,KeyError) as e:errors.append({'uid':uid,'error':str(e)})
closure=inv['completeRecursiveProductionModuleClosure']['inputHashes']
changed=[path for path,h in closure.items() if digest((ROOT/path).read_bytes())!=h]
new=sorted(set(models)-set(rows));fresh=[]
for uid in new:
 proof=packed_world_bounds(assets[uid].read_bytes())
 fresh.append({'uid':uid,'completeOriginalPOSITIONProof':proof,'originalBoundsDisjoint':closed_disjoint([proof['originalWholeSourceBounds']]*4,domain),'requiresCurrentActualAttributeBinding':True})
result={'currentNativeActors':len(models),'oldActors':len(rows),'oldTupleFailures':errors,'changedProductionClosure':changed,'oldTouchingActors':touch,'newActors':fresh,'domain':domain,'acceptance':False,'newlyInstalled':0}

assert not errors and not changed and new==['landsd/335875:0'] and touch==['landsd/159863:0']
attrdir=base/'government-xl-ets-current-native-attributes-v1-20261015';attrs=read(attrdir/'attributes.json.gz');attrinput=read(attrdir/'input.json.gz')
for path,h in attrs['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
freshrow=next(r for r in attrs['rows']if r['uid']==new[0]);proof=fresh[0]['completeOriginalPOSITIONProof'];assert freshrow['sourceSHA256']==proof['sourceSHA256']
boxes=[proof['originalWholeSourceBounds'],freshrow['completeLiteralWorldBounds'],freshrow['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],freshrow['completeExplicitBalancedFloat32ModelMatrixWorldBounds']];assert closed_disjoint(boxes,domain)
result.update(allCurrentActorsNominated=True,newActorAllFourBounds=boxes,newActorDisjoint=True,touchingNativeUids=touch)
doc=base/'government-xl-ets-native-parent-scope-v1-20261015';assert not doc.exists();doc.mkdir();save(doc/'scope.json',result)
refs=[Path(__file__),old/'input.json.gz',old/'inventory.json.gz',attrdir/'input.json.gz',attrdir/'attributes.json.gz',attrdir/'result.json',ROOT/'3d-viewer/city/data/manifest.json']
refs.extend(assets.values());refs.extend(ROOT/path for path in closure);refs.extend(ROOT/'3d-viewer'/url for url in manifest['officialModelCatalogues']);refs.extend(ROOT/'3d-viewer'/tile['url']for tile in manifest['tiles'])
from run import HERE
from primrose_compound_foundation_v2_20261015 import module
refs.extend(HERE/n for n in ['heritage_saved_native_bounds_binding_v1_20261014.py','exact_packed_world_bounds_v3_20261010.py'])
r=module('ets_native_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(doc.name,'all-current-native-complete-four-world-parent-scope',list(dict.fromkeys(refs)),{'uids':touch+new,'completeNativeActors':len(models),'touchingNativeUids':touch,'fullAcceptance':False,'newlyInstalled':0});print(r['jobId'])
