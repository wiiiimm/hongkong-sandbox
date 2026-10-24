"""Mei Yat complete current original assembly plus nonstructural visual mounts.

All ordinary original components independently root without the 121 details.
Every detail's unchanged original and literal mount is replayed. Complete current
19-form identity/foreign/native/terrain/foundation/runtime gates stay mandatory.
Historical numeric proof is reusable only with identical literal world and ground.
"""
import importlib.util,json,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as original_graph
from exact_original_paired_finite_clearance_v2_20261010 import verify as paired_clearance
from exact_original_georef_cell_identity_20261009 import apply_exact_cell
from mei_yat_original_named_visual_mounts_v1_20261010 import verify as named_mounts,canonical,WORLD,ACTUAL,SOURCE
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-mei-yat-current-complete-visual-support-v1';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-mei-yat-original-terrain-current-v4-20261010'
SUPPORT=BASE/'xl-terrain-recovery-20261010-mei-yat-fresh-original-support-replay-v1'
CLEARANCE=BASE/'xl-terrain-recovery-20261010-mei-yat-complete-paired-column-v1'
COARSE=BASE/'xl-terrain-recovery-20261010-mei-yat-complete-finite-clearance-v1'
ROLE=BASE/'xl-terrain-recovery-20261010-mei-yat-all-named-original-visual-mounts-v1'
OLD_PHYSICAL=BASE/'government-xl-terrain-recovery-mei-yat-original-physical-v3-20261010'
ARCHIVE=BASE/'xl-terrain-recovery-20261010-no1-garden-source-scope-declaration-v1/acceptance-manifest.json'
OLD_MANIFEST='a3a28145511e3ce6f0b0255d490e1219ad05c643030d00f3e4d9844cdf784b64'
GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';OLD_GEOMETRY=HERE/'local'/OLD_PHYSICAL.name/'runtime-geometry.json.gz'
MANIFEST=ROOT/'3d-viewer/city/data/manifest.json';UID='landsd/183776:0';TERRAIN_SHA='236965084f218668079721d9197867bf04fcf93bc6491ab7a08cd8a9096520e7'
def normalized(v):return json.loads(json.dumps(v))
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(doc,historical=False):
 r=read(doc/'result.json');assert read(doc/'neon-sync.json')==dict(jobId=r['jobId'],resultVerified=True)
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p in r['evidenceRefs']:
  if historical and p['path']=='3d-viewer/city/data/manifest.json':assert p['sha256']==OLD_MANIFEST==digest(ARCHIVE.read_bytes())
  else:assert ref(ROOT/p['path'])==p,'Changed frozen input: '+p['path']
 return r
def recheck():
 current=ref(MANIFEST);physical=receipt(PHYSICAL);sr=receipt(SUPPORT);cr=receipt(CLEARANCE,True);coarse=receipt(COARSE,True);rr=receipt(ROLE,True)
 selected=read(PHYSICAL/'selection.json.gz');assert selected['manifestSHA256']==current['sha256'] and len(selected['rows'])==1
 row=selected['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE and row['triangles']==10209
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE
 streams=source_stream_binding(raw);preflight=read(PHYSICAL/'current-source-terrain-preflight.json');assert streams==preflight['sourceProviderRootAndStreams'] and preflight['currentManifest']==current
 tri=decode_original_world_triangles(raw);runtime=read(GEOMETRY);assert len(runtime['rows'])==1;g=runtime['rows'][0];assert g['uid']==UID and g['sourceSHA256']==SOURCE
 for path,sha in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 p=np.asarray(g['position']).reshape(-1,3);idx=np.asarray(g['index'],np.uint32).reshape(-1,3);world=p[idx];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 old=read(OLD_GEOMETRY)['rows'][0]
 for key,dtype in [('position',np.float64),('index',np.uint32),('drawnGroundGeometry',np.float64)]:assert np.array_equal(np.asarray(g[key],dtype),np.asarray(old[key],dtype)),'Historical numerical proof requires literal current source/ground equality: '+key
 assert tri.shape==world.shape==(10209,3,3) and digest(tri.tobytes())==WORLD and digest(world.tobytes())==ACTUAL and np.max(np.abs(tri-world))<=1e-9
 original=np.empty_like(p);assigned={}
 for ids,face in zip(idx,tri):
  for i,v in zip(ids,face):
   i=int(i)
   if i in assigned:assert np.array_equal(assigned[i],v)
   else:assigned[i]=v;original[i]=v
 assert set(assigned)==set(range(len(original))) and np.array_equal(original[idx],tri)
 indexed=[dict(uid=UID,sourceSHA256=SOURCE,position=original.reshape(-1).tolist(),index=idx.reshape(-1).tolist())];unique=np.unique(ground.reshape(-1,9),axis=0).reshape(-1,3,3)
 binding=dict(completeOriginalWorldTrianglesSHA256=WORLD,currentDrawnGroundSHA256=digest(unique.tobytes()),groundInterfacesInputSHA256=digest(GEOMETRY.read_bytes()),supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed))
 graph=read(SUPPORT/'diagnostic.json.gz');assert graph['binding']==binding
 replay=normalized(original_graph(tri,graph['actors'],graph['components'],graph['contactWitnesses'],indexed,unique,expected_binding=binding,current_binding=binding));assert all(replay[k]==graph[k] for k in replay)
 assert len(graph['components'])==878 and len(replay['resolvedOriginalComponents'])==757 and replay['ordinaryGroundRootComponents']==[124] and not replay['supportInterfaceAccepted'] and not graph['wallRoleCredit']
 finite=read(CLEARANCE/'diagnostic.json.gz');prior=read(COARSE/'diagnostic.json.gz');assert len(finite['rows'])==len(prior['rows'])==1
 f=finite['rows'][0];c=prior['rows'][0];assert f['uid']==c['uid']==UID and f['sourceSHA256']==SOURCE and f['completeOriginalWorldSHA256']==WORLD and f['completeActualRenderedWorldSHA256']==ACTUAL and f['completeGroundSHA256']==digest(ground.tobytes())
 assert len(f['allFaces'])==len(c['allFaces'])==10209 and not f['unprovedOriginalFaces'] and not f['unprovedActualRenderedFaces']
 for i,r in enumerate(f['allFaces']):
  assert r['sourceFace']==i and r['priorCoarseBoundProofVerbatim']==c['allFaces'][i] and r['completeOriginalBoundProved'] is True and r['completeActualRenderedBoundProved'] is True
  for face,key,coarsekey in [(tri[i],'exactOriginalColumnRefinement','completeOriginal'),(world[i],'exactActualRenderedColumnRefinement','actualRendered')]:
   oldproof=r['priorCoarseBoundProofVerbatim'][coarsekey];assert oldproof['sourceFaceSHA256']==digest(face.tobytes()) and oldproof['completeCurrentGroundSHA256']==digest(ground.tobytes())
   refined=r[key]
   if refined is not None:assert normalized(paired_clearance(face,ground))==refined and refined['existingOrdinaryClearanceBoundProved'] is True
   else:assert oldproof['existingOrdinaryClearanceBoundProved'] is True and oldproof['groundProjectionCovered'] is True
 provider=read(ROLE/'conditional-provider-roles.json');assert provider['sourceSHA256']==digest(raw)==SOURCE
 mount_binding=dict(completeOriginalWorldSHA256=WORLD,completeLiteralWorldSHA256=ACTUAL,completeGraphSHA256=canonical(graph),completeFiniteContextsSHA256=canonical(finite),providerRolesSHA256=canonical(provider))
 mounts=normalized(named_mounts(tri,world,graph,finite,provider,expected_binding=mount_binding,current_binding=mount_binding));assert mounts['allComponentsAccounted'] and len(mounts['namedVisualOnlyComponents'])==121 and len(mounts['independentlyStructuralComponents'])==757
 candidates=read(PHYSICAL/'terrain-candidates.json');assert len(candidates)==1 and candidates[0]['uids']==[UID] and candidates[0]['sha256']==TERRAIN_SHA and ref(ROOT/candidates[0]['path'])['sha256']==TERRAIN_SHA and not candidates[0].get('replaces')
 bounds=candidates[0]['bounds'];patchshape=shapely.box(*bounds);manifest=read(MANIFEST)
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');final=module('mei_yat_fresh_forms','xl-final-script-pass.py');actual=final.load_forms(bounds)
 assert len(actual)==len(neighbours['rows'])==19 and {f['uid']:f for f,_,_ in actual}=={r['building']['uid']:r['building'] for r in neighbours['rows']}
 for path,sha in neighbours['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 context=read(PHYSICAL/'context.json.gz')['rows'][0];identity=read(PHYSICAL/'identity-proofs.json')['rows'][0];assert identity['uid']==UID and identity['passed'] is True
 sources=[];tiles={};prefix=row['modelId'][1:11]
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];forms=[f for f in read(path)['buildings'] if str(f.get('buildingCSUID') or '')[:10]==prefix]
  if forms:tiles[tile['url']]=digest(path.read_bytes());sources.extend(dict(building=f,tile=tile['url'],tileSHA256=digest(path.read_bytes())) for f in forms)
 route=module('mei_yat_original_routed_identity','routed_original_cell_identity.py');fresh=route.verify(raw,row,context,tri,current_identity=final.identity_context(row,tri,actual),sources=sources);fresh.update(exactRouteTileHashes=tiles,exactRouteManifestSHA256=current['sha256'])
 ib=dict(uid=UID,sourceSHA256=SOURCE,decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()));fresh=apply_exact_cell(fresh,tri,expected_binding=ib,current_binding=ib);assert normalized(fresh)==identity and fresh['passed'] is True
 native=[];catalogues=[]
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogues.append(ref(path))
  for e in read(path)['models']:
   assert e['uid']!=UID;b=np.asarray(e['worldBounds']);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all();assert shapely.box(b[0,0],b[0,2],b[1,0],b[1,2]).disjoint(patchshape),'Whole original native bounds touch proposed terrain: complete native physical scope required'
   native.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],completeOriginalWorldBounds=b.tolist()))
 assert len(native)==len({e['uid'] for e in native}) and all(not r['existingNative'] and not r['building'].get('modelGeometry') for r in neighbours['rows'])
 for routing in preflight['completeCurrentTerrainRouting']:assert ref(ROOT/routing['asset']['path'])==routing['asset'] and all(patchshape.disjoint(shapely.box(*b)) for b in routing['testedBounds'])
 assert [r['entry'] for r in preflight['completeCurrentTerrainRouting']]==manifest['terrainPatches']
 foundation=read(PHYSICAL/'foundation.json')['rows'][0];assert foundation['uid']==UID and foundation['sourceSHA256']==SOURCE and foundation['strictFoundationAccepted'] is True
 fc=foundation['foundation'];assert fc['completeTerrainTriangles']==fc['triangles']==10209 and fc['fullyBuriedTriangles']==fc['fullyBuriedUpwardTriangles']==0
 checks=read(PHYSICAL/'neighbour-checks.json');assert len(checks['rows'])==19 and not any(r['reasons'] for r in checks['rows']);nc=read(PHYSICAL/'native-neighbour-checks.json');assert not nc['blocked'] and not nc['rows']
 validation=read(PHYSICAL/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==1 and not validation['exceptions'];metrics=read(PHYSICAL/'metrics.json');assert len(metrics['rows'])==1;metric=metrics['rows'][0];assert metric['uid']==UID and metric['sourcePreserved'] is True and metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004
 policy=module('mei_yat_current_policy','acceptance-policy.py');numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),metric,metrics['profiles']['mobile']);assert not numeric and not physical['reasons'],'No independent current physical flag may be waived'
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 refs=[ref(p) for p in [Path(__file__),GEOMETRY,OLD_GEOMETRY,MANIFEST,ARCHIVE,asset,HERE/'mei_yat_original_named_visual_mounts_v1_20261010.py',HERE/'test_mei_yat_original_named_visual_mounts_v1_20261010.py',HERE/'exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'test_exact_original_facet_orthogonal_finite_facade_band_20261010.py',HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'exact_original_paired_finite_clearance_v2_20261010.py',HERE/'mei_yat_original_open_ended_ledge_geometry_v2_20261010.py',HERE/'test_mei_yat_original_open_ended_ledge_geometry_v2_20261010.py',HERE/'xl_source_stream_binding_20261009.py',ROLE/'conditional-provider-roles.json',SUPPORT/'diagnostic.json.gz',CLEARANCE/'diagnostic.json.gz',COARSE/'diagnostic.json.gz',PHYSICAL/'selection.json.gz',PHYSICAL/'identity-proofs.json',PHYSICAL/'metrics.json',PHYSICAL/'foundation.json',PHYSICAL/'validation.json',PHYSICAL/'neighbour-checks.json',PHYSICAL/'native-neighbour-checks.json',PHYSICAL/'neighbour-inputs.json.gz']]+catalogues
 # Historical current-manifest pointers remain in their original immutable
 # receipts; exact archive is supplied, never rewritten to a current hash.
 for doc in [PHYSICAL,SUPPORT,CLEARANCE,COARSE,ROLE]:refs.append(ref(doc/'result.json'))
 refs.extend(physical['evidenceRefs']);refs=sorted({(r['path'],r['sha256']):r for r in refs}.values(),key=lambda r:(r['path'],r['sha256']))
 assert all(ref(ROOT/r['path'])==r for r in refs) and ref(MANIFEST)==current
 return normalized(dict(uids=[UID],manifestSHA256=current['sha256'],completeOriginalFaces=10209,completeOriginalComponents=878,completeStructuralSupportGraph=replay,completeProviderRootAndStreams=streams,wholeOriginalAndActualRenderedFiniteClearance=ref(CLEARANCE/'diagnostic.json.gz'),literalCurrentNumericInputsExactlyHistorical=True,completeCurrentIdentities=[identity],completeNamedNonstructuralVisualMounts=mounts,completeCurrentActorScope=dict(currentFormsCount=19,currentForms=neighbours['rows'],currentTileHashes=neighbours['inputHashes'],allCurrentNativeWholeBoundsCount=len(native),allCurrentNativeWholeBoundsSHA256=canonical(native),allCurrentNativeCatalogueHashes=catalogues),sourceDecisions=[dict(uid=UID,rawPhysicalReasons=physical['reasons'],freshNumericReasons=numeric,sourceBoundResolvedReasons=[],rawOriginalUnrootedDetailReasonsRetained=replay['reasons'])],unresolvedIndependentPhysicalReasons=[],independentPhysicalChecksPassed=True,sourceGeometryChanges=0,terrainProposalChanged=False,visualRootCredit=0,visualBridgeCredit=0,installationApproved=False,publication=False,evidenceRefs=refs))
def main():
 assert not DOC.exists();claim=reservations.claim('mei-yat-complete-current-role-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  typed=recheck();save(DOC/'typed-role.json.gz',typed);module('mei_yat_role_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-mei-yat-original-structural-plus-visual-mounts-v1',[ROOT/r['path'] for r in typed['evidenceRefs']],dict(uids=[UID],manifestSHA256=typed['manifestSHA256'],completeOriginalFaces=10209,completeOriginalComponents=878,independentPhysicalChecksPassed=True,typedRole=ref(DOC/'typed-role.json.gz'),installationApproved=False));print(dict(independentPhysicalChecksPassed=True,originalStructuralParts=757,visualOnlyParts=121),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
