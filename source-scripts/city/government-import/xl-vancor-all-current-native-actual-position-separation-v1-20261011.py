"""Complete 6642 current actual-native whole POSITION separation diagnostic.
Exact6637+2 baseline bindings plus three actual current loader captures; no
geographic metadata proxy. Any overlapping bounds require full actor physics.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from complete_actual_native_position_bounds_separation_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import'
OLD=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011'
PREV=BASE/'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011'
DELTA=BASE/'government-xl-complete-native-actual-position-vancor-post-mount-delta-v1-20261011'
ACTUAL=BASE/'government-xl-vancor-own-retained-actual-render-capture-v2-20261011'
PHYS=BASE/'government-xl-vancor-basic-parent-core-apron-current-physical-v3-20261011'
BATCH='government-xl-vancor-all-current-native-actual-position-separation-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);refs=[Path(__file__),manifest];receipts={}
 for folder in [OLD,PREV,DELTA,ACTUAL,PHYS]:
  r=read(folder/'result.json');receipts[folder.name]=r
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
 a=read(OLD/'inventory.json.gz');b=read(PREV/'inventory.json.gz');c=read(DELTA/'inventory.json.gz');binding=read(DELTA/'complete-unchanged-baseline-bindings.json.gz');composition=read(DELTA/'composition.json.gz');inp=read(DELTA/'input.json.gz')
 assert composition['currentManifest']==binding['currentManifest']==inp['currentManifest']==start
 assert composition['completeCurrentNativeActors']==6642 and composition['completeOldActorsExactlyRebound']==binding['completeOldActorsRebound']==6639
 assert composition['baselineInventory']==ref(OLD/'inventory.json.gz')and composition['secondBaselineInventory']==ref(PREV/'inventory.json.gz')and composition['actualCurrentDelta']==ref(DELTA/'inventory.json.gz')and composition['baselineCurrentExactBinding']==ref(DELTA/'complete-unchanged-baseline-bindings.json.gz')
 assert not a['errors']and not b['errors']and not c['errors']and a['successfullyCapturedActors']==6637 and b['successfullyCapturedActors']==2 and c['successfullyCapturedActors']==3
 actors=a['rows']+b['rows']+c['rows'];assert len(actors)==len({r['uid']for r in actors})==6642;old={r['uid']:r for r in a['rows']+b['rows']};assert {r['uid']for r in binding['rows']}==set(old)
 for r in binding['rows']:assert canonical(old[r['uid']])==r['unchangedActualCompleteBoundsRowSHA256']and ref(ROOT/r['source']['path'])==r['source'];refs.append(ROOT/r['source']['path'])
 assert [r['uid']for r in c['rows']]==['landsd/239465:0','landsd/75782:0','landsd/261717:0']
 geometry=read(ACTUAL/'complete-actual-render-geometry.json.gz');assert geometry['startAndEndInputsVerified'];own=geometry['rows'][0];selection=read(PHYS/'selection.json.gz')['rows'][0];assert own['uid']==selection['uid']=='landsd/147956:0'and own['sourceSHA256']==selection['sourceSHA256'];assert read(PHYS/'diagnostic.json')['currentManifest']==start
 asset=ROOT/selection['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==own['sourceSHA256'];packed=packed_world_bounds(raw);assert packed['allOriginalPositionVerticesAccounted']and packed['completeOriginalTriangles']==669
 bounds={'providerOriginal':packed['originalWholeSourceBounds']}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:
  points=np.asarray(own[key],dtype='<f8').reshape(-1,3);assert len(points)==packed['completeOriginalPositionVertices']and np.isfinite(points).all();bounds[mode]=[points.min(0).tolist(),points.max(0).tolist()]
 for path,sha in {**geometry['inputHashes'],**c['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 for r in inp['currentCatalogueRefs']:assert ref(ROOT/r['path'])=={k:r[k]for k in ['path','sha256']};refs.append(ROOT/r['path'])
 certificate=verify(bounds,actors);assert certificate['completeForeignNativeActors']==6642
 save(DOC/'diagnostic.json.gz',dict(uid=own['uid'],sourceSHA256=own['sourceSHA256'],currentManifest=start,completeOwnedWorldBounds=bounds,completeOriginalPOSITIONProof=packed,completeNativeActualBoundsCertificate=certificate,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
 for folder,names in [(OLD,['inventory.json.gz']),(PREV,['inventory.json.gz']),(DELTA,['input.json.gz','inventory.json.gz','composition.json.gz','complete-unchanged-baseline-bindings.json.gz']),(ACTUAL,['complete-actual-render-geometry.json.gz']),(PHYS,['selection.json.gz','diagnostic.json'])]:
  for name in names:p=folder/name;assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(p)
 refs += [asset,HERE/'complete_actual_native_position_bounds_separation_20261011.py',HERE/'test_complete_actual_native_position_bounds_separation_20261011.py',HERE/'exact_packed_world_bounds_v3_20261010.py']
 assert ref(manifest)==start
 for path,sha in {**geometry['inputHashes'],**c['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==sha
 s=importlib.util.spec_from_file_location('vancor_current_native_separation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete6642-current-native-whole-unused-actual-position-three-arithmetic-bounds-separation-diagnostic',refs,dict(uids=[own['uid']],completeNativeActors=6642,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 print(json.dumps(dict(completeNativeActors=6642,strictAllNativeSeparation=True)),flush=True)
if __name__=='__main__':main()
