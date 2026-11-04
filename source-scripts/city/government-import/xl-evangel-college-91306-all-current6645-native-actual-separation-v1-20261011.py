"""Complete6645 current actual native unused-POSITION separation diagnostic.
The exact6642 old tuple rebind plus3 actual current actors is mandatory. Whole
source POSITION and literal/F32 modes use exact current source/form/loader
inputs, never geographic catalogue bounds. Overlaps remain full obligations.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from complete_actual_native_position_bounds_separation_20261011 import verify
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import source_proposal_pin_path
BASE=ROOT/'docs/astra-city/government-import'
OLD=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011'
PREV=BASE/'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011'
THIRD=BASE/'government-xl-complete-native-actual-position-vancor-post-mount-delta-v1-20261011'
DELTA=BASE/'government-xl-complete-native-actual-position-evangel-post-elements-delta-v1-20261011'
ACTUAL=BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011'
PHYS=BASE/'government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011'
BATCH='government-xl-evangel-college-91306-all-current6645-native-actual-separation-v1-20261011';DOC=BASE/BATCH
UID='landsd/91306:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);refs=[Path(__file__),manifest];receipts={}
 for folder in [OLD,PREV,THIRD,DELTA,ACTUAL,PHYS]:
  r=read(folder/'result.json');receipts[folder.name]=r
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
 a=read(OLD/'inventory.json.gz');b=read(PREV/'inventory.json.gz');c=read(THIRD/'inventory.json.gz');d=read(DELTA/'inventory.json.gz');binding=read(DELTA/'complete-unchanged-baseline-bindings.json.gz');composition=read(DELTA/'composition.json.gz');inp=read(DELTA/'input.json.gz')
 assert composition['currentManifest']==binding['currentManifest']==inp['currentManifest']==start
 assert composition['completeCurrentNativeActors']==6645 and composition['completeOldActorsExactlyRebound']==binding['completeOldActorsRebound']==6642
 for key,path in [('baselineInventory',OLD/'inventory.json.gz'),('secondBaselineInventory',PREV/'inventory.json.gz'),('thirdBaselineInventory',THIRD/'inventory.json.gz'),('actualCurrentDelta',DELTA/'inventory.json.gz'),('baselineCurrentExactBinding',DELTA/'complete-unchanged-baseline-bindings.json.gz')]:assert composition[key]==ref(path)
 assert all(not r['errors']for r in [a,b,c,d])and [r['successfullyCapturedActors']for r in [a,b,c,d]]==[6637,2,3,3]
 old={r['uid']:r for r in a['rows']+b['rows']+c['rows']};actors=list(old.values())+d['rows'];assert len(old)==6642 and len(actors)==len({r['uid']for r in actors})==6645
 assert {r['uid']for r in binding['rows']}==set(old)
 for r in binding['rows']:assert canonical(old[r['uid']])==r['unchangedActualCompleteBoundsRowSHA256']and ref(ROOT/r['source']['path'])==r['source'];refs.append(ROOT/r['source']['path'])
 assert [r['uid']for r in d['rows']]==['landsd/95691:0','landsd/204145:0','landsd/204143:0']
 geometry=read(ACTUAL/'complete-current-actual-source-and-ground.json.gz');assert geometry['startAndEndInputsVerified'];selection=read(PHYS/'selection.json.gz')['rows'][0];assert geometry['uid']==selection['uid']==UID and geometry['sourceSHA256']==selection['sourceSHA256']and geometry['entry']==selection['candidate']['entry']
 assert read(PHYS/'diagnostic.json.gz')['currentManifest']==start
 captured=[f for f in geometry['completeCurrentForms']if f['uid']==UID];assert len(captured)==1 and captured[0]==selection['source']['building']
 tilepath='3d-viewer/'+selection['source']['tile'];assert geometry['inputHashes'][tilepath]==digest((ROOT/tilepath).read_bytes());assert [f for f in read(ROOT/tilepath)['buildings']if f['uid']==UID]==captured
 for path,sha in geometry['completeRecursiveLoaderModuleClosure']['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 runtime_path=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtime_path);assert len(runtime['rows'])==1 and runtime['rows'][0]['uid']==UID
 assert np.array_equal(np.asarray(runtime['rows'][0]['position'],dtype='<f8'),np.asarray(geometry['completeLiteralWorldPosition'],dtype='<f8'))and runtime['rows'][0]['index']==geometry['completeOriginalIndex']
 asset=ROOT/selection['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==geometry['sourceSHA256'];packed=packed_world_bounds(raw);assert packed['allOriginalPositionVerticesAccounted']and packed['completeOriginalTriangles']==13960 and packed==geometry['completeOriginalPOSITIONProof']
 bounds={'providerOriginal':packed['originalWholeSourceBounds']}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:
  points=np.asarray(geometry[key],dtype='<f8').reshape(-1,3);assert len(points)==packed['completeOriginalPositionVertices']and np.isfinite(points).all();bounds[mode]=[points.min(0).tolist(),points.max(0).tolist()]
 for path,sha in geometry['inputHashes'].items():p=source_proposal_pin_path(dict(path=path,sha256=sha));assert digest(p.read_bytes())==sha;refs.append(p)
 for path,sha in {**d['inputHashes'],**runtime['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 for r in inp['currentCatalogueRefs']:assert ref(ROOT/r['path'])=={k:r[k]for k in ['path','sha256']};refs.append(ROOT/r['path'])
 certificate=verify(bounds,actors);assert certificate['completeForeignNativeActors']==6645
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=geometry['sourceSHA256'],currentManifest=start,completeOwnedWorldBounds=bounds,completeOriginalPOSITIONProof=packed,completeNativeActualBoundsCertificate=certificate,exactCurrentInputFormEntrySourceAndLoaderTuple=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
 for folder,names in [(OLD,['inventory.json.gz']),(PREV,['inventory.json.gz']),(THIRD,['inventory.json.gz']),(DELTA,['input.json.gz','inventory.json.gz','composition.json.gz','complete-unchanged-baseline-bindings.json.gz']),(ACTUAL,['complete-current-actual-source-and-ground.json.gz']),(PHYS,['selection.json.gz','diagnostic.json.gz'])]:
  for name in names:p=folder/name;assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(p)
 refs += [runtime_path,asset,HERE/'complete_actual_native_position_bounds_separation_20261011.py',HERE/'test_complete_actual_native_position_bounds_separation_20261011.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011.py']
 assert ref(manifest)==start
 for path,sha in {**d['inputHashes'],**runtime['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==sha
 for path,sha in geometry['inputHashes'].items():assert digest(source_proposal_pin_path(dict(path=path,sha256=sha)).read_bytes())==sha
 s=importlib.util.spec_from_file_location('evangel_current_native_separation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.freeze(BATCH,'complete6645-current-native-whole-unused-actual-position-four-arithmetic-bounds-separation-diagnostic',refs,dict(uids=[UID],completeNativeActors=6645,physicalAccepted=False,installationApproved=False,newlyInstalled=0));print(json.dumps(dict(jobId=r['jobId'],completeNativeActors=6645)),flush=True)
if __name__=='__main__':main()
