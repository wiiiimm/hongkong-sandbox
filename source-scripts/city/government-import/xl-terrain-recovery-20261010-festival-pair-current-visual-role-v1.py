"""Complete current/source-bound Festival original structural + visual accounting.

Read-only deterministic replay; live publication remains root-owned. Every raw
physics/graph negative is retained; only precisely named source visual mounts
replace visual-component root demands. Actual full source/current gates remain.
"""
import importlib.util,json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as structural
from exact_original_georef_cell_identity_20261009 import verify_files as identity_verify
from festival_original_named_visual_mount_roles_v1_20261010 import verify as visual,canonical,WORLD,SOURCES
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-festival-pair-finite-sampler-current-v4-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-festival-pair-finite-sampler-current-original-support-v4'
FINITE=BASE/'xl-terrain-recovery-20261010-festival-pair-current-finite-sampler-paired-column-v3'
PROVIDER=BASE/'xl-terrain-recovery-20261010-festival-complete-original-provider-visual-mount-roles-v1'
BATCH='government-xl-terrain-recovery-festival-pair-current-typed-visual-role-v1-20261010';DOC=BASE/BATCH
MANIFEST='422e9d4df4478282d7745f9f804699e9acfbd807021710af5eb3c12925525e41'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def checked_receipt(folder):
 r=read(folder/'result.json');assert read(folder/'neon-sync.json')['resultVerified']
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert len({x['path'] for x in r['evidenceRefs']})==len(r['evidenceRefs'])
 for x in r['evidenceRefs']:assert ref(ROOT/x['path'])==x,'Frozen numeric/provider/physical dependency differs: '+x['path']
 return r
def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 receipts=[checked_receipt(p) for p in [PHYS,GRAPH,FINITE,PROVIDER]];physics=receipts[0]
 assert physics['manifestSHA256']==MANIFEST and physics['reasons']==['landsd/104302:0:ground-contact-unresolved','landsd/104302:0:sampled-ground-gap-below-model-bottom']
 rows=read(PHYS/'selection.json.gz')['rows'];contexts=read(PHYS/'context.json.gz')['rows'];assert {r['uid']:r['sourceSHA256'] for r in rows}==SOURCES
 current=read(manifest);installed=[]
 for u in current['officialModelCatalogues']:installed.extend(read(ROOT/'3d-viewer'/u)['models'])
 assert len({r['uid'] for r in installed})==len(installed) and not set(SOURCES)&{r['uid'] for r in installed}
 geometries=read(HERE/'local'/PHYS.name/'runtime-geometry.json.gz');assert {r['uid'] for r in geometries['rows']}==set(SOURCES)
 for p,h in geometries['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,'Current drawn runtime binding differs: '+p
 final=module('festival_actual_forms_current','xl-final-script-pass.py');terrain=read(PHYS/'terrain-candidates.json');assert len(terrain)==1 and set(terrain[0]['uids'])==set(SOURCES)
 formrows=final.load_forms(terrain[0]['bounds']);actualforms=[r[0] for r in formrows];neighbours=read(PHYS/'neighbour-inputs.json.gz');assert [r['building'] for r in neighbours['rows']]==actualforms and neighbours['candidateIds']==sorted(SOURCES)
 hashes={str((ROOT/'3d-viewer'/u).relative_to(ROOT)):digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in formrows};assert hashes==neighbours['inputHashes'] and len(actualforms)==physics['currentNeighbourForms']==91
 assert all(not r['reasons'] for r in read(PHYS/'neighbour-checks.json')['rows'])
 native=read(PHYS/'native-neighbour-checks.json');assert not set(native['blocked'])-set(native['resolved'])
 for p,h in native.get('inputHashes',native.get('hashes',{})).items():assert digest((ROOT/p).read_bytes())==h
 foundations=read(PHYS/'foundation.json')['rows'];assert {r['uid'] for r in foundations}==set(SOURCES)
 for f in foundations:
  x=f['foundation'];assert f['strictFoundationAccepted'] is True and x['completeTerrainTriangles']==x['triangles'] and x['fullyBuriedAreaFraction']==0 and x['fullyBuriedUpwardTriangles']==0
 validation=read(PHYS/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==2 and validation['exceptions']==0
 g=read(GRAPH/'diagnostic.json.gz');f=read(FINITE/'diagnostic.json.gz');provider=read(PROVIDER/'provider-role.json.gz');pieces=[];groundpieces=[];indexed=[];actors=[];identities=[];cursor=0;assetpaths=[]
 for row in rows:
  uid=row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==SOURCES[uid];assetpaths.append(asset);t=decode_original_world_triangles(raw);rt=next(v for v in geometries['rows'] if v['uid']==uid);idx=np.asarray(rt['index'],dtype=np.uint32).reshape(-1,3);positions=np.asarray(rt['position'],float).reshape(-1,3);world=positions[idx];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
  assert t.shape==world.shape and np.max(np.abs(t-world))<=1e-9
  ff=next(r for r in f['rows'] if r['uid']==uid);assert ff['completeOriginalWorldSHA256']==digest(t.tobytes()) and ff['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and ff['completeGroundSHA256']==digest(ground.tobytes())
  stream=source_stream_binding(raw);assert provider['completeOriginalProviderRootAndStreams'][uid]==stream
  with connect() as c:
   from run import NATIVE_RUN
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  context=next(c for c in contexts if c['uid']==uid);identity=identity_verify(row,context,HERE/'local'/PHYS.name);assert identity['passed'];saved=next(c for c in read(PHYS/'identity-proofs.json')['rows'] if c['uid']==uid);assert identity==saved;identities.append(identity)
  sourcepos=np.empty_like(positions);assigned={}
  for inds,face in zip(idx,t):
   for v,p in zip(inds,face):
    v=int(v)
    if v in assigned:assert np.array_equal(assigned[v],p)
    else:assigned[v]=p;sourcepos[v]=p
  assert set(assigned)==set(range(len(positions))) and np.array_equal(sourcepos[idx],t)
  actors.append(dict(uid=uid,sourceSHA256=digest(raw),originalStreamBindingSHA256=canonical(stream),globalFaceRange=[cursor,cursor+len(t)],completeOriginalFaceCount=len(t),originalWorldTrianglesSHA256=digest(t.tobytes())));indexed.append(dict(uid=uid,sourceSHA256=digest(raw),position=sourcepos.reshape(-1).tolist(),index=idx.reshape(-1).tolist()));pieces.append(t);groundpieces.append(ground);cursor+=len(t)
 tri=np.concatenate(pieces);ground=np.unique(np.concatenate(groundpieces).reshape(-1,9),axis=0).reshape(-1,3,3);assert digest(tri.tobytes())==WORLD and actors==g['actors']
 binding=dict(completeOriginalWorldTrianglesSHA256=WORLD,currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=digest((HERE/'local'/PHYS.name/'runtime-geometry.json.gz').read_bytes()),supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed));assert binding==g['binding']
 graph=structural(tri,actors,g['components'],g['contactWitnesses'],indexed,ground,expected_binding=binding,current_binding=binding);graph=json.loads(json.dumps(graph))
 for k,v in graph.items():assert g[k]==v,'Full current strict source graph replay differs: '+k
 vb=dict(completeOriginalWorldSHA256=WORLD,completeGraphSHA256=canonical(g),completeFiniteContextsSHA256=canonical(f),providerRolesSHA256=canonical(provider));visualproof=visual(tri,g,f,provider,expected_binding=vb,current_binding=vb)
 assert visualproof['allComponentsAccounted'] and visualproof['groundRootCredit'] is False and visualproof['structuralBridgeCredit'] is False
 assert ref(manifest)==start
 dependencies=[Path(__file__),HERE/'festival_original_named_visual_mount_roles_v1_20261010.py',HERE/'test_festival_original_named_visual_mount_roles_v1_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'test_exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',manifest,*assetpaths]
 for folder in [PHYS,GRAPH,FINITE,PROVIDER]:dependencies.extend(p for p in sorted(folder.iterdir()) if p.is_file())
 dependencies.extend([HERE/'local'/PHYS.name/'runtime-geometry.json.gz',ROOT/terrain[0]['path']]);refs=[ref(p) for p in sorted(set(dependencies))]
 return dict(uids=sorted(SOURCES),contract='complete-current-festival-original-structural-plus-named-visual-mount-acceptance-v1',currentManifest=start,sourceSHA256s=SOURCES,completeOriginalFaces=35006,completeOriginalComponents=279,completeCurrentNeighbourForms=91,completeCurrentSourceIdentities=identities,fullOrdinaryOriginalAndRenderedClearanceProved=True,allComponentsAccounted=True,completeStrictStructuralGraph=graph,namedVisualMountProof=visualproof,strictWholeSourceFoundationsPreserved=True,allForeignCurrentActorsRetained=True,rawPhysicalReasonsPreserved=physics['reasons'],replacedDiagnosticReasonsOnly=physics['reasons'],currentTypedPhysicalAccepted=True,reasons=[],terrainProposalGeometryChanged=True,terrainProposal=terrain,sourceGeometryChanges=0,aiGeometryModelling=False,visualStructuralCredit=False,publication=False,newlyInstalled=0,installationApproved=False,evidenceRefs=refs)
def main():
 assert not DOC.exists();result=recheck();save(DOC/'typed-role.json.gz',result);f=module('festival_role_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');f.freeze(BATCH,'festival-complete-current-original-structural-and-named-visual-mount-role-v1',[ROOT/x['path'] for x in result['evidenceRefs']],dict(uids=sorted(SOURCES),currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,terrainProposalGeometryChanged=True,completeOriginalFaces=35006,completeOriginalComponents=279,typedRole=ref(DOC/'typed-role.json.gz'),browserRequired=True,publication=False,newlyInstalled=0))
if __name__=='__main__':main()
