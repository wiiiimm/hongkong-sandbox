"""Read-only whole retained native renderer attributes and actual drawn terrain.

Both current native actors retain every original flag/source. This supplies
literal/two explicit F32 arithmetic and complete ground inputs, never approval.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011';GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1';UIDS=['landsd/273061:0','landsd/204144:0'];COUNTS=[203738,11166];MANIFEST='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43';CAPTURE=HERE/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);assert not DOC.exists();refs=[ref(Path(__file__)),ref(CAPTURE),*[ref(HERE/n)for n in ['exact_packed_world_bounds_v3_20261010.py','exact_packed_world_geometry_20261009.py','actual_float32_model_matrix_bounds_20261011.mjs','literal_production_module_dependency_closure_20261010.mjs']]]
 for folder in [PHYSICAL,GRAPH]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 prior=read(PHYSICAL/'result.json');bound={r['path']:r for r in prior['evidenceRefs']}
 for path in [PHYSICAL/'current-source-terrain-preflight.json',PHYSICAL/'native-source-form-preflight.json',PHYSICAL/'historical-current-manifest.json']:
  assert bound[str(path.relative_to(ROOT))]==ref(path);refs.append(ref(path))
 preflight=read(PHYSICAL/'native-source-form-preflight.json');assert preflight['requiredNativeUids']==sorted(UIDS);manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST==preflight['currentManifest']['sha256'];refs.extend([start,*preflight['catalogueRefs'],*preflight['currentTileRefs']]);assert all(ref(ROOT/r['path'])==r for r in refs)
 retained=read(PHYSICAL/'current-source-terrain-preflight.json')['completeRetainedNativeEntries'];assert[r['uid']for r in retained]==UIDS;rows=[]
 for r,count in zip(retained,COUNTS):
  asset=ROOT/r['source']['path'];assert ref(asset)==r['source']and r['source']['sha256']==r['entry']['sha256'];assert r['entry']['triangles']==count and r['entry']['publicationApproved']is True;proof=packed_world_bounds(asset.read_bytes());assert proof['sourceSHA256']==r['entry']['sha256'];refs.append(ref(asset));rows.append(dict(uid=r['uid'],rawEntry=r['entry'],sourceAsset=r['source'],catalogue=r['catalogue'],sourceForm=preflight['sourceForms'][r['uid']],completeOriginalPOSITIONProof=proof))
 DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append(ref(DOC/'historical-current-manifest.json'));save(DOC/'native-render-inputs.json.gz',dict(rows=rows,currentManifest=start,currentCatalogueRefs=preflight['catalogueRefs'],currentTileRefs=preflight['currentTileRefs'],evidenceRefs=refs));subprocess.run(['node',str(CAPTURE),str((DOC/'native-render-inputs.json.gz').relative_to(ROOT)),str((DOC/'native-render-ground.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 output=read(DOC/'native-render-ground.json.gz');assert[r['uid']for r in output['rows']]==UIDS
 for row,count in zip(output['rows'],COUNTS):assert len(row['completeOriginalIndex'])//3==count and row['sourceSHA256']==next(r['entry']['sha256']for r in retained if r['uid']==row['uid'])
 assert reservations.owns(lease)and ref(manifest)==start;assert all(ref(ROOT/r['path'])==r for r in refs);assert all(digest((ROOT/p).read_bytes())==sha for p,sha in output['inputHashes'].items());refs.extend(ref(ROOT/p)for p in output['inputHashes']);refs.extend(ref(DOC/p)for p in ['native-render-inputs.json.gz','native-render-ground.json.gz']);refs.extend(ref(HERE/n)for n in ['exact_packed_world_bounds_v3_20261010.py','actual_float32_model_matrix_bounds_20261011.mjs','literal_production_module_dependency_closure_20261010.mjs','xl-popcorn-source-investigations-checkpoints-20261009.py'])
 spec=importlib.util.spec_from_file_location('elements_native_render_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-elements-two-native-original-literal-explicit-float32-drawn-ground-read-only-v1',[ROOT/r['path']for r in {r['path']:r for r in refs}.values()],dict(uids=UIDS,completeNativeOriginalFaces=214904,completePOSITIONIncludingUnused=True,currentManifest=start,allCurrentCatalogueHashesPinned=True,nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,terrainChanges=0,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('elements-native-render-ground-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
