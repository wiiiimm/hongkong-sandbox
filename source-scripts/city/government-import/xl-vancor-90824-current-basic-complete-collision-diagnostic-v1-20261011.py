"""Exact complete finite contacts plus closed BASIC solid witnesses only.
All669 source faces and all20 actual BASIC faces remain, including zero-area
source records. No ownership, tolerance, root, clearance or installation credit.
"""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,primitive_census
from exact_closed_two_level_mesh_vertical_ray_20261010 import verify as ray
BASE=ROOT/'docs/astra-city/government-import';FOREIGN=BASE/'government-xl-vancor-complete-current-foreign-basic-context-v2-20261011';ACTUAL=BASE/'government-xl-vancor-own-retained-actual-render-capture-v2-20261011';PHYS=BASE/'government-xl-vancor-basic-parent-core-apron-current-physical-v3-20261011'
BATCH='government-xl-vancor-90824-current-basic-complete-collision-diagnostic-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);refs=[Path(__file__),manifest]
 for folder in [FOREIGN,ACTUAL,PHYS]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
 diagnostic=read(FOREIGN/'diagnostic.json.gz');assert diagnostic['currentManifest']==start and diagnostic['foreignActorsRequiringFullCollisionProof']==['landsd/90824:0']
 capture=read(FOREIGN/'complete-current-foreign-basic-geometry.json.gz');f=next(r for r in capture['rows']if r['uid']=='landsd/90824:0');assert f['currentForm']['buildingCSUID']=='3556718520T20050430'and f['completeFaces']==20
 p=np.asarray(f['completePosition'],dtype='<f8').reshape(-1,3);index=np.asarray(f['completeIndex'],int).reshape(-1,3);foreign=p[index];assert np.array_equal(p,np.asarray(f['leftAssociatedPerMultiplyAddFloat32WorldPosition']).reshape(-1,3))and np.array_equal(p,np.asarray(f['balancedPerMultiplyAddFloat32WorldPosition']).reshape(-1,3))
 own=read(ACTUAL/'complete-actual-render-geometry.json.gz');a=own['rows'][0];selection=read(PHYS/'selection.json.gz')['rows'][0];asset=ROOT/selection['candidate']['path'];assert digest(asset.read_bytes())==a['sourceSHA256']==selection['sourceSHA256'];ix=np.asarray(a['completeOriginalIndex'],int).reshape(-1,3);streams={'providerOriginal':decode_original_world_triangles(asset.read_bytes())}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(a[key],dtype='<f8').reshape(-1,3)[ix]
 rows=[];cache={}
 for mode,world in streams.items():
  assert world.shape==(669,3,3);sha=digest(world.tobytes())
  if sha not in cache:
   contacts=exact_finite_contacts(world,list(range(669)),foreign,list(range(20)));assert contacts['allPairsExamined'];vertices=sorted({tuple(F(float(v))for v in p)for face in world for p in face});vertextrials=[ray(foreign,p)for p in vertices];centroids=[tuple(sum(F(float(v))for v in face[:,k])/3 for k in range(3))for face in world];centroidtrials=[dict(sourceFace=i,proof=ray(foreign,p))for i,p in enumerate(centroids)]
   cache[sha]=dict(completeSourceWorldSHA256=sha,completeForeignWorldSHA256=digest(foreign.tobytes()),completeSourceFaces=669,completeForeignFaces=20,completeSourceFinitePrimitiveCensus=primitive_census(world),completeForeignFinitePrimitiveCensus=primitive_census(foreign),allCompleteExact3DSurfaceContacts=contacts,completeUniqueSourceVertexRayTrials=vertextrials,all669ExactSourceCentroidRayTrials=centroidtrials,strictSourceVertexInteriorWitnesses=[r for r in vertextrials if r['strictOddParityInterior']],strictSourceFaceCentroidInteriorWitnesses=[r for r in centroidtrials if r['proof']['strictOddParityInterior']],surfaceContactAbsenceNeverMeansSolidClearance=True,negativeWitnessSearchNotPositiveCollisionCertification=True)
  rows.append(dict(arithmetic=mode,**cache[sha]))
 save(DOC/'diagnostic.json.gz',dict(uid=selection['uid'],sourceSHA256=selection['sourceSHA256'],foreignUID=f['uid'],completeActualForeignForm=f['currentForm'],currentManifest=start,rows=rows,currentFormNamesParentsContextOnly=True,ownershipClaimed=False,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,installationApproved=False))
 refs += [asset,FOREIGN/'diagnostic.json.gz',FOREIGN/'complete-current-foreign-basic-geometry.json.gz',ACTUAL/'complete-actual-render-geometry.json.gz',PHYS/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_closed_two_level_mesh_vertical_ray_20261010.py',HERE/'test_exact_closed_two_level_mesh_vertical_ray_20261010.py']
 for captured in [capture,own]:
  for path,sha in captured['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 assert ref(manifest)==start
 s=importlib.util.spec_from_file_location('vancor_foreign_collision_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete669-by20-current-basic-finite3D-contacts-and-closed-solid-interior-witnesses-diagnostic-only',refs,dict(uids=[selection['uid'],f['uid']],strictCentroidInteriorCounts={r['arithmetic']:len(r['strictSourceFaceCentroidInteriorWitnesses'])for r in rows},currentAcceptance=False,newlyInstalled=0))
 print(json.dumps({r['arithmetic']:dict(contacts=len(r['allCompleteExact3DSurfaceContacts']['contacts']),strictCentroidInterior=len(r['strictSourceFaceCentroidInteriorWitnesses']))for r in rows}),flush=True)
if __name__=='__main__':main()
