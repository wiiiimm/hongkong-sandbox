"""Explicit authenticated two-sheet terrain replacement candidate, never apply.

The current Parkview9 terrain is preserved beneath its complete unchanged
original/literal/F32 building bounds, which are disjoint from Block11. Elsewhere
the proposal restores original government TIN. All affected native/basic actors
remain mandatory in the subsequent full current physical/finite checks.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-parkview-authentic-current-retained-terrain-proposal-v3';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v2-20261011'
PRIOR=BASE/'xl-terrain-recovery-20261011-parkview-block11-current-inputs-v1'
AUTHENTIC=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3'
PARENT_URL='city/data/government-native-255439-0.json'
UID='landsd/255647:0';CARRIER='landsd/254491:0';RETAINED='landsd/255439:0'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest)
 selected=read(PROBE/'selection.json.gz');assert selected['manifestSHA256']==start['sha256'];entries={};catrefs=[]
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catrefs.append(ref(p))
  for e in read(p)['models']:assert e['uid']not in entries;entries[e['uid']]=(p,e)
 assert UID not in entries and CARRIER in entries and RETAINED in entries
 rootparent=ROOT/'3d-viewer/city/data/terrain.json';parentpath=ROOT/'3d-viewer'/PARENT_URL;parent=read(rootparent);oldpatch=read(parentpath)
 assert PARENT_URL in {p['url']for p in current['terrainPatches']}and oldpatch['meta']['targetUids']==[RETAINED,UID]
 assert oldpatch.get('nativeMesh')and not oldpatch.get('patches')
 second=module('parkview_authentic_resolution','xl-second-pass.py');patches=module('parkview_authentic_retention','native_patch_resolution.py');context=module('parkview_authentic_source','pending-context.py')
 rawrows=selected['rows'];world=[];sourcefiles=[];worldrefs=[];ownedtri=None
 for r in rawrows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];b=packed_world_bounds(raw);world.append(b['originalWholeSourceBounds']);worldrefs.append(ref(p))
  if r['uid']==UID:ownedtri=decode_original_world_triangles(raw)
 assert ownedtri.shape==(10679,3,3)
 rects=[second.resolution.rectangle_for(b,parent)for b in world];cells=[min(r[0]for r in rects),min(r[1]for r in rects),max(r[2]for r in rects),max(r[3]for r in rects)]
 oldcells=oldpatch['coarseCells'];cells=[min(cells[0],oldcells[0]),min(cells[1],oldcells[1]),max(cells[2],oldcells[2]),max(cells[3],oldcells[3])];bounds=second.resolution.extent(cells,parent);assert cells==[548,494,554,499]
 routing=[]
 for r in current['terrainPatches']:
  p=ROOT/'3d-viewer'/r['url'];obj=read(p);bb=patches._patch_bounds(obj);routing.append(dict(entry=r,asset=ref(p),completeAssetBounds=bb))
  if r['url']!=PARENT_URL:assert box(*bb).intersection(box(*bounds)).area==0,'Unaccounted existing terrain overlap: '+r['url']
 # Capture actual current retained/native carrier sources with the independently
 # reviewed complete production module closure before and after the loader.
 nativeuids=[CARRIER,RETAINED,'landsd/256112:0','landsd/256114:0'];assert set(nativeuids)<=set(entries)
 save(DOC/'current-native-bounds-input.json',dict(uids=nativeuids,manifest=start))
 subprocess.run(['node',str(HERE/'xl-terrain-recovery-20261010-current-original-literal-actor-bounds-readonly-v4.mjs'),'--input',str((DOC/'current-native-bounds-input.json').relative_to(ROOT)),'--out',str((DOC/'current-native-bounds.json').relative_to(ROOT))],cwd=ROOT,check=True)
 captured=read(DOC/'current-native-bounds.json');native=next(r for r in captured['rows']if r['uid']==RETAINED);cp,e=entries[RETAINED];asset=cp.parent/e['asset'];pos=packed_world_bounds(asset.read_bytes());assert pos['sourceSHA256']==e['sha256']==native['sourceSHA256']
 boxes=[pos['originalWholeSourceBounds'],native['completeLiteralWorldBounds'],native['completeFloat32CastWorldBounds'],native['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],native['completeExplicitBalancedFloat32ModelMatrixWorldBounds']];lo=np.min(np.asarray(boxes)[:,0],axis=0);hi=np.max(np.asarray(boxes)[:,1],axis=0);protected=box(lo[0],lo[2],hi[0],hi[2]);projection=shapely.union_all(shapely.polygons(ownedtri[:,:,[0,2]]));assert protected.intersection(projection).is_empty,'Complete retained original/literal/F32 region overlaps the original owned projection'
 allterrain=[];used=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receipt=read(folder/'original/download.json');assert receipt['directorySHA256']==read(folder/'directory/result.json')['directorySHA256'];files=[];paths=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];files.append(ref(p));sourcefiles.append(ref(p))
    if p.suffix=='.gltf':paths.append(p)
  assert paths;allterrain.extend(context.triangles(p)for p in sorted(paths));used.append(dict(sheet=sheet,revision=receipt['revisionDate'],sourceETag=receipt['sourceETag'],directorySHA256=receipt['directorySHA256'],sourceFiles=files))
 whole=np.concatenate(allterrain);auth=next(r for r in read(AUTHENTIC/'diagnostic.json.gz')['rows']if r['uid']==CARRIER);assert len(whole)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(whole.tobytes())==auth['authenticWholeSourceTerrainSHA256']
 keep=(whole[:,:,0].max(axis=1)>=bounds[0])&(whole[:,:,0].min(axis=1)<=bounds[2])&(whole[:,:,2].max(axis=1)>=bounds[1])&(whole[:,:,2].min(axis=1)<=bounds[3]);terrain=whole[keep];assert terrain[:,:,1].min()>=1.2
 core=[min(b[0][0]for b in world)-1,min(b[0][2]for b in world)-1,max(b[1][0]for b in world)+1,max(b[1][2]for b in world)+1]
 validator=second.resolution.validate_patch;deferred=[]
 # Construction defers ONLY the same final validator until the immutable
 # original-overlap audit and retained-parent faces exist; it never accepts.
 second.resolution.validate_patch=lambda *args:deferred.append(args)
 try:patch=second.resolution.make_patch(dict(uids=[UID],cells=cells),parent,terrain,used,native_core=core,terrain_triangle_budget=100000)
 finally:second.resolution.validate_patch=validator
 assert len(deferred)==1
 # The preserved installed actor and the uninstalled target retain their exact
 # current terrain metadata membership; this does not reapprove either actor.
 patch['meta']['targetUids']=sorted({UID,RETAINED})
 for r in captured['rows']:
  cp0,e0=entries[r['uid']];original=packed_world_bounds((cp0.parent/e0['asset']).read_bytes())['originalWholeSourceBounds']
  for bb0 in [original,r['completeLiteralWorldBounds'],r['completeFloat32CastWorldBounds'],r['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],r['completeExplicitBalancedFloat32ModelMatrixWorldBounds']]:
   assert bounds[0]<=bb0[0][0]<=bb0[1][0]<=bounds[2]and bounds[1]<=bb0[0][2]<=bb0[1][2]<=bounds[3],'Complete actual native arithmetic bounds outside proposed region'
 from rendered_patch_sampler import RenderedPatchSampler
 sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True);old_sampler=RenderedPatchSampler(oldpatch,sampler,second.resolution.terrain.fine.DemSampler(oldpatch,rendered=True))
 retention=patches.preserve_parent_under_projection(patch,bounds,protected,old_sampler,edge_sampler=sampler)
 retention.update(supersededURL=PARENT_URL,supersededSHA256=ref(parentpath)['sha256'],retainedUID=RETAINED,protectedCompleteOriginalLiteralF32Bounds=[lo.tolist(),hi.tolist()],allOriginalPositionProof=pos,currentLiteralFloat32Proof=native,exactOwnedProjectionDisjoint=True)
 fill=patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler);snap=patches.snap_boundary_to_parent(patch,bounds,sampler)
 path=LOCAL/(patch['id']+'.json');save(path,patch)
 if patches.projected_context(patch,bounds)[3]>1e-8:
  patches.approve_original_overlap(patch,path,DOC/'native-overlap.json',sourcefiles);patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
 validator(patch,parent);save(path,patch);assert reservations.heartbeat(lease)['ok']and ref(manifest)==start
 candidate=dict(path=str(path.relative_to(ROOT)),sha256=ref(path)['sha256'],uids=[UID],bounds=bounds,cells=cells,triangles=len(patch['nativeMesh']['index'])//3,replaces=dict(url=PARENT_URL,sha256=ref(parentpath)['sha256'],retainedUids=[RETAINED]))
 save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'terrain.json',dict(patch=candidate,sourceFiles=sourcefiles,currentRetainedParent=ref(parentpath),fullAuthenticatedSourceTerrainSHA256=digest(whole.tobytes()),selectedWholeOriginalTINFacetIds=np.flatnonzero(keep).tolist(),retention=retention,parentHoleFill=fill,finalBoundarySnap=snap,sourceBuildingGeometryChanges=0,terrainProposalGeometryChanged=True,fullCurrentPhysicalRequired=True,actualFloat32ModelMatrixRepresentationsIncluded=True,explicitArithmeticNotUniversalGPUCameraGuarantee=True,retainedTargetUids=patch['meta']['targetUids'],publication=False))
 refs=[ref(p)for p in [Path(__file__),manifest,rootparent,parentpath,asset,PROBE/'selection.json.gz',PROBE/'result.json',PRIOR/'check-selection.json.gz',PRIOR/'context.json.gz',AUTHENTIC/'diagnostic.json.gz',AUTHENTIC/'result.json',DOC/'current-native-bounds-input.json',DOC/'current-native-bounds.json',DOC/'terrain-candidates.json',DOC/'terrain.json',path,HERE/'xl-second-pass.py',HERE/'resolve-pass.py',HERE/'native_patch_resolution.py',HERE/'rendered_patch_sampler.py',HERE/'pending-context.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-terrain-recovery-20261010-current-original-literal-actor-bounds-readonly-v4.mjs',HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'test_actual_float32_model_matrix_bounds_20261011.mjs']]+sourcefiles+worldrefs+catrefs
 refs.extend(dict(path=p,sha256=h)for p,h in captured['inputHashes'].items());refs=list({r['path']:r for r in refs}.values())
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[UID,CARRIER,RETAINED],currentManifest=start,terrainCandidate=candidate,fullTerrainRouting=routing,sourceGeometryChanges=0,terrainProposalGeometryChanged=True,terrainValidationPassed=True,fullCurrentPhysicalRequired=True,nativeReacceptance=False,fullAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
 freeze=module('parkview_authentic_proposal_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'explicit-authentic-two-TIN-current-parent-retained-original-literal-explicit-matrix-F32-disjoint-terrain-candidate-v2',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceGeometryChanges=0,terrainProposalGeometryChanged=True,fullCurrentPhysicalRequired=True,nativeReacceptance=False,newlyInstalled=0));print(dict(terrainCandidateValidated=True,triangles=candidate['triangles'],fullCurrentPhysicalRequired=True),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();keys=['building:'+u for u in [UID,CARRIER,RETAINED,'landsd/256112:0','landsd/256114:0']]+['terrain-surface:'+PARENT_URL]
 claim=reservations.claim('parkview-authentic-retained-terrain-proposal-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
