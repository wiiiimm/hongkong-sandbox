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
doc=base/'government-xl-ets-current-native-attributes-v1-20261015'
assert not doc.exists();doc.mkdir()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
save(doc/'scope-preflight.json',result)
selected=[]
for uid in touch+new:
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;cat=read(path)
  if any(e['uid']==uid for e in cat['models']):
   entry={**models[uid],'rootTranslation':cat['rootTranslation']};break
 selected.append({'uid':uid,'entry':entry,'building':forms[uid],'path':str(assets[uid].relative_to(ROOT))})
save(doc/'input.json.gz',{'currentManifest':ref(ROOT/'3d-viewer/city/data/manifest.json'),'currentCatalogueRefs':[ref(ROOT/'3d-viewer'/u)for u in manifest['officialModelCatalogues']],'evidenceRefs':[ref(old/'input.json.gz'),ref(old/'inventory.json.gz')],'rows':selected})
import subprocess
from primrose_compound_foundation_v2_20261015 import module
from run import HERE
with (doc/'capture.log').open('w')as log:
 proc=subprocess.run(['node',str(HERE/'ets_current_native_attributes_v1_20261015.mjs'),str((doc/'input.json.gz').relative_to(ROOT)),str((doc/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
save(doc/'command.json',{'exitCode':proc.returncode});assert proc.returncode==0
out=read(doc/'attributes.json.gz');assert out['startEndAllInputsVerified']
for path,h in out['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
# Both actual streams are captured; full native before/after still needs ground
# covering the complete K11 source bounds, beyond the earlier BASIC-only ROI.
save(doc/'next-check.json',{'uid':'landsd/159863:0','completeFaces':32225,'fullBounds':rows['landsd/159863:0']['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],'requiresExpandedGroundCapture':True,'installationApproved':False})
refs=[Path(__file__),HERE/'ets_current_native_attributes_v1_20261015.mjs',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py',HERE/'exact_packed_world_bounds_v3_20261010.py']+[ROOT/path for path in out['inputHashes']]
receipt=module('ets_current_attributes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(doc.name,'current-neighbour-and-new-actor-complete-attributes',refs,{'uids':touch+new,'completeNativeActors':len(models),'oldTupleFailures':[],'changedProductionClosure':[],'fullAcceptance':False,'newlyInstalled':0})
print(json.dumps({'jobId':receipt['jobId'],'capturedFaces':42274,'next':'expanded full K11 terrain regression','newlyInstalled':0}))
