"""Fresh read-only complete original Elements Suntower/Startower renderer-attribute capture.

Original current source probe is a frozen baseline, never acceptance. Source,
actual literal correspondence, complete current catalogues/modules are pinned.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROBE=BASE/'government-xl-terrain-recovery-elements-sun-star-two-original-current-probe-v1-20261011';UIDS=['landsd/204145:0','landsd/204143:0'];CAPTURE=HERE/'xl-terrain-recovery-20261011-elements-sun-star-two-original-actual-render-attributes-v1.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);receipt=read(PROBE/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);assert start['sha256']==ref(PROBE/'historical-current-manifest.json')['sha256']=='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43';DOC.mkdir(parents=True,exist_ok=False);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());rows=read(PROBE/'selection.json.gz')['rows'];assert[r['uid']for r in rows]==UIDS;runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime={r['uid']:r for r in read(runtimepath)['rows']};bound={r['path']:r for r in receipt['evidenceRefs']};assert bound[str((PROBE/'selection.json.gz').relative_to(ROOT))]==ref(PROBE/'selection.json.gz')and bound[str(runtimepath.relative_to(ROOT))]==ref(runtimepath);refs=[ref(p)for p in [Path(__file__),CAPTURE,PROBE/'result.json',PROBE/'selection.json.gz',runtimepath,manifest,DOC/'historical-current-manifest.json',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'literal_production_module_dependency_closure_20261010.mjs']];cats=[ref(ROOT/'3d-viewer'/p)for p in current['officialModelCatalogues']];forms={}
 for tile in current['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid']in UIDS:assert b['uid']not in forms;forms[b['uid']]=(b,path)
 assert set(forms)==set(UIDS)
 matches=[]
 for p in current['officialModelCatalogues']:
  cat=read(ROOT/'3d-viewer'/p)
  for entry in cat['models']:
   if entry['uid']in UIDS:matches.append((entry['uid'],entry,cat))
 assert not matches,'Both Elements originals must remain uninstalled, with no duplicate current native';inputs=[]
 for row in rows:
  uid=row['uid'];assert row['source']['building']==forms[uid][0];asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==row['sourceSHA256']==runtime[uid]['sourceSHA256'];refs.extend([ref(asset),ref(forms[uid][1])]);inputs.append(dict(uid=uid,entry=row['candidate']['entry'],building=forms[uid][0],path=str(asset.relative_to(ROOT))))
 save(DOC/'literal-source-inputs.json.gz',dict(rows=inputs,currentManifest=start,currentCatalogueRefs=cats,evidenceRefs=refs));subprocess.run(['node',str(CAPTURE),str((DOC/'literal-source-inputs.json.gz').relative_to(ROOT)),str((DOC/'actual-render-attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);actual=read(DOC/'actual-render-attributes.json.gz');assert[r['uid']for r in actual['rows']]==UIDS
 for r in actual['rows']:
  rt=runtime[r['uid']];assert r['sourceSHA256']==rt['sourceSHA256'];assert np.array_equal(np.asarray(r['completeLiteralWorldPosition']),np.asarray(rt['position']));assert r['completeOriginalIndex']==rt['index'];assert len(r['completeOriginalIndex'])//3==({'landsd/204145:0':12129,'landsd/204143:0':11680}[r['uid']])
 assert ref(manifest)==start and reservations.owns(lease);assert all(ref(ROOT/r['path'])==r for r in refs+cats);assert all(digest((ROOT/path).read_bytes())==sha for path,sha in actual['inputHashes'].items());refs.extend(ref(ROOT/path)for path in actual['inputHashes']);refs.extend(cats+[ref(DOC/'literal-source-inputs.json.gz'),ref(DOC/'actual-render-attributes.json.gz')]);s=importlib.util.spec_from_file_location('freeze_elements-sun-star_attributes',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'fresh-complete-elements-sun-star-original-literal-two-explicit-float32-attribute-capture-v1',[ROOT/r['path']for r in {r['path']:r for r in refs}.values()],dict(uids=UIDS,currentManifest=start,allCompletePOSITIONAttributesIncludingUnused=True,completeOriginalFaces=23809,allCurrentCatalogueHashesPinned=True,completeRecursiveProductionModuleClosure=True,explicitArithmeticOnlyNotUniversalGPUCameraGuarantee=True,currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('elements-sun-star-two-actual-render-capture-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
