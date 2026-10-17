"""Fresh exact own/retained production attr/matrix capture, no acceptance."""
import importlib.util,subprocess,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from whole_source_disjoint_literal_parent_facets_20261010 import finite_projection
BATCH='government-xl-vancor-own-retained-actual-render-capture-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v1-20261011';BASIC=DOC.parent/'government-xl-vancor-basic-253697-whole-projection-diagnostic-v1-20261011';JS=HERE/'xl-vancor-own-retained-actual-render-geometry-v1-20261011.mjs'
MANIFEST='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 receipt=read(INPUT/'result.json');basicreceipt=read(BASIC/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [receipt,basicreceipt]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',('landsd/147956:0',)).fetchone()is None
 for name in ['check-selection.json.gz','proposal-input.json','complete-proposed-region-current-forms.json.gz']:assert ref(INPUT/name)in receipt['evidenceRefs']
 assert ref(BASIC/'complete-current-basic-geometry.json.gz')in basicreceipt['evidenceRefs'];base=read(BASIC/'complete-current-basic-geometry.json.gz');pos=np.asarray(base['actor']['completePosition'],dtype='<f8').reshape(-1,3);idx=np.asarray(base['actor']['completeIndex'],int).reshape(-1,3);basicprojection=finite_projection(pos[idx])
 claim=reservations.claim('vancor-original-actual-render-'+str(uuid.uuid4()),['building:'+u for u in ['landsd/147956:0','landsd/186864:0','landsd/253697:0']],batch=BATCH,ttl=1800);assert claim['ok'],claim
 try:
  DOC.mkdir(parents=True);process=subprocess.run(['node',str(JS)],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-log.json',dict(exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode==0,process.stderr
  capture=read(DOC/'complete-actual-render-geometry.json.gz');assert capture['startAndEndInputsVerified'];assert [r['uid']for r in capture['rows']]==['landsd/147956:0','landsd/186864:0'];assert [r['completeFaces']for r in capture['rows']]==[669,11744]
  proposal=read(INPUT/'proposal-input.json');selected=read(INPUT/'check-selection.json.gz')['rows'][0];sourcepaths={selected['uid']:ROOT/selected['candidate']['path'],proposal['retainedNativeUID']:ROOT/proposal['retainedAsset']['path']};rows=[]
  for row in capture['rows']:
   raw=sourcepaths[row['uid']].read_bytes();assert digest(raw)==row['sourceSHA256'];source=decode_original_world_triangles(raw);index=np.asarray(row['completeOriginalIndex'],int).reshape(-1,3);assert len(source)==len(index)==row['completeFaces']
   streams=[('providerOriginal',source)]
   for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:streams.append((mode,np.asarray(row[key],dtype='<f8').reshape(-1,3)[index]))
   metrics=[]
   for mode,world in streams:
    projection=finite_projection(world);metrics.append(dict(arithmetic=mode,completeFaces=len(world),completeTriangleSHA256=digest(world.astype('<f8').tobytes()),completeWholeIndexedBounds=[world.min((0,1)).tolist(),world.max((0,1)).tolist()],completeBasicProjectionIntersectionM2=projection.intersection(basicprojection).area,strictCompleteBasicProjectionDisjoint=not projection.intersects(basicprojection),minimumCompleteBasicProjectionDistanceM=projection.distance(basicprojection)))
   rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],source=ref(sourcepaths[row['uid']]),streams=metrics))
  out=dict(rows=rows,currentManifest=start,currentBasicGeometry=ref(BASIC/'complete-current-basic-geometry.json.gz'),completeActualMeshAttributesAndMatrices=ref(DOC/'complete-actual-render-geometry.json.gz'),sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Full production original attributes/matrices and complete indexed/unused vertices separately captured. Provider-original/literal/two explicit Float32 arithmetic streams remain distinct; no universal GPU camera/FMA, support, terrain/native or installation claim.')
  save(DOC/'diagnostic.json',out);assert ref(manifest)==start and reservations.owns(claim['reservation'])
  refs=[Path(__file__),JS,INPUT/'result.json',INPUT/'check-selection.json.gz',INPUT/'proposal-input.json',INPUT/'complete-proposed-region-current-forms.json.gz',BASIC/'result.json',BASIC/'complete-current-basic-geometry.json.gz',*[ROOT/p for p in capture['inputHashes']],*sourcepaths.values(),HERE/'exact_packed_world_geometry_20261009.py',HERE/'whole_source_disjoint_literal_parent_facets_20261010.py',HERE/'test_actual_float32_model_matrix_bounds_20261011.mjs',HERE/'test_literal_production_module_dependency_closure_20261010.mjs',HERE/'test_current_geometry_capture_preflight_20261011.mjs']
  spec=importlib.util.spec_from_file_location('vancor_actual_render_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-own-retained-actual-render-attribute-matrix-and-four-stream-basic-projection-diagnostic-v1',refs,dict(uids=[r['uid']for r in rows],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,newlyInstalled=0))
  print(json.dumps(rows))
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
