"""Complete unchanged Park Haven source support and current finite acceptance.

No visual/wall role, identity exception or original geometry change is used.
The explicitly overlapping native-parent terrain proposal is measured, not
certified disjoint. Every source/literal facet and whole native gate remains.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as structural
from exact_original_georef_cell_identity_20261009 import verify_files as identity_verify
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-park-haven-overlapping-native-parent-original-pair-current-physical-v4-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-park-haven-v4-complete-original-support-v1'
FINITE=BASE/'xl-terrain-recovery-20261010-park-haven-v4-complete-paired-finite-clearance-v1'
BATCH='government-xl-terrain-recovery-park-haven-current-complete-ordinary-role-v1-20261010';DOC=BASE/BATCH
MANIFEST='44c9e80ec3999285616bb12a3fdfbe142a15855db7aa7c3216bffab3500f991a'
SOURCES={'landsd/246467:0':'de104bedd64810cec4253142280fa27e4c91d4d98807667852ec1073419c840d','landsd/320705:0':'53e7601fae7d72d2dcc4ee5d32002628c927769095cd6d9d07f5c2fa7afc95e9'}
NATIVE='landsd/246270:0';NATIVESHA='d5284c8d1c3bbe5e6d950660b77ba10e3b4b5e9672df7472137cf201a8de0394'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def module(n,f):
 s=importlib.util.spec_from_file_location(n,HERE/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(folder):
 r=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for item in r['evidenceRefs']:assert ref(ROOT/item['path'])==item
 return r

def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 receipts=[receipt(p) for p in [PHYS,GRAPH,FINITE]];expected_raw=['landsd/320705:0:ground-contact-unresolved','landsd/320705:0:sampled-ground-gap-below-model-bottom'];assert receipts[0]['reasons']==expected_raw
 selected=read(PHYS/'selection.json.gz');rows=selected['rows'];assert selected['manifestSHA256']==MANIFEST and [r['uid'] for r in rows]==list(SOURCES) and {r['uid']:r['sourceSHA256'] for r in rows}==SOURCES
 geometry=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(geometry);contexts=read(HERE/'local'/PHYS.name/'frozen-inputs/context.json.gz')['rows']
 for path,sha in runtime['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 candidates=read(PHYS/'terrain-candidates.json');assert len(candidates)==1;candidate=candidates[0];assert candidate['uids']==list(SOURCES) and ref(ROOT/candidate['path'])=={k:candidate[k] for k in ['path','sha256']}
 assert candidate['replaces']==dict(url='city/data/government-native-246270-0.json',sha256='f9820f73a85954da92964500179d3ac4f42b4edca203c5def4337f443490e765',retainedUids=[NATIVE])
 parentpath=ROOT/'3d-viewer'/candidate['replaces']['url'];assert ref(parentpath)['sha256']==candidate['replaces']['sha256'];parent=read(parentpath);proposal=read(ROOT/candidate['path']);assert proposal['meta']['targetUids']==[NATIVE,*SOURCES] and parent['meta']['targetUids']==[NATIVE]
 for key in ['w','h','cell','coarseCells','vegetation']:assert proposal.get(key)==parent.get(key)
 assert proposal['meta']['georef']==parent['meta']['georef'] and proposal['meta']['source']==parent['meta']['source']
 final=module('park_current_forms','xl-final-script-pass.py');forms=final.load_forms(candidate['bounds']);neighbours=read(PHYS/'neighbour-inputs.json.gz');assert [r['building'] for r in neighbours['rows']]==[b for b,_,_ in forms] and len(forms)==24 and neighbours['candidateIds']==sorted(SOURCES)
 assert {str((ROOT/'3d-viewer'/u).relative_to(ROOT)):digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in forms}==neighbours['inputHashes']
 checks=read(PHYS/'neighbour-checks.json');assert len(checks['rows'])==24
 for r in checks['rows']:assert not r['reasons'] or (r['uid']==NATIVE and r['reasons']==['existing-native-neighbour-requires-full-mesh-check'])
 native=read(PHYS/'native-neighbour-checks.json');assert native['blocked']==native['resolved']==[NATIVE] and len(native['rows'])==1 and native['rows'][0]['uid']==NATIVE and native['rows'][0]['passed'] is True and native['rows'][0]['triangles']==296
 for path,sha in native['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 foundation=read(PHYS/'foundation.json')['rows'];validation=read(PHYS/'validation.json');metrics=read(PHYS/'metrics.json');assert validation['checksPassed']==validation['loaderAccepted']==2 and validation['exceptions']==0
 g=read(GRAPH/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz');assert finite['allWholeOriginalAndRenderedBoundsProved'] is True
 pieces=[];literal=[];groundpieces=[];indexed=[];actors=[];assets=[];identities=[];cursor=0;roundoff=[]
 for row in rows:
  uid=row['uid'];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCES[uid];assets.append(asset);tri=decode_original_world_triangles(raw);rt=next(r for r in runtime['rows'] if r['uid']==uid);pos=np.asarray(rt['position'],float).reshape(-1,3);idx=np.asarray(rt['index'],np.uint32).reshape(-1,3);world=pos[idx];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);delta=float(np.max(np.abs(tri-world)));assert delta<=1e-9 and tri.shape==world.shape;roundoff.append(dict(uid=uid,maximumSourceRuntimeTransformRoundoffM=delta))
  f=next(r for r in finite['rows'] if r['uid']==uid);assert f['completeOriginalWorldSHA256']==digest(tri.tobytes()) and f['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and f['completeGroundSHA256']==digest(ground.tobytes()) and f['completeOriginalFaces']==len(tri) and not f['unprovedOriginalFaces'] and not f['unprovedActualRenderedFaces'] and len(f['allFaces'])==len(tri)
  for i,face in enumerate(f['allFaces']):assert face['sourceFace']==i and face['completeOriginalBoundProved'] is True and face['completeActualRenderedBoundProved'] is True and face['priorCoarseBoundProofVerbatim']['completeOriginal']['sourceFaceSHA256']==digest(tri[i].tobytes()) and face['priorCoarseBoundProofVerbatim']['actualRendered']['sourceFaceSHA256']==digest(world[i].tobytes())
  stream=source_stream_binding(raw)
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  identity=identity_verify(row,next(c for c in contexts if c['uid']==uid),HERE/'local'/PHYS.name/'current-ordinary-role-identity'/uid.split('/')[1]);assert identity['passed'] and identity==next(r for r in read(PHYS/'owned-source-identity.json')['rows'] if r['uid']==uid);identities.append(identity)
  assigned={};originalpos=np.empty_like(pos)
  for ids,face in zip(idx,tri):
   for i,v in zip(ids,face):
    i=int(i)
    if i in assigned:assert np.array_equal(assigned[i],v)
    else:assigned[i]=v;originalpos[i]=v
  assert set(assigned)==set(range(len(pos))) and np.array_equal(originalpos[idx],tri)
  actors.append(dict(uid=uid,sourceSHA256=SOURCES[uid],originalStreamBindingSHA256=canonical(stream),globalFaceRange=[cursor,cursor+len(tri)],completeOriginalFaceCount=len(tri),originalWorldTrianglesSHA256=digest(tri.tobytes())));indexed.append(dict(uid=uid,sourceSHA256=SOURCES[uid],position=originalpos.reshape(-1).tolist(),index=idx.reshape(-1).tolist()));pieces.append(tri);literal.append(world);groundpieces.append(ground);cursor+=len(tri)
  ff=next(r for r in foundation if r['uid']==uid);q=ff['foundation'];assert ff['strictFoundationAccepted'] is True and q['completeTerrainTriangles']==q['triangles']==len(tri) and q['fullyBuriedTriangles']==q['fullyBuriedUpwardTriangles']==0
  m=next(r for r in metrics['rows'] if r['uid']==uid);assert m['sourceSHA256']==SOURCES[uid] and m['sourcePreserved'] is True and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004
  if uid=='landsd/246467:0':assert m['minSurfaceGap']>=-.5 and m['minLowGap']<=.1 and m['maxLowGap']<=1
 tri=np.concatenate(pieces);ground=np.unique(np.concatenate(groundpieces).reshape(-1,9),axis=0).reshape(-1,3,3);assert actors==g['actors']
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=ref(geometry)['sha256'],supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed));assert binding==g['binding']
 graph=json.loads(json.dumps(structural(tri,actors,g['components'],g['contactWitnesses'],indexed,ground,expected_binding=binding,current_binding=binding)))
 for k,v in graph.items():assert g[k]==v,'Original ordinary full graph differs:'+k
 assert graph['supportInterfaceAccepted'] and not graph['reasons'] and len(graph['resolvedOriginalComponents'])==554 and graph['ordinaryGroundRootComponents']==[0]
 matches=[];catalogues=[];installed=set()
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues.append(ref(p))
  for e in read(p)['models']:
   assert e['uid'] not in installed;installed.add(e['uid'])
   if e['uid']==NATIVE:matches.append((p,e))
 assert len(matches)==1 and not installed&set(SOURCES);catalogue,entry=matches[0];nativeasset=catalogue.parent/entry['asset'];assert entry['sha256']==NATIVESHA==digest(nativeasset.read_bytes()) and entry['triangles']==296;nt=decode_original_world_triangles(nativeasset.read_bytes());assert len(nt)==296
 proofdoc=read(PHYS/'complete-original-native-projection-government-native-246270-0.json');assert proofdoc['currentParentURL']==candidate['replaces']['url'] and len(proofdoc['proofs'])==1;proof=proofdoc['proofs'][0]
 for item in proof['evidenceRefs']:assert ref(ROOT/item['path'])==item
 assert proof['contract']=='park-haven-explicit-overlapping-current-native-parent-terrain-proposal-v1' and proof['uid']==NATIVE and proof['everyOriginalFaceIncludingVerticalCollapsedAccounted'] and proof['terrainProposalGeometryChanged'] and proof['disjointProtectionAccepted'] is False and proof['nativeSourceProjectionStrictDisjoint'] is False and proof['sourceGeometryChanges']==0
 cover=shapely.geometry.shape(proof['coverGeometry']);npj=shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in nt]);spj=shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in tri]);assert cover.is_valid and cover.covers(npj) and digest(cover.wkb)==proof['coverWKB_SHA256']
 coords=shapely.get_coordinates(cover);assert np.array_equal(coords,coords.astype(np.float32).astype(float)) and np.array_equal(coords/.25,np.rint(coords/.25))
 assert float(npj.intersection(spj).area)==proof['nativeSourceProjectionIntersectionM2'] and float(cover.intersection(spj).area)==proof['proposedCoverSourceIntersectionM2']
 sb=proof['sourceAndCurrentBindings'];assert sb['completeOriginalActorBindings']==[dict(uid=a['uid'],sourceSHA256=a['sourceSHA256'],decodedWorldTrianglesSHA256=a['originalWorldTrianglesSHA256']) for a in actors] and sb['currentManifestSHA256']==MANIFEST and sb['currentNativeParentSHA256']==ref(parentpath)['sha256'] and sb['nativeCatalogueSHA256']==ref(catalogue)['sha256'] and sb['nativeSourceSHA256']==NATIVESHA and sb['nativeDecodedWorldTrianglesSHA256']==digest(nt.tobytes()) and sb['sourceDecodedWorldTrianglesSHA256']==digest(tri.tobytes())
 assert proof['completeCurrentNativeOriginalFaces']==296 and proof['completeNewOriginalSourceFaces']==11173
 assert ref(manifest)==start
 paths=[Path(__file__),geometry,parentpath,manifest,ROOT/candidate['path'],nativeasset,catalogue,HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',*assets]
 refs=[ref(p) for p in paths]+catalogues
 for folder in [PHYS,GRAPH,FINITE]:refs.extend(ref(p) for p in sorted(folder.iterdir()) if p.is_file())
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path'])
 return dict(contract='park-haven-complete-current-ordinary-original-support-v1',uids=sorted(SOURCES),currentManifest=start,sourceSHA256s=SOURCES,completeOriginalFaces=11173,completeOriginalComponents=554,completeCurrentNeighbourForms=24,completeCurrentSourceIdentities=identities,completeStrictStructuralGraph=graph,fullOrdinaryOriginalAndRenderedClearanceProved=True,sourceRuntimeRoundoff=roundoff,strictWholeSourceFoundationsPreserved=True,allCurrentRetainedNativeChecksPassed=True,completeCurrentRetainedNativeChecks=native,explicitOverlappingNativeParentProposal=proof,terrainProposalGeometryChanged=True,terrainProposal=candidates,rawPhysicalReasonsPreserved=expected_raw,replacedDiagnosticReasonsOnly=expected_raw,currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,aiGeometryModelling=False,visualRoleCredit=False,wallRoleCredit=False,publication=False,newlyInstalled=0,installationApproved=False,evidenceRefs=refs)
def main():
 assert not DOC.exists();r=recheck();save(DOC/'typed-role.json.gz',r);f=module('freeze_park_current','xl-popcorn-source-investigations-checkpoints-20261009.py');f.freeze(BATCH,'complete-current-original-two-source-all-ordinary-support-v1',[ROOT/x['path'] for x in r['evidenceRefs']],dict(uids=sorted(SOURCES),currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,terrainProposalGeometryChanged=True,completeOriginalFaces=11173,completeOriginalComponents=554,typedRole=ref(DOC/'typed-role.json.gz'),browserRequired=True,publication=False,newlyInstalled=0));print(dict(passed=True,faces=11173,parts=554,foreign=24),flush=True)
if __name__=='__main__':main()
