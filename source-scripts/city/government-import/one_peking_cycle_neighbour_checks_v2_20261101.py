"""Complete current native/BASIC obligations for the exact private cycle successor.
Reuses unchanged current dependency, before/after neighbour and native policies.
No source modelling, acceptance, public terrain edit or installation.
"""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';SCOPE=P+'cycle-current-scope-v2-20261101';DEPS=P+'cycle-current-dependency-bindings-v2-20261101';BATCH=P+'cycle-neighbour-checks-v2-20261101';BOUNDS=[492.5,-1037.5,1127.5,-592.5]
def context():
 refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 stage=P+'cycle-preparation-v3-20261101';receipt,pins[stage]=authenticate(BASE/stage);refs.append(BASE/stage/'result.json');assert receipt['terrainValidatorPassed']and receipt['newlyDerivedTerrainWorkFaces']==5773
 candidate=take(stage,ROOT/receipt['candidate']['path']);invbatch='government-xl-after-twin-fresh-native-bounds-v1-20261101';inv=take(invbatch,BASE/invbatch/'complete-bounds.json.gz');mp=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(mp.read_bytes());assert msha==receipt['currentManifestSHA256']==inv['currentManifest']['sha256'];manifest=read(mp);refs.append(mp)
 parentref=receipt['replacedNativeTerrain'][0];parentpath=ROOT/'3d-viewer'/parentref['url'];assert digest(parentpath.read_bytes())==parentref['sha256'];prior=read(parentpath);refs.append(parentpath)
 models={};cataloguepaths={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for e in read(path)['models']:assert e['uid']not in models;models[e['uid']]=e;cataloguepaths[e['uid']]=path
 assert len(models)==len(inv['rows'])==7069
 required={r['uid']for r in inv['rows']if any(b[1][0]>=BOUNDS[0]and b[0][0]<=BOUNDS[2]and b[1][2]>=BOUNDS[1]and b[0][2]<=BOUNDS[3]for b in r['completeFourWorldBounds'])}|set(prior['meta']['targetUids']);assert required<=models.keys()
 allforms={};near=set();formtiles={}
 for entry in manifest['tiles']:
  path=ROOT/'3d-viewer'/entry['url'];sha=digest(path.read_bytes());assert sha==inv['currentFormTileHashes'][str(path.relative_to(ROOT))]
  for f in read(path)['buildings']:
   assert f['uid']not in allforms;allforms[f['uid']]=f;formtiles[f['uid']]=path
   points=[p for ring in f.get('rings',[])for p in ring]
   if not points:continue
   points=np.asarray(points);lo,hi=points.min(0),points.max(0)
   if hi[0]>=BOUNDS[0]and lo[0]<=BOUNDS[2]and hi[1]>=BOUNDS[1]and lo[1]<=BOUNDS[3]:near.add(f['uid'])
 parents={allforms[u].get('parent')for u in required}-{None};peer={u for u,f in allforms.items()if u in models and f.get('parent')in parents};wanted=near|required|peer|set(receipt['uids'])
 while True:
  more={d['uid']for u in wanted if u in models for d in models[u].get('supportDependencies',[])};new=wanted|more
  if new==wanted:break
  wanted=new
 assert wanted<=allforms.keys();forms=[allforms[u]for u in sorted(wanted)];refs.extend(formtiles[u]for u in wanted)
 resources=sorted({('building:'if u.startswith('landsd/')else 'source-form:')+u for u in wanted}|{'terrain:'+parentref['url']})
 hashes={str(path.relative_to(ROOT)):digest(path.read_bytes())for path in set(refs)}
 patch=dict(path=receipt['candidate']['path'],sha256=receipt['candidate']['sha256'],uids=receipt['uids'],replaces=dict(url=parentref['url'],sha256=parentref['sha256'],retainedUids=prior['meta']['targetUids']))
 scope=dict(uids=receipt['uids'],currentManifestSHA256=msha,fullChangedLeafEnvelope=BOUNDS,currentNativeActors=7069,touchingNativeUids=sorted(required),geometricallyIntersectingNativeUids=sorted({r['uid']for r in inv['rows']if any(b[1][0]>=BOUNDS[0]and b[0][0]<=BOUNDS[2]and b[1][2]>=BOUNDS[1]and b[0][2]<=BOUNDS[3]for b in r['completeFourWorldBounds'])}),allRetainedTargetUids=prior['meta']['targetUids'],intersectingForms=len(near),completeContextForms=len(forms),resources=resources,installationApproved=False,publication=False)
 inputs=dict(inputHashes=hashes,candidateIds=receipt['uids'],requiredNativeUids=sorted(required),patches=[patch],rows=[dict(building=f,existingNative=f['uid']in models,patchIndexes=[0])for f in forms])
 return scope,inputs,forms,refs,inv

def owned(leasepath):
 lease=read(leasepath);assert reservations.owns(lease);scope,inputs,forms,refs,inv=context();assert set(scope['resources'])==set(lease['resources']);assert not (BASE/SCOPE).exists()and not (BASE/BATCH).exists()
 save(BASE/SCOPE/'scope.json',scope);save(BASE/SCOPE/'neighbour-inputs.json.gz',inputs);save(BASE/SCOPE/'form-obligations.json.gz',forms);save(BASE/SCOPE/'native-obligations.json.gz',[r for r in inv['rows']if r['uid']in scope['touchingNativeUids']]);module('one_peking_cycle_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(SCOPE,'complete-current-envelope-retained-target-peer-and-dependency-scope',list(dict.fromkeys(refs)),scope)
 tool=HERE/'selected_current_installed_dependency_bindings_v2_20261028.py';out=BASE/BATCH;out.mkdir()
 with(out/'dependency-worker.log').open('w')as log:subprocess.run([sys.executable,str(tool),'--batch',DEPS,'--scope',SCOPE],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 dr,dp=authenticate(BASE/DEPS);path=BASE/DEPS/'bindings.json';assert digest(path.read_bytes())==dp[str(path.relative_to(ROOT))];save(out/'installed-dependency-bindings.json',read(path));save(out/'neighbour-inputs.json.gz',inputs);refs.extend([BASE/SCOPE/'result.json',BASE/DEPS/'result.json',path,tool])
 for filename,logname in [('check-neighbours-multi-retained-v1-20261028.mjs','basic-worker.log'),('check-native-neighbours-current-installed-v5-20261028.mjs','native-worker.log')]:
  assert reservations.owns(lease)
  with(out/logname).open('w')as log:subprocess.run(['node',str(HERE/filename),str(out.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  refs.append(HERE/filename)
 basic=read(out/'neighbour-checks.json');native=read(out/'native-neighbour-checks.json');assert set(r['uid']for r in native['rows'])==set(scope['touchingNativeUids']);assert set(r['uid']for r in basic['rows'])=={f['uid']for f in forms}
 for report in [basic,native]:
  for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 result=dict(uids=scope['uids'],currentManifestSHA256=scope['currentManifestSHA256'],currentNativeActors=7069,fullChangedLeafEnvelope=BOUNDS,nativeChecked=len(native['rows']),nativePassed=sum(r['passed']for r in native['rows']),basicChecked=len(basic['rows']),basicFlagged=[dict(uid=r['uid'],existingNative=r['existingNative'],reasons=r['reasons'])for r in basic['rows']if r['reasons']],nativeFailed=[r for r in native['rows']if not r['passed']],allNativePassed=all(r['passed']for r in native['rows']),allBasicPassed=all(not r['reasons']or r['existingNative']for r in basic['rows']),rawFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False)
 save(out/'summary.json',result);module('one_peking_cycle_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-cycle-envelope-basic-and-installed-native-regressions',list(dict.fromkeys(refs)),result);print({k:result[k]for k in ['nativeChecked','nativePassed','basicChecked','basicFlagged']},flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');p.add_argument('--lease');a=p.parse_args()
 if a.owned:return owned(Path(a.lease))
 assert not (BASE/SCOPE).exists()and not (BASE/BATCH).exists();scope,*_=context();claim=reservations.claim('one-peking-complete-cycle-neighbours-'+str(uuid.uuid4()),scope['resources'],batch=BATCH,ttl=3600);assert claim['ok'],claim;leasepath=HERE/'local'/(BATCH+'-control')/'reservation.json';execute_reserved(claim['reservation'],leasepath,[sys.executable,__file__,'--owned','--lease',str(leasepath)])
if __name__=='__main__':main()
