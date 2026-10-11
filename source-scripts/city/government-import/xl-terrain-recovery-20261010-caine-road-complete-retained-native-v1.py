"""Explicit all-retained original native before/after terrain checks; no publication."""
import importlib.util,json,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
BATCH='xl-terrain-recovery-20261010-caine-road-complete-retained-native-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-unnamed-268032-nested-original-pair-current-physical-v5-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);physical=read(PHYSICAL/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(physical['jobId'],)).fetchone()==('complete',physical)
 for r in physical['evidenceRefs']:assert ref(ROOT/r['path'])==r
 inputs=read(PHYSICAL/'neighbour-inputs.json.gz');assert inputs['candidateIds']==['landsd/101781:0','landsd/268032:0'];parent=ROOT/'3d-viewer'/inputs['patches'][0]['replaces']['url'];retained=sorted({u for child in read(parent)['patches'] for u in child['meta']['targetUids']}|{r['building']['uid'] for r in inputs['rows'] if r['existingNative']})
 assert len(read(parent)['patches'])==9
 catalogues=[ROOT/'3d-viewer'/u for u in read(manifest)['officialModelCatalogues']];native={m['uid']:m for p in catalogues for m in read(p)['models']};assert set(retained)<=set(native)
 spec=importlib.util.spec_from_file_location('complete_native_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
 forms={r['building']['uid']:r['building'] for r in inputs['rows']};hashes=dict(inputs['inputHashes'])
 for uid in retained:
  lo,hi=native[uid]['worldBounds']
  for f,_,tile in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]):forms[f['uid']]=f;hashes[str((ROOT/'3d-viewer'/tile).relative_to(ROOT))]=digest((ROOT/'3d-viewer'/tile).read_bytes())
 assert set(retained)<=set(forms)
 inputs['rows']=[dict(building=f,existingNative=u in native,patchIndexes=[0]) for u,f in sorted(forms.items())];inputs['inputHashes']=hashes;inputs['patches'][0]['replaces']['retainedUids']=retained
 bindings=[]
 for uid in retained:
  for dep in native[uid].get('supportDependencies',[]):
   if dep['state']=='installed':continue
   assert uid=='landsd/263590:0' and dep==dict(uid='landsd/232907:0',state='candidate') and dep['uid'] in native
   def pin(u):
    e=native[u];cat=next(p for p in catalogues if any(m['uid']==u for m in read(p)['models']));asset=cat.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];return dict(sourceSHA256=e['sha256'],buildingCSUID=e['buildingCSUID'],modelId=e['modelId'],catalogue=ref(cat),originalSource=ref(asset))
   bindings.append(dict(ownerUID=uid,supportUID=dep['uid'],owner=pin(uid),support=pin(dep['uid']),originalRecordedDependency=dep,currentSupportIsUniquelyInstalled=sum(m['uid']==dep['uid'] for p in catalogues for m in read(p)['models'])==1))
 save(DOC/'current-native-dependency-bindings.json',dict(rows=bindings,currentManifest=start))
 save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'neighbour-checks.json',read(PHYSICAL/'neighbour-checks.json'))
 keys=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(forms)]+['terrain-surface:'+inputs['patches'][0]['replaces']['url']]
 claim=reservations.claim(BATCH,keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=json.loads(json.dumps(claim['reservation'],default=str));save(DOC/'reservation.json',lease)
 try:
  assert subprocess.run(['node',str(HERE/'xl-terrain-recovery-20261010-no1-garden-complete-native-checker-v2.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT).returncode==0
  result=read(DOC/'native-neighbour-checks.json');assert set(result['blocked'])==set(retained);assert reservations.owns(lease) and ref(manifest)==start
  for path,sha in result['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
  refs=[ref(p) for p in [Path(__file__),PHYSICAL/'result.json',PHYSICAL/'neighbour-inputs.json.gz',PHYSICAL/'neighbour-checks.json',HERE/'xl-terrain-recovery-20261010-no1-garden-complete-native-checker-v2.mjs',HERE/'native-neighbour-policy.mjs',parent,manifest,HERE/'current_installed_recorded_native_dependency_20261010.mjs',HERE/'test_current_installed_recorded_native_dependency_20261010.mjs']]+[dict(path=p,sha256=s) for p,s in result['inputHashes'].items()]
  save(DOC/'retained-scope.json',dict(retainedNativeUids=retained,parent=ref(parent),allNineChildrenPinned=True,originalScopeForms=len(forms),physicalResult=ref(PHYSICAL/'result.json'),currentManifest=start))
  spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freeze=importlib.util.module_from_spec(spec);spec.loader.exec_module(freeze)
  freeze.freeze(BATCH,'explicit-complete-current-retained-native-before-after-v1',[ROOT/r['path'] for r in refs],dict(uids=['landsd/101781:0','landsd/268032:0'],retainedNativeUids=retained,allCurrentRetainedNativeChecksPassed=all(r['passed'] for r in result['rows']),rawFailedNativeUids=[r['uid'] for r in result['rows'] if not r['passed']],sourceGeometryChanges=0,terrainProposalGeometryChanged=True,fullAcceptance=False,publication=False))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
