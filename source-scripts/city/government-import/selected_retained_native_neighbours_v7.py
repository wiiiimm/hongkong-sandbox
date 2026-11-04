"""Full current-region regressions for explicitly pinned native terrain replacements."""
import argparse,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','scope','inventory','patch','bindings']:ap.add_argument('--'+k,required=True)
 ap.add_argument('--resume-from');ap.add_argument('--lease-file',required=True);a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
 base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();refs=[Path(__file__)];receipts={};pins={}
 for name in [a.scope,a.inventory,a.patch,a.bindings]:
  r,p=authenticate(base/name);receipts[name]=r;refs.append(base/name/'result.json')
  for path,h in p.items():assert path not in pins or pins[path]==h;pins[path]=h
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 scope=take(base/a.scope/'scope.json');inventory=take(base/a.inventory/'complete-bounds.json.gz');candidate=receipts[a.patch]['candidate'];replacement=candidate.get('replacesMany')or[candidate['replaces']];allowed={p['url']:p for p in replacement};assert len(allowed)==len(replacement)
 contacts=[x for x in scope['terrainContacts']if x['coarseOverlapAreaM2']>0 or any(p['overlapAreaM2']>0 for p in x['packedContacts'])]
 assert {x['url']for x in contacts}==set(allowed),'Every positive terrain overlap needs an exact replacement'
 required=set(scope['touchingNativeUids'])
 for url,r in allowed.items():
  path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==r['sha256'];refs.append(path);old=read(path);assert set(r['retainedUids'])==set(old['meta']['targetUids']);required.update(r['retainedUids'])
 forms={r['uid']:r for r in take(base/a.scope/'form-obligations.json.gz')};manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(manifestpath);msha=digest(manifestpath.read_bytes());native={r['uid']for r in inventory['rows']};assert required<=native
 needed=required-set(forms);tilehash={}
 for entry in manifest['tiles']:
  if not needed:break
  path=ROOT/'3d-viewer'/entry['url'];key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==inventory['currentFormTileHashes'][key]
  for form in read(path)['buildings']:
   if form['uid']in needed:forms[form['uid']]=form;needed.remove(form['uid']);tilehash[key]=digest(path.read_bytes());refs.append(path)
 assert not needed,needed
 tiles={x['id']:x for x in manifest['tiles']}
 for form in forms.values():
  path=ROOT/'3d-viewer'/tiles[form['tile']]['url'];key=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert sha==inventory['currentFormTileHashes'][key];tilehash[key]=sha;refs.append(path)
 path=ROOT/candidate['path'];assert digest(path.read_bytes())==candidate['sha256'];refs.append(path)
 patch=dict(**candidate,uids=scope['uids'],bounds=scope['regionalParentExtent'])
 keys=[('building:'if u.startswith('landsd/')else'source-form:')+u for u in sorted(forms)]+['terrain:city/data/terrain.json']+['terrain:'+u for u in allowed]
 lease=read(Path(a.lease_file));assert set(keys)<=set(lease['resources']) and reservations.owns(lease)
 try:
  bindingpath=base/a.bindings/'bindings.json';binding=take(bindingpath);assert binding['currentManifest']['sha256']==msha;save(doc/'installed-dependency-bindings.json',binding)
  save(doc/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=u in native or bool(b.get('modelGeometry')))for u,b in forms.items()],inputHashes={**tilehash,str(manifestpath.relative_to(ROOT)):msha},candidateIds=scope['uids'],patches=[patch],requiredNativeUids=sorted(required)))
  for name in ['check-neighbours-multi-retained.mjs','check-native-neighbours-current-installed-v4-20261022.mjs']:
   assert reservations.owns(lease)
   if name=='check-neighbours-multi-retained.mjs' and a.resume_from:
    prior=base/a.resume_from;oldinput=prior/'neighbour-inputs.json.gz';oldcheck=prior/'neighbour-checks.json';audit=read(prior/'termination-audit.json');assert audit['exitCode']==143 and not audit['exactWorkerPidsAlive']
    assert read(oldinput)==read(doc/'neighbour-inputs.json.gz');completed=read(oldcheck);assert len(completed['rows'])==len(forms) and {r['uid']for r in completed['rows']}==set(forms)
    for p,h in {**completed['inputHashes'],**completed['sourceInputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    (doc/'neighbour-checks.json').write_bytes(oldcheck.read_bytes());refs.extend([oldinput,oldcheck,prior/'termination-audit.json']);save(doc/'base-check-reuse.json',dict(prior=str(prior.relative_to(ROOT)),rows=len(forms),allInputsRehashed=True,exactInputsEqual=True,wholePriorJobComplete=False));continue
   tool=HERE/name;refs.append(tool)
   with(doc/(name+'.log')).open('w')as log:subprocess.run(['node',str(tool),str(doc.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  ordinary=read(doc/'neighbour-checks.json');report=read(doc/'native-neighbour-checks.json');assert required<=set(report['blocked'])and required<={r['uid']for r in report['rows']}
  for r in [ordinary,report]:
   for p,h in r['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  result=dict(uids=scope['uids'],forms=len(forms),requiredNativeUids=sorted(required),basicFlags=[dict(uid=r['uid'],reasons=r['reasons'])for r in ordinary['rows']if r['reasons']and not r['existingNative']],nativeRows=report['rows'],nativeResolved=report['resolved'],newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0)
  save(doc/'summary.json',result);assert digest(manifestpath.read_bytes())==msha and reservations.owns(lease)
  module('retained_native_neighbour_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-retained-native-whole-region-regression',list(set(refs)),result)
  print(dict(forms=len(forms),basicFlags=result['basicFlags'],requiredNative=len(required),nativeResolved=report['resolved']),flush=True)
 finally:assert reservations.owns(lease)
if __name__=='__main__':main()
