"""Four complete original/literal/F32 streams on frozen current drawn ground.

Read-only diagnostic: exact finite coverage/clearance, ordinary genuine roots,
nonzero-edge components and complete positive-facet interfaces. Zero faces stay
inventoried without structural credit. No actor/physical/runtime exemption.
"""
import importlib.util,json,time
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_wall_rim_accounting_20261009 import original_samples
from original_ordinary_rim_accounting_20261009 import verify as rim
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-vancor-basic-parent-core-apron-current-physical-v3-20261011'
ACTUAL=BASE/'government-xl-vancor-own-retained-actual-render-capture-v2-20261011'
BATCH='government-xl-vancor-four-stream-complete-current-finite-support-v1-20261011';DOC=BASE/BATCH
UID='landsd/147956:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();refs=[Path(__file__)];receipts=[]
 for folder in [PHYS,ACTUAL]:
  r=read(folder/'result.json');receipts.append(r)
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);physical=read(PHYS/'diagnostic.json');assert physical['currentManifest']==start and physical['rawReasons']==[]
 sel=read(PHYS/'selection.json.gz')['rows'][0];asset=ROOT/sel['candidate']['path'];assert sel['uid']==UID and digest(asset.read_bytes())==sel['sourceSHA256']
 captured=read(ACTUAL/'complete-actual-render-geometry.json.gz');a=next(r for r in captured['rows']if r['uid']==UID);assert a['sourceSHA256']==sel['sourceSHA256'] and captured['startAndEndInputsVerified']
 runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath)['rows'][0];assert runtime['uid']==UID and runtime['sourceSHA256']==sel['sourceSHA256']
 index=np.asarray(a['completeOriginalIndex'],int).reshape(-1,3);streams={'providerOriginal':decode_original_world_triangles(asset.read_bytes())}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(a[key],dtype='<f8').reshape(-1,3)[index]
 ground=np.asarray(runtime['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);literal=np.asarray(runtime['position'],dtype='<f8').reshape(-1,3)[np.asarray(runtime['index'],int).reshape(-1,3)];assert np.array_equal(literal,streams['actualLiteral']) and len(ground)>0
 for path,sha in captured['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 for p in [runtimepath,asset,manifest,PHYS/'diagnostic.json',PHYS/'selection.json.gz',ACTUAL/'complete-actual-render-geometry.json.gz']:assert ref(p)in receipts[0]['evidenceRefs']or ref(p)in receipts[1]['evidenceRefs'];refs.append(p)
 height=module('vancor_frozen_exact_height','xl-lee-kong-two-independent-original-tin-body-graph-diagnostic-v1-20261011.py').height
 outputs=[];cache={};clock=time.monotonic()
 for mode,world in streams.items():
  assert world.shape==(669,3,3) and np.isfinite(world).all();faces=[]
  for i,face in enumerate(world):
   key=digest(face.tobytes())
   if key not in cache:
    first=coarse(face,ground);second=None if first['existingOrdinaryClearanceBoundProved']else paired(face,ground)
    cache[key]=dict(coarse=first,paired=second,finiteBoundProved=first['existingOrdinaryClearanceBoundProved']or bool(second and second['existingOrdinaryClearanceBoundProved']))
   faces.append(dict(sourceFace=i,**cache[key]))
   if time.monotonic()-clock>20:print(json.dumps(dict(mode=mode,faces=i,total=669)),flush=True);clock=time.monotonic()
  top=census(world,list(range(669)));groups=top['sharedEdgeConnectedComponents'];parts=[];roots=[];edges=[];adj={i:set()for i in range(len(groups))}
  for i,ids in enumerate(groups):
   p,inv=np.unique(world[ids].reshape(-1,3),axis=0,return_inverse=True);ix=inv.reshape(-1,3);assert np.array_equal(p[ix],world[ids]);bottom=float(p[:,1].min());samples=original_samples(p,ix,bottom);error=None;proof=None
   try:
    for s in samples:s['ground']=height(s['point'],ground);s['gap']=s['point'][1]-s['ground']
    low=[s for s in samples if s['point'][1]<=bottom+.35];metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(s['gap']for s in samples),minLowGap=min(s['gap']for s in low),maxLowGap=max(s['gap']for s in low));proof=rim(p,ix,bottom,samples,expected_metric=metric);roots.append(i)
   except AssertionError as e:error=str(e)
   parts.append(dict(component=i,completeFaceIds=ids,completeOrdinarySamples=samples,ordinaryRootProof=proof,rawOrdinaryRootFailure=error))
  for i,ids in enumerate(groups):
   for j in range(i+1,len(groups)):
    aa,bb=world[ids],world[groups[j]]
    if np.any(aa.max((0,1))<bb.min((0,1)))or np.any(bb.max((0,1))<aa.min((0,1))):edges.append(dict(components=[i,j],strictClosedBoundsDisjoint=True));continue
    contact=exact_finite_contacts(world,ids,world,groups[j]);assert contact['allPairsExamined'];positive=[v for v in contact['contacts']if v['dimension']>0 and v['sourcePrimitiveDimensionA']==v['sourcePrimitiveDimensionB']==2]
    if positive:adj[i].add(j);adj[j].add(i)
    edges.append(dict(components=[i,j],completeExactContactProof=contact,positiveFacetInterfaces=len(positive)))
  reached=set(roots);todo=list(roots)
  while todo:
   i=todo.pop()
   for j in sorted(adj[i]):
    if j not in reached:reached.add(j);todo.append(j)
  outputs.append(dict(arithmetic=mode,completeWorldSHA256=digest(world.tobytes()),completeFaces=669,completeGroundSHA256=digest(ground.tobytes()),completeGroundFaces=len(ground),allFaces=faces,unprovedFiniteFaces=[v['sourceFace']for v in faces if not v['finiteBoundProved']],completeTopology=top,completeComponents=parts,completeBodyInterfaces=edges,ordinaryRoots=roots,reachableComponents=sorted(reached),unresolvedComponents=sorted(set(adj)-reached)))
 out=dict(uid=UID,sourceSHA256=sel['sourceSHA256'],currentManifest=start,rows=outputs,allFourStreamsCompleteFiniteAndRooted=all(not r['unprovedFiniteFaces']and not r['unresolvedComponents']for r in outputs),rawPhysicalReasons=[],sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,installationApproved=False)
 save(DOC/'diagnostic.json.gz',out)
 refs += [HERE/name for name in ['exact_packed_world_geometry_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_closed_projection_intersection_20261010.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','original_wall_rim_accounting_20261009.py','original_ordinary_rim_accounting_20261009.py','xl-lee-kong-two-independent-original-tin-body-graph-diagnostic-v1-20261011.py']]
 assert ref(manifest)==start
 for path,sha in captured['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 module('vancor_four_stream_proof_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-four-stream-exact-finite-ordinary-root-and-positive-interface-diagnostic-only',refs,dict(uids=[UID],allFourStreamsCompleteFiniteAndRooted=out['allFourStreamsCompleteFiniteAndRooted'],currentAcceptance=False,newlyInstalled=0))
 print(json.dumps({r['arithmetic']:dict(unproved=r['unprovedFiniteFaces'],unresolved=r['unresolvedComponents'])for r in outputs}),flush=True)
if __name__=='__main__':main()
