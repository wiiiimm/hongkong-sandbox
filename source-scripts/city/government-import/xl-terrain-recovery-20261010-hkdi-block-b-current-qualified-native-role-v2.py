"""Owned HKDI B acceptance through unchanged, narrowly qualified installed caps.

Native22089 is not reaccepted; every old failure remains. All owned original and
literal facets/foundation/identity/current actors/loader/sampler gates stay strict.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify as structural
from exact_original_georef_cell_identity_20261009 import verify_files as identity
from hkdi_owned_block_b_current_native_cap_support_20261010 import verify as owned_support
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-terrain-recovery-hkdi-block-b-unchanged-current-terrain-physical-v2-20261010';PROBE=BASE/'government-xl-terrain-recovery-hkdi-complete-original-current-probe-v1-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-hkdi-native-and-block-b-complete-original-support-v1';FINITE=BASE/'xl-terrain-recovery-20261010-hkdi-complete-native-and-original-paired-finite-v1';CAPS=BASE/'government-xl-terrain-recovery-hkdi-block-b-current-exposed-native-cap-paths-v2-20261010';ROOTS=BASE/'government-xl-terrain-recovery-hkdi-current-native-literal-ground-roots-v3-20261010'
BATCH='government-xl-terrain-recovery-hkdi-block-b-current-qualified-native-role-v2-20261010';DOC=BASE/BATCH
OWNED='landsd/89613:0';NATIVE='landsd/22089:0';SOURCES={NATIVE:'5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40',OWNED:'447d5391c1e8f0044ac5b86b6597d11392ea861cac3389fe2b3e81413ebbdc34'}
MANIFEST='44c9e80ec3999285616bb12a3fdfbe142a15855db7aa7c3216bffab3500f991a'
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(n,f):
 s=importlib.util.spec_from_file_location(n,HERE/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(folder):
 r=read(folder/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for x in r['evidenceRefs']:assert ref(ROOT/x['path'])==x
 return r

def recheck():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 for folder in [PHYS,PROBE,GRAPH,FINITE,CAPS,ROOTS]:receipt(folder)
 physical=read(PHYS/'result.json');raw=['ground-contact-unresolved','sampled-ground-gap-below-model-bottom'];assert physical['reasons']==raw and physical['manifestSHA256']==MANIFEST
 selected=read(PHYS/'selection.json.gz');assert selected['manifestSHA256']==MANIFEST and len(selected['rows'])==1
 row=selected['rows'][0];assert row['uid']==OWNED and row['sourceSHA256']==SOURCES[OWNED]
 runtimepath=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';runtime=read(runtimepath);assert len(runtime['rows'])==1;rt=runtime['rows'][0];assert rt['uid']==OWNED
 for p,h in runtime['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 assert read(PHYS/'terrain-candidates.json')==[] and read(PHYS/'terrain.json')['patches']==[]
 pre=read(PHYS/'current-source-terrain-preflight.json');assert pre['currentManifest']==start and pre['sourceSHA256']==SOURCES[OWNED]
 current=read(manifest);assert len(pre['completeCurrentTerrainRouting'])==len(current['terrainPatches'])
 for r,e in zip(pre['completeCurrentTerrainRouting'],current['terrainPatches']):assert r['entry']==e and ref(ROOT/r['asset']['path'])==r['asset']
 assert ref(ROOT/pre['rootTerrain']['path'])==pre['rootTerrain']
 final=module('hkdi_current_full_forms','xl-final-script-pass.py');tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);neighbours=read(PHYS/'neighbour-inputs.json.gz');assert len(forms)==2 and [b for b,_,_ in forms]==[r['building']for r in neighbours['rows']] and neighbours['candidateIds']==[OWNED]
 assert {str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms}==neighbours['inputHashes']
 checks=read(PHYS/'neighbour-checks.json');assert len(checks['rows'])==2 and all(not r['reasons']for r in checks['rows'])
 native=read(PHYS/'native-neighbour-checks.json');assert native['blocked']==native['resolved']==[NATIVE] and len(native['rows'])==1 and native['rows'][0]['passed']is True and native['rows'][0]['triangles']==3965
 for p,h in native['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 validation=read(PHYS/'validation.json');assert validation['checksPassed']==validation['loaderAccepted']==1 and validation['exceptions']==0
 ff=read(PHYS/'foundation.json')['rows'][0];f=ff['foundation'];assert ff['uid']==OWNED and ff['sourceSHA256']==SOURCES[OWNED] and ff['strictFoundationAccepted']is True and f['completeTerrainTriangles']==f['triangles']==11593 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
 metrics=read(PHYS/'metrics.json');m=metrics['rows'][0];assert m['uid']==OWNED and m['sourceSHA256']==SOURCES[OWNED] and m['sourcePreserved']is True and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004
 context=read(PHYS/'context.json.gz')['rows'][0];ident=identity(row,context,HERE/'local'/PHYS.name/'identity-current');assert ident['passed'] and ident==read(PHYS/'identity-proofs.json')['rows'][0]
 installed={};catalogues=[]
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogues.append(ref(p))
  for e in read(p)['models']:assert e['uid']not in installed;installed[e['uid']]=(p,e)
 assert OWNED not in installed and NATIVE in installed;cat,entry=installed[NATIVE];nativeasset=cat.parent/entry['asset'];assert entry['sha256']==SOURCES[NATIVE]==digest(nativeasset.read_bytes()) and entry['triangles']==3965
 probe_runtime=read(HERE/'local'/PROBE.name/'runtime-geometry.json.gz');probe_rows=read(PROBE/'selection.json.gz')['rows'];g=read(GRAPH/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz');pieces=[];actualpieces=[];groundpieces=[];indexed=[];actors=[];assets=[];cursor=0
 for uid in [NATIVE,OWNED]:
  source=next(r for r in probe_rows if r['uid']==uid);asset=ROOT/source['candidate']['path'];blob=asset.read_bytes();assert digest(blob)==SOURCES[uid];assets.append(asset);t=decode_original_world_triangles(blob);v=next(r for r in probe_runtime['rows']if r['uid']==uid);pos=np.asarray(v['position'],float).reshape(-1,3);idx=np.asarray(v['index'],np.uint32).reshape(-1,3);world=pos[idx];ground=np.asarray(v['drawnGroundGeometry'],float).reshape(-1,3,3)
  if uid==OWNED:
   for field in ['position','index','drawnGroundGeometry']:assert v[field]==rt[field],'Owned current numerical input differs from frozen full-facet input'
   assert digest((ROOT/row['candidate']['path']).read_bytes())==SOURCES[uid] and pre['sourceProviderRootAndStreams']==source_stream_binding(blob)
  else:assert asset.read_bytes()==nativeasset.read_bytes()
  with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,source['native']['cacheKey'])).fetchone()==(source['native']['resultSha'],)
  fr=next(r for r in finite['rows']if r['uid']==uid);assert fr['completeOriginalWorldSHA256']==digest(t.tobytes()) and fr['completeActualRenderedWorldSHA256']==digest(world.tobytes()) and fr['completeGroundSHA256']==digest(ground.tobytes()) and len(fr['allFaces'])==len(t)
  if uid==OWNED:
   assert len(t)==11593 and not fr['unprovedOriginalFaces']and not fr['unprovedActualRenderedFaces']
   for i,c in enumerate(fr['allFaces']):assert c['sourceFace']==i and c['completeOriginalBoundProved']is True and c['completeActualRenderedBoundProved']is True and c['priorCoarseBoundProofVerbatim']['completeOriginal']['sourceFaceSHA256']==digest(t[i].tobytes()) and c['priorCoarseBoundProofVerbatim']['actualRendered']['sourceFaceSHA256']==digest(world[i].tobytes())
  originalpos=np.empty_like(pos);assigned={}
  for ids,face in zip(idx,t):
   for j,point in zip(ids,face):
    j=int(j)
    if j in assigned:assert np.array_equal(assigned[j],point)
    else:assigned[j]=point;originalpos[j]=point
  assert set(assigned)==set(range(len(pos))) and np.array_equal(originalpos[idx],t)
  actors.append(dict(uid=uid,sourceSHA256=SOURCES[uid],originalStreamBindingSHA256=canonical(source_stream_binding(blob)),globalFaceRange=[cursor,cursor+len(t)],completeOriginalFaceCount=len(t),originalWorldTrianglesSHA256=digest(t.tobytes())));indexed.append(dict(uid=uid,sourceSHA256=SOURCES[uid],position=originalpos.reshape(-1).tolist(),index=idx.reshape(-1).tolist()));pieces.append(t);actualpieces.append(world);groundpieces.append(ground);cursor+=len(t)
 tri=np.concatenate(pieces);ground=np.unique(np.concatenate(groundpieces).reshape(-1,9),axis=0).reshape(-1,3,3);assert actors==g['actors']
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=ref(HERE/'local'/PROBE.name/'runtime-geometry.json.gz')['sha256'],supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(indexed));assert binding==g['binding']
 graph=json.loads(json.dumps(structural(tri,actors,g['components'],g['contactWitnesses'],indexed,ground,expected_binding=binding,current_binding=binding)))
 for k,v in graph.items():assert g[k]==v,'Full original restricted graph changed:'+k
 assert graph['supportInterfaceAccepted']is False and g['newOwnedOriginalBAllComponentsRooted']is True and len(g['retainedCurrentNativeUnrootedComponents'])==27
 roots=module('hkdi_actual_four_roots','xl-terrain-recovery-20261010-hkdi-current-native-literal-ground-roots-v3.py').recheck();assert roots==read(ROOTS/'diagnostic.json.gz')
 cap=json.loads(json.dumps(module('hkdi_complete_carrier_inventory','xl-terrain-recovery-20261010-hkdi-block-b-current-exposed-native-cap-paths-v2.py').recheck()));assert cap==read(CAPS/'diagnostic.json.gz')
 rb=dict(qualifiedCapProofSHA256=canonical(cap),completeOriginalComponentsSHA256=canonical(g['components']),actualFourRootProofSHA256=canonical(roots));owned=owned_support(cap,g['components'],roots,expected_binding=rb,current_binding=rb)
 assert ref(manifest)==start
 refs=[ref(p)for p in [Path(__file__),runtimepath,manifest,nativeasset,cat,HERE/'hkdi_owned_block_b_current_native_cap_support_20261010.py',HERE/'test_hkdi_owned_block_b_current_native_cap_support_20261010.py',HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_original_georef_cell_identity_20261009.py',*assets]]+catalogues
 for folder in [PHYS,PROBE,GRAPH,FINITE,CAPS,ROOTS]:refs.extend(ref(p)for p in sorted(folder.iterdir())if p.is_file())
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path'])
 return dict(contract='hkdi-owned-block-b-current-qualified-native-cap-support-v2',uids=[OWNED],currentManifest=start,sourceSHA256s={OWNED:SOURCES[OWNED]},mandatoryInstalledNativeSupport=dict(uid=NATIVE,sourceSHA256=SOURCES[NATIVE],buildingCSUID=entry['buildingCSUID'],asset=ref(nativeasset),catalogue=ref(cat)),completeOriginalFaces=11593,completeOriginalComponents=345,completeCurrentNeighbourForms=2,currentOwnedIdentity=ident,currentWholeFoundation=ff,ownedSourceAndLiteralWholeFiniteClearanceProved=True,allCurrentNativeBeforeAfterChecksPreserved=native,completeStrictOriginalCollectionGraph=graph,qualifiedOwnedNativeSupport=owned,independentActualFourRoots=roots,fullQualifiedCarrierInventory=cap,nativeReacceptance=False,rawPhysicalReasonsPreserved=raw,replacedDiagnosticReasonsOnly=raw,sourceGeometryChanges=0,terrainProposalGeometryChanged=False,terrainProposal=[],visualOrWallRoleCredit=False,currentTypedPhysicalAccepted=True,reasons=[],publication=False,newlyInstalled=0,installationApproved=False,evidenceRefs=refs)

def main():
 assert not DOC.exists();r=recheck();save(DOC/'typed-role.json.gz',r);m=module('hkdi_current_owned_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');m.freeze(BATCH,'current-owned-block-b-qualified-existing-native-source-literal-cap-support-v2',[ROOT/x['path']for x in r['evidenceRefs']],dict(uids=[OWNED],completeOriginalFaces=11593,completeOriginalComponents=345,currentTypedPhysicalAccepted=True,nativeReacceptance=False,reasons=[],typedRole=ref(DOC/'typed-role.json.gz'),publication=False,newlyInstalled=0));print(dict(ownedBCurrentAccepted=True,faces=11593,parts=345,nativeReacceptance=False),flush=True)
if __name__=='__main__':main()
