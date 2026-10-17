"""Current strict whole-POSITION/native separation certificate only.
Complete 6637 pinned actual baseline + current independently loaded Block6 and Block17.
No current identity/support/runtime approval follows from this certificate.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from complete_actual_native_position_bounds_separation_20261011 import verify
BATCH='government-xl-lippo-tower-all-current-native-actual-position-separation-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-lippo-tower-only-current-complete-inputs-v5-20261011'
DELTA=DOC.parent/'government-xl-complete-native-actual-position-post-block17-delta-v1-20261011'
OLD=DOC.parent/'government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical_sha(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not DOC.exists();inp=read(INPUT/'input.json.gz');geo=read(INPUT/'complete-current-geometry.json.gz');manifestpath=ROOT/inp['currentManifest']['path'];start=ref(manifestpath);assert start==inp['currentManifest']
 refs=[Path(__file__)];old=read(OLD/'inventory.json.gz');delta=read(DELTA/'inventory.json.gz');composition=read(DELTA/'composition.json.gz');bindings=read(DELTA/'complete-unchanged-baseline-bindings.json.gz');delta_input=read(DELTA/'input.json.gz')
 for folder in [INPUT,OLD,DELTA]:
  receipt=read(folder/'result.json')
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(folder/'result.json')
 assert composition['currentManifest']==bindings['currentManifest']==delta_input['currentManifest']==start
 assert composition['completeCurrentNativeActors']==6639 and bindings['completeOldActorsRebound']==6637 and composition['completeOldActorsExactlyRebound']==6637
 assert composition['baselineInventory']==ref(OLD/'inventory.json.gz') and composition['actualCurrentDelta']==ref(DELTA/'inventory.json.gz') and composition['baselineCurrentExactBinding']==ref(DELTA/'complete-unchanged-baseline-bindings.json.gz')
 assert old['successfullyCapturedActors']==6637 and not old['errors'] and delta['successfullyCapturedActors']==2 and not delta['errors']
 actors=old['rows']+delta['rows'];assert len(actors)==len({a['uid'] for a in actors})==6639
 old_by_uid={a['uid']:a for a in old['rows']};assert {b['uid'] for b in bindings['rows']}==set(old_by_uid)
 for binding in bindings['rows']:
  assert binding['unchangedActualCompleteBoundsRowSHA256']==canonical_sha(old_by_uid[binding['uid']])
  assert ref(ROOT/binding['source']['path'])==binding['source']
 assert [a['uid'] for a in delta['rows']]==['landsd/255438:0','landsd/256116:0']
 # Revalidate the complete current catalogue byte pins, not merely manifest SHA.
 for r in inp['currentCatalogueRefs']:assert ref(ROOT/r['path'])==r
 assert [(r['path'],r['sha256']) for r in delta_input['currentCatalogueRefs']]==[(r['path'],r['sha256']) for r in inp['currentCatalogueRefs']]
 for path,sha in geo['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 for path,sha in delta['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 for path,sha in old['completeRecursiveProductionModuleClosure']['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 row=inp['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];packed=packed_world_bounds(asset.read_bytes());assert packed['allOriginalPositionVerticesAccounted'] is True and packed['completeOriginalTriangles']==3597
 render=geo['row'];assert render['uid']==row['uid'] and render['sourceSHA256']==row['sourceSHA256']
 owned={'providerOriginal':packed['originalWholeSourceBounds']}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:
  positions=np.asarray(render[key],dtype='<f8').reshape(-1,3);assert len(positions)==packed['completeOriginalPositionVertices'] and np.isfinite(positions).all();owned[mode]=[positions.min(0).tolist(),positions.max(0).tolist()]
 certificate=verify(owned,actors);assert certificate['completeForeignNativeActors']==6639
 save(DOC/'diagnostic.json.gz',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],currentManifest=start,completeUnusedOwnedPOSITIONVertices=packed['completeOriginalPositionVertices'],completeOwnedWorldBounds=owned,completeOriginalPOSITIONProof=packed,completeNativeActualBoundsCertificate=certificate,currentBaselineAndDeltaExactBindings=ref(DELTA/'composition.json.gz'),physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
 test=HERE/'test_complete_actual_native_position_bounds_separation_20261011.py';proc=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p',test.name,'-v'],cwd=ROOT,capture_output=True,text=True);save(DOC/'tests.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,hermeticCounterexamples=True,separateCompleteActualCurrent6639ActorCertificate=True));assert proc.returncode==0,proc.stderr
 assert ref(manifestpath)==start
 for binding in bindings['rows']:assert ref(ROOT/binding['source']['path'])==binding['source']
 refs += [asset,INPUT/'input.json.gz',INPUT/'complete-current-geometry.json.gz',OLD/'inventory.json.gz',DELTA/'inventory.json.gz',DELTA/'composition.json.gz',DELTA/'complete-unchanged-baseline-bindings.json.gz',DELTA/'input.json.gz',DOC/'diagnostic.json.gz',DOC/'tests.json',HERE/'complete_actual_native_position_bounds_separation_20261011.py',test,HERE/'exact_packed_world_bounds_v3_20261010.py',*[ROOT/p for p in geo['inputHashes']],*[ROOT/p for p in delta['inputHashes']]]
 s=importlib.util.spec_from_file_location('lippo_all_actual_native_separation_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'lippo-current-complete6639-native-whole-actual-literal-and-declared-f32-position-strict-separation-only',refs,dict(uids=[row['uid']],currentManifest=start,completeNativeActors=6639,completeOwnedFaces=3597,wholeUnusedPositionsIncluded=True,noGeographicOrToleranceCredit=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=receipt['jobId'],completeNativeActors=6639,strictPlanarSeparation=True)),flush=True)
if __name__=='__main__':main()
