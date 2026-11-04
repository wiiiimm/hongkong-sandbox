"""UNEXECUTED bounded attribution, never matching by tolerance/permutation.

Compare raw old Float32 triangle order, the EXACT current renderer b/c swap,
and complete captured literal triangles/multiplicity. No candidate generation,
unchanged projection rerun, support, native reapproval or acceptance credit.
ROOT reviews helper/nine tests/producer before either CLI execution.
"""
from pathlib import Path
from collections import Counter
import importlib.util,json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from sparkle_retained_literal_terrain_construction_20261011 import dyadic_facet_boxes,merge_literal_ground_snapshots,whole_ground_faces_touching_boxes
from sparkle_current_native_renderer_winding_20261011 import drawn_native_faces
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-sparkle-retained-ground-winding-attribution-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
FAILED=BASE/'xl-terrain-recovery-20261011-sparkle-authentic-retained-market-terrain-candidate-v1'
RETAINED=BASE/'xl-terrain-recovery-20261011-sparkle-retained-market-two-current-render-ground-capture-v2'
UIDS=['landsd/242198:0','landsd/228000:0','landsd/113733:0','landsd/138091:0']
MANIFEST='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
HELPER=HERE/'sparkle_current_native_renderer_winding_20261011.py';TEST=HERE/'test_sparkle_current_native_renderer_winding_20261011.py'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(r):
 p=ROOT/r['path'];assert p.is_file()and ref(p)==r;return p
def counter(a):return Counter(f.astype('<f4').tobytes()for f in np.asarray(a).reshape(-1,3,3))
def difference(c):return [dict(orderedFloat32TriangleBytes=k.hex(),multiplicity=v)for k,v in sorted(c.items())]
def validate():
 assert not DOC.exists()and not(LOCAL/'validation.json').exists();before=[ref(HELPER),ref(TEST)];LOCAL.mkdir(parents=True,exist_ok=True);log=LOCAL/'actual-nine-adverse-tests.log'
 with log.open('wb')as f:r=subprocess.run([sys.executable,str(TEST)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and 'Ran 9 tests'in log.read_text()and '\nOK\n'in log.read_text()and before==[ref(HELPER),ref(TEST)]
 save(LOCAL/'validation.json',dict(executedCode=before,actualLog=ref(log),passed=9,exitCode=0))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();v=read(LOCAL/'validation.json');assert v['executedCode']==[ref(HELPER),ref(TEST)]and v['passed']==9 and v['exitCode']==0;verify(v['actualLog'])
 refs=[ref(Path(__file__)),ref(HELPER),ref(TEST),ref(LOCAL/'validation.json'),v['actualLog'],ref(HERE/'sparkle_retained_literal_terrain_construction_20261011.py'),ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')]
 for folder,job in [(FAILED,'35b9647355f0b31c98ec1f7c3a3e78c29a787a0af8d9e706228b8bee24536ff5'),(RETAINED,'4832a8e05527b49eca61ff04478d7ce4d9a3a8dcc315fdf1756171293ab144b9')]:
  r=read(folder/'result.json');assert r['jobId']==job
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',r)
  for p in r['evidenceRefs']:verify(p)
  refs.extend([ref(folder/'result.json'),*r['evidenceRefs']])
 assert read(FAILED/'construction-guard-failure.json')['error']=='Captured whole protected ground differs from complete old native mesh'
 assert not read(FAILED/'construction-summary.json')['candidateFilesProduced']
 inp=read(RETAINED/'native-render-inputs.json.gz');actual=read(RETAINED/'native-render-ground.json.gz')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST and inp['currentManifest']==start
 for path,sha in actual['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha;refs.append(ref(ROOT/path))
 old=read(verify(inp['retainedTerrain']));assert old['meta']['targetUids']==UIDS[2:]and len(old['nativeMesh']['index'])//3==3845
 # Named Float32 POSITION + index transform is the exact makeNativeTerrain
 # formula from the byte-pinned current world.js, not arbitrary correspondence.
 assert {'3d-viewer/city/world.js','3d-viewer/city/native-terrain.js'}<=set(actual['inputHashes'])
 worlds=[]
 for row,geometry in zip(inp['rows'],actual['rows']):
  assert row['uid']==geometry['uid']and geometry['uid']in UIDS[2:]
  asset=verify(row['sourceAsset']);assert ref(asset)['sha256']==geometry['sourceSHA256']
  worlds.append(decode_original_world_triangles(asset.read_bytes()))
  ids=np.asarray(geometry['completeOriginalIndex'],int)
  for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   positions=np.asarray(geometry[key],float).reshape(-1,3);worlds.append(positions[ids].reshape(-1,3,3))
 outer=dyadic_facet_boxes(worlds,collar_cells=1)
 vertices=np.asarray(old['nativeMesh']['position'],np.float32).astype(float).reshape(-1,3);ids=np.asarray(old['nativeMesh']['index'],int).reshape(-1,3);raw=vertices[ids]
 drawn,transform=drawn_native_faces(old['nativeMesh']);captured=merge_literal_ground_snapshots([r['drawnGroundGeometry']for r in actual['rows']])
 old_ids,raw_selected=whole_ground_faces_touching_boxes(raw,outer);draw_ids,draw_selected=whole_ground_faces_touching_boxes(drawn,outer);captured_ids,captured_selected=whole_ground_faces_touching_boxes(captured,outer);assert np.array_equal(old_ids,draw_ids)
 rc,dc,cc=counter(raw_selected),counter(draw_selected),counter(captured_selected)
 counts=Counter(int(i)for i in ids.reshape(-1));appearance=dict(completeOriginalIndexIsSequential=old['nativeMesh']['index']==list(range(len(old['nativeMesh']['index']))),sourceSharedVertexIDs=sum(n>1 for n in counts.values()),maximumSourceVertexReferences=max(counts.values()),oldGridVegetationValues=sorted(set(old['vegetation'])),normalAlgorithm='world.js computeVertexNormals after exact winding swap; sequential vertices are face-local, not shared smoothing',colorAlgorithm='world.js clamp(Math.round((x+ORIGIN-bE)/aE),0,w-1), likewise z; vegetation chooses fixed urban/green color',exactGridOffsetConventionRequired=True,actualCandidateNormalsAndColorsNotYetCaptured=True,appearanceApproval=False)
 allrc,alldc,allcc=counter(raw),counter(drawn),counter(captured)
 output=dict(uids=UIDS,currentManifest=start,exactCurrentRendererTransform=transform,completeOldRawFloat32Faces=len(raw),completeMergedActualCapturedFaces=len(captured),protectedOldFaceIDs=old_ids.tolist(),protectedCapturedFaceIDs=captured_ids.tolist(),rawOrderedProtectedCount=sum(rc.values()),rendererOrderedProtectedCount=sum(dc.values()),actualCapturedProtectedCount=sum(cc.values()),rawOrderMatchesCaptured=rc==cc,exactNamedRendererOrderMatchesCaptured=dc==cc,rawMissingFromCaptured=difference(rc-cc),rawExtraCaptured=difference(cc-rc),rendererMissingFromCaptured=difference(dc-cc),rendererExtraCaptured=difference(cc-dc),allCapturedFacesAbsentFromOldRaw=difference(allcc-allrc),allCapturedFacesAbsentFromOldRenderer=difference(allcc-alldc),sourceFloat32XYZUnchanged=True,originalSamplerIndicesNotChanged=True,arbitraryPermutationsOrToleranceUsed=False,noProjectionContactRerun=True,candidateCreated=False,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0)
 output['retainedAppearanceObligations']=appearance
 for p in refs:verify(p)
 assert ref(manifest)==start and reservations.owns(lease);DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());save(DOC/'diagnostic.json.gz',output)
 s=importlib.util.spec_from_file_location('sparkle_ground_attribution_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 result=m.freeze(BATCH,'sparkle-retained-ground-exact-renderer-winding-and-multiplicity-attribution-v1',[verify(r)for r in {r['path']:r for r in refs}.values()],dict(uids=UIDS,rawOrderMatchesCaptured=rc==cc,exactNamedRendererOrderMatchesCaptured=dc==cc,candidateCreated=False,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=result['jobId'],raw=rc==cc,rendered=dc==cc)),flush=True)
def main():
 if '--validate-helper'in sys.argv:return validate()
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not(LOCAL/'reservation.json').exists();claim=reservations.claim('sparkle-ground-winding-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['terrain-patch:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
