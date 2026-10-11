"""Complete original Man Oi acceptance; no source edits or waived physical flags.

The old runtime-coordinate graph is retained as a diagnostic. Its original
face memberships and witnesses are replayed on decoded source coordinates,
including every face, against the complete actual drawn terrain.
"""
import importlib.util,json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as original_graph
from exact_original_face_conservative_clearance_v4_20261010 import verify as clipped_clearance
from exact_original_georef_cell_identity_20261009 import apply_exact_cell

BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261010-man-oi-current-complete-support-v2';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-man-oi-complete-original-physical-v2-20261010'
SUPPORT=BASE/'government-xl-man-oi-complete-original-root-graph-20261010'
COARSE=BASE/'government-xl-man-oi-complete-original-rendered-clearance-20261010'
CLEARANCE=BASE/'government-xl-man-oi-complete-clipped-original-rendered-clearance-20261010'
GEOMETRY=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
CONTEXT=HERE/'local'/PHYSICAL.name/'frozen-inputs/context.json.gz'
MANIFEST=ROOT/'3d-viewer/city/data/manifest.json'
UID='landsd/75697:0';SOURCE='6c7de45ebc146c7be0eeef151d5f217ae0c0cd72525eb74d46077bbd66c0b80d'
TERRAIN_SHA='a86ea751c2c8fb14843999e590580199f4c3b4e67f6a8f9874dcde9b3dff9ebc'
def canonical(d):return digest(json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def normalized(d):return json.loads(json.dumps(d,allow_nan=False))
def ref(p):
 p=Path(p).resolve();assert p.is_relative_to(ROOT.resolve());return dict(path=str(p.relative_to(ROOT.resolve())),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(doc):
 r=read(doc/'result.json');assert read(doc/'neon-sync.json')==dict(jobId=r['jobId'],resultVerified=True)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p in r['evidenceRefs']:assert ref(ROOT/p['path'])==p,'Changed frozen input '+p['path']
 return r
def recheck():
 current=ref(MANIFEST);physical=receipt(PHYSICAL);receipt(SUPPORT);receipt(COARSE);receipt(CLEARANCE)
 assert physical['scriptChecksPassed'] is True and physical['reasons']==[]
 selected=read(PHYSICAL/'selection.json.gz');assert selected['manifestSHA256']==current['sha256'] and len(selected['rows'])==1
 row=selected['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE
 geometry=read(GEOMETRY);assert len(geometry['rows'])==1;g=geometry['rows'][0];assert g['uid']==UID and g['sourceSHA256']==SOURCE
 for p,h in geometry['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE
 streams=source_stream_binding(raw);tri=decode_original_world_triangles(raw)
 positions=np.asarray(g['position']).reshape(-1,3);indices=np.asarray(g['index'],np.uint32).reshape(-1,3);world=positions[indices]
 assert tri.shape==world.shape==(2160,3,3) and np.max(np.abs(tri-world))<=1e-9
 original=np.empty_like(positions);assigned={}
 for ids,face in zip(indices,tri):
  for i,v in zip(ids,face):
   i=int(i)
   if i in assigned:assert np.array_equal(assigned[i],v)
   else:assigned[i]=v;original[i]=v
 assert set(assigned)==set(range(len(original))) and np.array_equal(original[indices],tri)
 indexed=[dict(uid=UID,sourceSHA256=SOURCE,position=original.reshape(-1).tolist(),index=indices.reshape(-1).tolist())]
 ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert np.isfinite(ground).all()
 prior_graph=read(SUPPORT/'diagnostic.json.gz');assert prior_graph['completeOriginalFaces']==2160 and len(prior_graph['components'])==4
 actors=[dict(uid=UID,sourceSHA256=SOURCE,originalStreamBindingSHA256=canonical(streams),globalFaceRange=[0,2160],completeOriginalFaceCount=2160,originalWorldTrianglesSHA256=digest(tri.tobytes()))]
 components=[dict(actorUID=UID,globalOriginalFaces=c['globalOriginalFaces'],bounds=[tri[c['globalOriginalFaces']].min(axis=(0,1)).tolist(),tri[c['globalOriginalFaces']].max(axis=(0,1)).tolist()]) for c in prior_graph['components']]
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=ref(GEOMETRY)['sha256'],supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed))
 graph=normalized(original_graph(tri,actors,components,prior_graph['contactWitnesses'],indexed,ground,expected_binding=binding,current_binding=binding))
 assert graph['supportInterfaceAccepted'] is True and graph['reasons']==[] and graph['resolvedOriginalComponents']==[0,1,2,3] and graph['ordinaryGroundRootComponents']==[0]
 finite=read(CLEARANCE/'diagnostic.json.gz');coarse=read(COARSE/'diagnostic.json.gz');assert len(finite['rows'])==len(coarse['rows'])==1 and finite['allWholeOriginalAndRenderedBoundsProved'] is True
 f=finite['rows'][0];c=coarse['rows'][0]
 assert f['uid']==c['uid']==UID and f['sourceSHA256']==c['sourceSHA256']==SOURCE and f['completeOriginalWorldSHA256']==digest(tri.tobytes()) and f['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and f['completeGroundSHA256']==digest(ground.tobytes())
 assert len(f['allFaces'])==len(c['allFaces'])==2160 and f['unprovedOriginalFaces']==f['unprovedActualRenderedFaces']==[]
 for i,r in enumerate(f['allFaces']):
  assert r['sourceFace']==i and r['coarseOriginalAndRenderedProofVerbatim']==c['allFaces'][i] and r['completeOriginalBoundProved'] is True and r['completeActualRenderedBoundProved'] is True
  for face,key,oldkey in [(tri[i],'refinedOriginalFiniteProjectionBound','completeOriginal'),(world[i],'refinedActualRenderedFiniteProjectionBound','actualRendered')]:
   old=r['coarseOriginalAndRenderedProofVerbatim'][oldkey];assert old['sourceFaceSHA256']==digest(face.tobytes()) and old['completeCurrentGroundSHA256']==digest(ground.tobytes())
   new=r[key]
   if new is not None:assert normalized(clipped_clearance(face,ground))==new and new['existingOrdinaryClearanceBoundProved'] is True
   else:assert old['existingOrdinaryClearanceBoundProved'] is True and old['groundProjectionCovered'] is True
 patches=read(PHYSICAL/'terrain-candidates.json');assert len(patches)==1
 patch=patches[0];assert patch['uids']==[UID] and patch['sha256']==TERRAIN_SHA and ref(ROOT/patch['path'])['sha256']==TERRAIN_SHA and not patch.get('replaces') and not patch.get('replacesMany') and patch['triangles']==602
 bounds=patch['bounds'];patchshape=shapely.box(*bounds);manifest=read(MANIFEST)
 neighbours=read(PHYSICAL/'neighbour-inputs.json.gz');final=module('man_oi_current_forms','xl-final-script-pass.py');actual=final.load_forms(bounds)
 assert len(actual)==len(neighbours['rows'])==13 and {f['uid']:f for f,_,_ in actual}=={r['building']['uid']:r['building'] for r in neighbours['rows']} and all(not r['existingNative'] for r in neighbours['rows'])
 for p,h in neighbours['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 lo,hi=row['native']['model']['worldBounds'];identity_forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=read(CONTEXT)['rows'][0]
 assert context['identity']==final.identity_context(row,tri,identity_forms)
 identity=read(PHYSICAL/'owned-source-identity.json')['rows'][0];assert identity['uid']==UID and identity['passed'] is True
 sources=[];tiles={};prefix=row['modelId'][1:11]
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];forms=[f for f in read(p)['buildings'] if str(f.get('buildingCSUID') or '')[:10]==prefix]
  if forms:tiles[tile['url']]=ref(p)['sha256'];sources.extend(dict(building=f,tile=tile['url'],tileSHA256=ref(p)['sha256']) for f in forms)
 route=module('man_oi_exact_routed_identity','routed_original_cell_identity.py')
 fresh=route.verify(raw,row,context,tri,current_identity=final.identity_context(row,tri,identity_forms),sources=sources);fresh.update(exactRouteTileHashes=tiles,exactRouteManifestSHA256=current['sha256'])
 ib=dict(uid=UID,sourceSHA256=SOURCE,decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()));fresh=apply_exact_cell(fresh,tri,expected_binding=ib,current_binding=ib)
 assert normalized(fresh)==identity and fresh['passed'] is True
 native=[];catalogues=[]
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues.append(ref(p))
  for e in read(p)['models']:
   assert e['uid']!=UID;b=np.asarray(e['worldBounds']);assert b.shape==(2,3) and np.isfinite(b).all() and (b[1]>=b[0]).all()
   assert shapely.box(b[0,0],b[0,2],b[1,0],b[1,2]).disjoint(patchshape),'Native whole bounds require full retained actor checks'
   native.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],completeOriginalWorldBounds=b.tolist()))
 routing=[];bounds_helper=module('man_oi_routing_bounds','native_patch_resolution.py')
 for e in manifest['terrainPatches']:
  p=ROOT/'3d-viewer'/e['url'];data=read(p);tested=[b for b in [e.get('bounds'),data.get('bounds')] if b]
  if not tested:tested=[bounds_helper._patch_bounds(data)]
  assert tested and all(shapely.box(*b).disjoint(patchshape) for b in tested),'Current terrain intersects proposal'
  routing.append(dict(entry=e,asset=ref(p),testedBounds=tested))
 foundation=read(PHYSICAL/'foundation.json')['rows'][0];assert foundation['uid']==UID and foundation['sourceSHA256']==SOURCE and foundation['strictFoundationAccepted'] is True
 ctx=foundation['foundation'];assert ctx['completeTerrainTriangles']==ctx['triangles']==2160 and ctx['fullyBuriedTriangles']==ctx['fullyBuriedUpwardTriangles']==0
 checks=read(PHYSICAL/'neighbour-checks.json');assert len(checks['rows'])==13 and not any(r['reasons'] for r in checks['rows'])
 nc=read(PHYSICAL/'native-neighbour-checks.json');assert nc['blocked']==nc['rows']==nc['resolved']==[]
 validation=read(PHYSICAL/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==1 and type(validation['exceptions']) is int and validation['exceptions']==0
 metrics=read(PHYSICAL/'metrics.json');assert len(metrics['rows'])==1;m=metrics['rows'][0];assert m['uid']==UID and m['sourcePreserved'] is True and m['missingTerrain']==0 and m['maxSamplerDelta']==0
 policy=module('man_oi_numeric_policy','acceptance-policy.py');numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),m,metrics['profiles']['mobile']);assert numeric==[]
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 refs=[ref(p) for p in [Path(__file__),GEOMETRY,CONTEXT,MANIFEST,asset,HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'test_original_ordinary_ground_root_graph_20261009.py',HERE/'exact_original_face_conservative_clearance_v4_20261010.py',HERE/'test_exact_original_face_conservative_clearance_v4_20261010.py',HERE/'routed_original_cell_identity.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'acceptance-policy.py',HERE/'xl-final-script-pass.py',HERE/'native_patch_resolution.py']]+catalogues+[r['asset'] for r in routing]
 for d in [PHYSICAL,SUPPORT,CLEARANCE,COARSE]:refs.extend(receipt(d)['evidenceRefs']+[ref(d/'result.json')])
 refs=sorted({(r['path'],r['sha256']):r for r in refs}.values(),key=lambda r:(r['path'],r['sha256']))
 for r in refs:assert ref(ROOT/r['path'])==r
 assert ref(MANIFEST)==current
 return normalized(dict(uids=[UID],manifestSHA256=current['sha256'],completeOriginalFaces=2160,completeOriginalComponents=4,completeStructuralSupportGraph=graph,completeProviderRootAndStreams=streams,originalSupportGraphBinding=binding,rawRuntimeCoordinateGraph=ref(SUPPORT/'diagnostic.json.gz'),wholeOriginalAndActualRenderedFiniteClearance=ref(CLEARANCE/'diagnostic.json.gz'),completeCurrentIdentities=[identity],completeCurrentActorScope=dict(currentFormsCount=13,currentForms=neighbours['rows'],currentTileHashes=neighbours['inputHashes'],allCurrentNativeWholeBoundsCount=len(native),allCurrentNativeWholeBoundsSHA256=canonical(native),allCurrentNativeCatalogueHashes=catalogues),completeCurrentTerrainRouting=routing,sourceDecisions=[dict(uid=UID,rawPhysicalReasons=physical['reasons'],freshNumericReasons=numeric,sourceBoundResolvedReasons=[])],unresolvedIndependentPhysicalReasons=[],independentPhysicalChecksPassed=True,sourceGeometryChanges=0,terrainProposalChanged=False,visualRootCredit=0,visualBridgeCredit=0,installationApproved=False,publication=False,evidenceRefs=refs))
def main():
 assert not DOC.exists();typed=recheck();save(DOC/'typed-role.json.gz',typed)
 module('man_oi_role_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-man-oi-original-support-v2',[ROOT/r['path'] for r in typed['evidenceRefs']],dict(uids=[UID],manifestSHA256=typed['manifestSHA256'],completeOriginalFaces=2160,completeOriginalComponents=4,independentPhysicalChecksPassed=True,typedRole=ref(DOC/'typed-role.json.gz'),installationApproved=False))
 print(dict(independentPhysicalChecksPassed=True,completeOriginalComponents=4),flush=True)
if __name__=='__main__':main()
