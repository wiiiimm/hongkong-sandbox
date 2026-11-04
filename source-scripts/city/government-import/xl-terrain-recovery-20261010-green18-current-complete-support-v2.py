"""Green18 current acceptance composition with complete genuine original support.

Only the raw global-bottom support warning can be resolved. Whole original and
rendered clearance, source/provider streams, original graph, identities, all
current foreign forms/native bounds, terrain routing, foundation and runtime
remain independently mandatory. No visual roles or geometry changes.
"""
import importlib.util,json,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as original_graph
from exact_original_paired_finite_clearance_20261010 import verify as paired_clearance
from exact_original_georef_cell_identity_20261009 import apply_exact_cell
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-green18-current-complete-support-v2';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-green18-original-terrain-current-v1-20261010';SUPPORT=BASE/'xl-terrain-recovery-20261010-green18-fresh-original-support-replay-v1';CLEARANCE=BASE/'xl-terrain-recovery-20261010-green18-complete-paired-finite-clearance-v1';COARSE=BASE/'xl-terrain-recovery-20261010-green18-complete-finite-clearance-v2'
GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';MANIFEST=ROOT/'3d-viewer/city/data/manifest.json';UID='landsd/6462:0';SOURCE='d2d2c62ed2d29ffbf7ec4060c108f1c53eb784558120cb153a5d9482d60d493f';TERRAIN_SHA='a092210b53f0d4a7286a9a1d10b262c8094058f9c14f6b8a6007cde73d3b6077'
def canonical(d):return digest(json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def normalized(d):return json.loads(json.dumps(d))
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(doc):
 r=read(doc/'result.json');assert read(doc/'neon-sync.json')==dict(jobId=r['jobId'],resultVerified=True)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p in r['evidenceRefs']:assert ref(ROOT/p['path'])==p,'Changed frozen input '+p['path']
 return r
def recheck():
 current=digest(MANIFEST.read_bytes());physical=receipt(PHYSICAL);sr=receipt(SUPPORT);cr=receipt(CLEARANCE);coarse=receipt(COARSE)
 selected=read(PHYSICAL/'selection.json.gz');assert selected['manifestSHA256']==current and len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE
 geometry=read(GEOMETRY);assert len(geometry['rows'])==1;g=geometry['rows'][0];assert g['uid']==UID and g['sourceSHA256']==SOURCE
 for p,h in geometry['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE;streams=source_stream_binding(raw);preflight=read(PHYSICAL/'current-source-terrain-preflight.json');assert streams==preflight['sourceProviderRootAndStreams'] and preflight['currentManifest']==ref(MANIFEST)
 tri=decode_original_world_triangles(raw);positions=np.asarray(g['position']).reshape(-1,3);indices=np.asarray(g['index'],np.uint32).reshape(-1,3);world=positions[indices];assert tri.shape==world.shape==(11088,3,3) and np.max(np.abs(tri-world))<=1e-9 and digest(tri.tobytes())==preflight['decodedOriginalWorldSHA256']
 original=np.empty_like(positions);assigned={}
 for ids,face in zip(indices,tri):
  for i,v in zip(ids,face):
   i=int(i)
   if i in assigned:assert np.array_equal(assigned[i],v)
   else:assigned[i]=v;original[i]=v
 assert set(assigned)==set(range(len(original))) and np.array_equal(original[indices],tri)
 indexed=[dict(uid=UID,sourceSHA256=SOURCE,position=original.reshape(-1).tolist(),index=indices.reshape(-1).tolist())];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);unique=np.unique(ground.reshape(-1,9),axis=0).reshape(-1,3,3)
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(unique.tobytes()),groundInterfacesInputSHA256=digest(GEOMETRY.read_bytes()),supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed))
 graph=read(SUPPORT/'diagnostic.json.gz');assert graph['binding']==binding;replay=normalized(original_graph(tri,graph['actors'],graph['components'],graph['contactWitnesses'],indexed,unique,expected_binding=binding,current_binding=binding));assert all(replay[k]==graph[k] for k in replay)
 assert replay['supportInterfaceAccepted'] and not replay['reasons'] and len(graph['components'])==len(replay['resolvedOriginalComponents'])==903 and len(replay['ordinaryGroundRootComponents'])==5
 assert not graph['wallRoleCredit'] and graph['completeOriginalFaces']==11088
 finite=read(CLEARANCE/'diagnostic.json.gz');prior=read(COARSE/'diagnostic.json.gz');assert len(finite['rows'])==len(prior['rows'])==1 and finite['allWholeOriginalAndRenderedBoundsProved'];f=finite['rows'][0];c=prior['rows'][0]
 assert f['uid']==c['uid']==UID and f['sourceSHA256']==SOURCE and f['completeOriginalWorldSHA256']==digest(tri.tobytes()) and f['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and f['completeGroundSHA256']==digest(ground.tobytes()) and len(f['allFaces'])==len(c['allFaces'])==11088 and not f['unprovedOriginalFaces'] and not f['unprovedActualRenderedFaces']
 for i,r in enumerate(f['allFaces']):
  assert r['sourceFace']==i and r['priorCoarseBoundProofVerbatim']==c['allFaces'][i] and r['completeOriginalBoundProved'] and r['completeActualRenderedBoundProved']
  for face,key,coarsekey in [(tri[i],'pairedExactOriginalFiniteBound','completeOriginal'),(world[i],'pairedExactActualRenderedFiniteBound','actualRendered')]:
   old=r['priorCoarseBoundProofVerbatim'][coarsekey];assert old['sourceFaceSHA256']==digest(face.tobytes()) and old['completeCurrentGroundSHA256']==digest(ground.tobytes())
   new=r[key]
   if new is not None:assert normalized(paired_clearance(face,ground))==new and new['existingOrdinaryClearanceBoundProved']
   else:assert old['existingOrdinaryClearanceBoundProved'] and old['groundProjectionCovered'] is True
 patches=read(PHYSICAL/'terrain-candidates.json');assert len(patches)==1 and patches[0]['uids']==[UID] and patches[0]['sha256']==TERRAIN_SHA and ref(ROOT/patches[0]['path'])['sha256']==TERRAIN_SHA and not patches[0].get('replaces');bounds=patches[0]['bounds'];patchshape=shapely.box(*bounds)
 context=read(PHYSICAL/'context.json.gz')['rows'][0];identity=read(PHYSICAL/'identity-proofs.json')['rows'][0];assert identity['uid']==UID and identity['passed']
 # Recompute source identity in memory only; no install replay writes.
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');final=module('green18_replay_current_forms','xl-final-script-pass.py');actual=final.load_forms(bounds)
 assert len(actual)==len(neighbours['rows']) and {f['uid']:f for f,_,_ in actual}=={r['building']['uid']:r['building'] for r in neighbours['rows']}
 sources=[];tiles={};prefix=row['modelId'][1:11]
 for tile in read(MANIFEST)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];forms=[f for f in read(p)['buildings'] if str(f.get('buildingCSUID') or '')[:10]==prefix]
  if forms:tiles[tile['url']]=digest(p.read_bytes());sources.extend(dict(building=f,tile=tile['url'],tileSHA256=digest(p.read_bytes())) for f in forms)
 route=module('green18_original_routed_identity','routed_original_cell_identity.py');fresh=route.verify(raw,row,context,tri,current_identity=final.identity_context(row,tri,actual),sources=sources);fresh.update(exactRouteTileHashes=tiles,exactRouteManifestSHA256=current)
 ib=dict(uid=UID,sourceSHA256=SOURCE,decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()));fresh=apply_exact_cell(fresh,tri,expected_binding=ib,current_binding=ib);assert normalized(fresh)==identity and fresh['passed']
 for p,h in neighbours['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 manifest=read(MANIFEST);native=[];catalogues=[]
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues.append(ref(p))
  for e in read(p)['models']:
   assert e['uid']!=UID;b=np.asarray(e['worldBounds']);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all();shape=shapely.box(b[0,0],b[0,2],b[1,0],b[1,2]);assert shape.disjoint(patchshape),'Current native whole bounds touch terrain proposal; full native context required';native.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],completeOriginalWorldBounds=b.tolist()))
 assert len(actual)==len(neighbours['rows'])==4 and all(not r['existingNative'] for r in neighbours['rows'])
 for p in preflight['completeCurrentTerrainRouting']:assert ref(ROOT/p['asset']['path'])==p['asset'] and all(patchshape.disjoint(shapely.box(*b)) for b in p['testedBounds'])
 assert [r['entry'] for r in preflight['completeCurrentTerrainRouting']]==manifest['terrainPatches']
 foundation=read(PHYSICAL/'foundation.json')['rows'][0];assert foundation['uid']==UID and foundation['sourceSHA256']==SOURCE and foundation['strictFoundationAccepted'];ctx=foundation['foundation'];assert ctx['completeTerrainTriangles']==ctx['triangles']==11088 and ctx['fullyBuriedTriangles']==ctx['fullyBuriedUpwardTriangles']==0
 checks=read(PHYSICAL/'neighbour-checks.json');assert len(checks['rows'])==4 and not any(r['reasons'] for r in checks['rows']);nc=read(PHYSICAL/'native-neighbour-checks.json');assert not nc['blocked'] and not nc['rows']
 validation=read(PHYSICAL/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==1 and not validation['exceptions'];metrics=read(PHYSICAL/'metrics.json');assert len(metrics['rows'])==1;m=metrics['rows'][0];assert m['uid']==UID and m['sourcePreserved'] and not m['missingTerrain'] and m['maxSamplerDelta']<=.004
 policy=module('green18_current_policy','acceptance-policy.py');numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),m,metrics['profiles']['mobile']);allreasons=set(numeric+physical['reasons']);assert allreasons=={'ground-contact-unresolved'},allreasons
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 refs=[ref(p) for p in [Path(__file__),GEOMETRY,MANIFEST,asset,HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'test_original_ordinary_ground_root_graph_20261009.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'test_exact_original_paired_finite_clearance_20261010.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'test_exact_projection_coverage_v2_20261010.py',HERE/'test_exact_projection_coverage_v2_actual_green18_20261010.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'acceptance-policy.py',HERE/'xl-final-script-pass.py']]+catalogues
 for d in [PHYSICAL,SUPPORT,CLEARANCE,COARSE]:refs.extend(receipt(d)['evidenceRefs']+[ref(d/'result.json')])
 refs=sorted({(r['path'],r['sha256']):r for r in refs}.values(),key=lambda r:(r['path'],r['sha256']))
 for r in refs:assert ref(ROOT/r['path'])==r
 assert digest(MANIFEST.read_bytes())==current
 return normalized(dict(uids=[UID],manifestSHA256=current,completeOriginalFaces=11088,completeOriginalComponents=903,completeStructuralSupportGraph=replay,completeProviderRootAndStreams=streams,wholeOriginalAndActualRenderedFiniteClearance=ref(CLEARANCE/'diagnostic.json.gz'),completeCurrentIdentities=[identity],completeCurrentActorScope=dict(currentFormsCount=4,currentForms=neighbours['rows'],currentTileHashes=neighbours['inputHashes'],allCurrentNativeWholeBoundsCount=len(native),allCurrentNativeWholeBoundsSHA256=canonical(native),allCurrentNativeCatalogueHashes=catalogues),sourceDecisions=[dict(uid=UID,rawPhysicalReasons=physical['reasons'],freshNumericReasons=numeric,sourceBoundResolvedReasons=['ground-contact-unresolved'])],unresolvedIndependentPhysicalReasons=[],independentPhysicalChecksPassed=True,sourceGeometryChanges=0,terrainProposalChanged=False,visualRootCredit=0,visualBridgeCredit=0,installationApproved=False,publication=False,evidenceRefs=refs))
def main():
 assert not DOC.exists();claim=reservations.claim('green18-current-complete-support-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  typed=recheck();save(DOC/'typed-role.json.gz',typed);module('green18_role_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-green18-original-support-v1',[ROOT/r['path'] for r in typed['evidenceRefs']],dict(uids=[UID],manifestSHA256=typed['manifestSHA256'],completeOriginalFaces=11088,completeOriginalComponents=903,independentPhysicalChecksPassed=True,typedRole=ref(DOC/'typed-role.json.gz'),installationApproved=False));print(dict(independentPhysicalChecksPassed=True,completeOriginalComponents=903))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
