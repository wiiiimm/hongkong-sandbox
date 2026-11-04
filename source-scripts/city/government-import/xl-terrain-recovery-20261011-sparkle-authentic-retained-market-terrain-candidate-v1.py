"""UNEXECUTED, candidate-only mixed authentic/retained literal terrain.

No viewer write, native reapproval, source edit or physical acceptance. Preserve
whole current literal terrain facets beneath all four market worlds; retain the
complete aligned old scalar grid. Construction overlays are not finite proofs.
ROOT must review this executable, helper and tests before either CLI is run.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import importlib.util,json,math,subprocess,sys,uuid,traceback
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from sparkle_retained_literal_terrain_construction_20261011 import (dyadic_facet_boxes,
 strictly_separate_boxes_from_owned,merge_literal_ground_snapshots,
 whole_ground_faces_touching_boxes,copy_complete_aligned_old_grid,clip_new_planes_outside)
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-sparkle-authentic-retained-market-terrain-candidate-v1'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
OWNED=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-two-current-render-attribute-capture-v1'
RETAINED=BASE/'xl-terrain-recovery-20261011-sparkle-retained-market-two-current-render-ground-capture-v2'
OVERLAP=BASE/'xl-terrain-recovery-20261011-sparkle-retained-market-overlap-receipt-recovery-v3'
PHYSICAL=BASE/'government-xl-terrain-recovery-sparkle-tower-podium-pair-authentic-current-v1-20261011'
ERRATUM=BASE/'government-xl-sparkle-pair-authentic-current-v1-attempted-terrain-erratum-20261011/erratum.json'
UIDS=['landsd/242198:0','landsd/228000:0','landsd/113733:0','landsd/138091:0']
COUNTS=[12875,6806,15641,25224]
FORM_UIDS=UIDS+['landsd/28244:0','landsd/107780:0','landsd/271008:0','landsd/271555:0','landsd/20045:0']
MANIFEST='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
OLD_URL='city/data/government-native-138091-0.json'
OLD_SHA='adba04439687b055cd499f334d57b6c2edf92e769180f87a4f09ec83a97421d0'
HELPER=HERE/'sparkle_retained_literal_terrain_construction_20261011.py'
TEST=HERE/'test_sparkle_retained_literal_terrain_construction_20261011.py'
MODES=['originalSource','actualLiteral','explicitLeftAssociatedFloat32','explicitBalancedFloat32']
CODE=['exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py',
 'native_patch_resolution.py','xl-second-pass.py','resolve-pass.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py']
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(r):
 p=ROOT/r['path'];assert p.is_file()and ref(p)==r;return p
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def counter(a):return Counter(f.astype(np.float32).tobytes()for f in np.asarray(a).reshape(-1,3,3))
def set_faces(p,a):
 p['nativeMesh']['position']=np.asarray(a,float).reshape(-1).tolist();p['nativeMesh']['index']=list(range(len(a)*3))
def validation():
 """Only run after ROOT approves these exact unit/adverse tests."""
 assert not DOC.exists()and not(LOCAL/'helper-validation.json').exists()
 pins=[ref(HELPER),ref(TEST)];LOCAL.mkdir(parents=True,exist_ok=True)
 log=LOCAL/'actual-helper-adverse-tests.log'
 with log.open('wb')as f:r=subprocess.run([sys.executable,str(TEST)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 text=log.read_text();assert r.returncode==0 and 'Ran 18 tests' in text and '\nOK\n'in text
 assert pins==[ref(HELPER),ref(TEST)]
 save(LOCAL/'helper-validation.json',dict(executedCode=pins,actualLog=ref(log),exitCode=r.returncode,passed=18))
def completed(folder,job,refs):
 r=read(folder/'result.json');assert r['jobId']==job
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',r)
 for pin in r['evidenceRefs']:verify(pin)
 refs.extend([ref(folder/'result.json'),*r['evidenceRefs']]);return r
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 v=read(LOCAL/'helper-validation.json');assert v['executedCode']==[ref(HELPER),ref(TEST)]and v['exitCode']==0 and v['passed']==18
 log=verify(v['actualLog']);assert 'Ran 18 tests'in log.read_text()and '\nOK\n'in log.read_text()
 refs=[ref(Path(__file__)),ref(HELPER),ref(TEST),ref(LOCAL/'helper-validation.json'),ref(log),*[ref(HERE/n)for n in CODE],ref(ERRATUM)]
 completed(OWNED,'80b48d4b97a689b19e34ace263ab907be1f5ebaa7b7a7be57dda9892d656487c',refs)
 completed(RETAINED,'4832a8e05527b49eca61ff04478d7ce4d9a3a8dcc315fdf1756171293ab144b9',refs)
 completed(OVERLAP,'50f8527bdbc87fbef0c65e34679035f1f418b7a330229aa14cfbe785c682b1d3',refs)
 completed(PHYSICAL,'c834befb9fc03942b42683e9aeaa8d233663609ca12e1cc0a22b9524d0fcceb7',refs)
 assert read(ERRATUM)['terrainProposalCreated']is False
 oi=read(OWNED/'literal-source-inputs.json.gz');ri=read(RETAINED/'native-render-inputs.json.gz')
 oa=read(OWNED/'actual-render-attributes.json.gz');ra=read(RETAINED/'native-render-ground.json.gz')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST and oi['currentManifest']==ri['currentManifest']==start
 refs.append(start);current=read(manifest);oldpath=ROOT/'3d-viewer'/OLD_URL;assert ref(oldpath)['sha256']==OLD_SHA
 old=read(oldpath);parentpath=ROOT/'3d-viewer'/old['meta']['parentTerrain'];parent=read(parentpath)
 assert old['meta']['targetUids']==UIDS[2:]and old['meta']['parentSha256']==ref(parentpath)['sha256']
 refs.extend([ref(oldpath),ref(parentpath)])
 assert sum(p['url']==OLD_URL for p in current['terrainPatches'])==1
 for p in current['terrainPatches']:refs.append(ref(ROOT/'3d-viewer'/p['url']))
 for p in ri['currentCatalogueRefs']+ri['currentTileRefs']:verify(p);refs.append(p)
 for key,sha in oa['inputHashes'].items():assert ref(ROOT/key)['sha256']==sha;refs.append(ref(ROOT/key))
 for key,sha in ra['inputHashes'].items():assert ref(ROOT/key)['sha256']==sha;refs.append(ref(ROOT/key))
 worlds={};whole_positions=[];bindings=[]
 for inp,actual,uid,count in zip(oi['rows']+ri['rows'],oa['rows']+ra['rows'],UIDS,COUNTS):
  assert inp['uid']==actual['uid']==uid;asset=ROOT/inp['path']if uid in UIDS[:2]else verify(inp['sourceAsset'])
  proof=packed_world_bounds(asset.read_bytes());assert proof['sourceSHA256']==actual['sourceSHA256']and proof['completeOriginalTriangles']==count and proof['originalUnreferencedPositionVertices']==0
  refs.append(ref(asset));ids=np.asarray(actual['completeOriginalIndex'],int)
  assert len(ids)==3*count;original=decode_original_world_triangles(asset.read_bytes());assert original.shape==(count,3,3)
  rows=[original]
  for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
   positions=np.asarray(actual[key],float).reshape(-1,3);assert np.isfinite(positions).all()and ids.min()>=0 and ids.max()<len(positions)
   rows.append(positions[ids].reshape(-1,3,3));whole_positions.append((uid,positions))
  whole_positions.append((uid,original.reshape(-1,3)))
  worlds[uid]=rows
  for mode,world in zip(MODES,rows):bindings.append(dict(uid=uid,mode=mode,completeFacets=count,completeIndexedWorldSHA256=digest(world.tobytes())))
 numeric=read(OVERLAP/'receipt-recovery.json');assert numeric['completeWorldTupleReplayBindings']==[{**b,'sourceSHA256':a['sourceSHA256']}for a,uid in zip(oa['rows']+ra['rows'],UIDS)for b in bindings if b['uid']==uid]
 assert numeric['exactProjectedCandidatePairsByRow']==[0]*16 and numeric['actual3DContactCountsByRow']==[0]*16
 second=module('sparkle_retained_second','xl-second-pass.py');second.LOCAL=LOCAL
 patches=module('sparkle_retained_patches','native_patch_resolution.py')
 construction_modules=[second,second.resolution,second.context,second.context.shared,
  second.resolution.terrain,second.resolution.terrain.fine,second.resolution.terrain.fine.m,patches]
 for m in list(sys.modules.values())+construction_modules:
  file=getattr(m,'__file__',None)
  if file and Path(file).resolve().is_relative_to(ROOT)and Path(file).is_file():refs.append(ref(Path(file)))
 # Every code/input pin is verified before numerical candidate construction.
 for pin in refs:verify(pin)
 DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append(ref(DOC/'historical-current-manifest.json'))
 try:
  own=[w for uid in UIDS[:2]for w in worlds[uid]];ret=[w for uid in UIDS[2:]for w in worlds[uid]]
  inner=dyadic_facet_boxes(ret);outer=dyadic_facet_boxes(ret,collar_cells=1)
  separation={'inner':strictly_separate_boxes_from_owned(inner,own),'outer':strictly_separate_boxes_from_owned(outer,own)}
  for actual,uid in zip(ra['rows'],UIDS[2:]):
   boxes=dyadic_facet_boxes(worlds[uid],collar_cells=1);bb=actual['groundCaptureBounds']
   assert np.all(boxes[:,:2]>=bb[:2])and np.all(boxes[:,2:]<=bb[2:]),'Retained protection outside completed ground capture'
  captured=merge_literal_ground_snapshots([r['drawnGroundGeometry']for r in ra['rows']])
  old_faces=patches._faces(old);old_ids,retained_faces=whole_ground_faces_touching_boxes(old_faces,outer)
  captured_ids,captured_selected=whole_ground_faces_touching_boxes(captured,outer)
  assert counter(retained_faces)==counter(captured_selected),'Captured whole protected ground differs from complete old native mesh'
  # Complete old remaining triangles must be strictly absent from every inner box.
  omitted=np.delete(old_faces,old_ids,axis=0)
  lo=omitted[:,:,[0,2]].min(axis=1);hi=omitted[:,:,[0,2]].max(axis=1)
  for b in inner:assert not(np.all(lo<=b[2:],axis=1)&np.all(hi>=b[:2],axis=1)).any()
  rectangles=[old['coarseCells']]
  for uid,positions in whole_positions:
   if uid in UIDS[:2]:rectangles.append(second.resolution.rectangle_for([positions.min(axis=0).tolist(),positions.max(axis=0).tolist()],parent))
  # Whole copied facets may extend beyond the retained model; contain all of them.
  pg=parent['meta']['georef'];lo=retained_faces.min(axis=(0,1));hi=retained_faces.max(axis=(0,1))
  rectangles.append([math.floor((lo[0]+834500-pg['bE'])/pg['aE']),math.floor((lo[2]-816500+pg['bN'])/-pg['aN']),math.ceil((hi[0]+834500-pg['bE'])/pg['aE']),math.ceil((hi[2]-816500+pg['bN'])/-pg['aN'])])
  cells=[min(r[0]for r in rectangles),min(r[1]for r in rectangles),max(r[2]for r in rectangles),max(r[3]for r in rectangles)]
  bounds=second.resolution.extent(cells,parent)
  assert 0<=cells[0]<cells[2]<parent['w']and 0<=cells[1]<cells[3]<parent['h']
  for p in current['terrainPatches']:
   if p['url']==OLD_URL:continue
   other=patches._patch_bounds(read(ROOT/'3d-viewer'/p['url']))
   assert bounds[2]<=other[0]or other[2]<=bounds[0]or bounds[3]<=other[1]or other[3]<=bounds[1],('Additional current terrain overlap',p['url'])
  sources=[];native=[];files=[]
  for source in read(PHYSICAL/'source-recovery.json')['sheets']:
   folder=ROOT/source['cache'];proof=read(folder/'original/download.json')
   assert proof['directorySHA256']==source['directorySHA256']==read(folder/'directory/result.json')['directorySHA256']
   refs.extend([ref(folder/'original/download.json'),ref(folder/'directory/result.json')]);pins=[]
   for item in source['terrainFiles']:
    path=folder/'terrain'/item['name'];pin=ref(path);assert pin['sha256']==item['sha256']and path.stat().st_size==item['bytes'];pins.append(pin);refs.append(pin)
   native.extend(second.terrain_triangles(ROOT/p['path'])for p in pins if p['path'].endswith('.gltf'))
   sources.append(dict(sheet=source['sheet'],revision=proof['revisionDate'],sourceETag=proof['sourceETag'],directorySHA256=source['directorySHA256'],sourceFiles=pins));files.extend(pins)
  for source in old['meta']['source']['nativeSources']:
   for pin in source['sourceFiles']:verify(pin);refs.append(pin);files.append(pin)
  oldaudit=Path(old['nativeMesh']['sourceOverlap']['evidencePath']);assert ref(oldaudit)['sha256']==old['nativeMesh']['sourceOverlap']['evidenceSHA256'];refs.append(ref(oldaudit))
  native=np.concatenate(native);hits=(native[:,:,0].max(axis=1)>=bounds[0])&(native[:,:,0].min(axis=1)<=bounds[2])&(native[:,:,2].max(axis=1)>=bounds[1])&(native[:,:,2].min(axis=1)<=bounds[3]);native=native[hits];assert len(native)
  ownpositions=np.concatenate([p for uid,p in whole_positions if uid in UIDS[:2]])
  core=[float(ownpositions[:,0].min()-1),float(ownpositions[:,2].min()-1),float(ownpositions[:,0].max()+1),float(ownpositions[:,2].max()+1)]
  validator=second.resolution.validate_patch;second.resolution.validate_patch=lambda *_:None
  try:patch=second.resolution.make_patch(dict(uids=UIDS,cells=cells),parent,native,sources,native_core=core,parent_url=old['meta']['parentTerrain'],parent_sha256=ref(parentpath)['sha256'],allow_native_below_clamp=bool(np.any(native[:,:,1]<1.2)),terrain_triangle_budget=100000)
  finally:second.resolution.validate_patch=validator
  outer_region=shapely.union_all([shapely.box(*b)for b in outer])
  literal_region=shapely.union_all(shapely.polygons(retained_faces[:,:,[0,2]]));protected=shapely.union_all([outer_region,literal_region])
  fresh=clip_new_planes_outside(patches._faces(patch),protected);set_faces(patch,fresh)
  sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
  # Snap NEW triangles before appending old ones. Never mutate copied old XYZ.
  snap=patches.snap_boundary_to_parent(patch,bounds,sampler)
  fresh=patches._faces(patch)
  _,_,missing,_=patches.projected_context(patch,bounds)
  ownprojection=shapely.union_all(shapely.polygons(np.concatenate(own)[:,:,[0,2]]))
  # Never fill under owned source or protected market region. Keep true holes
  # for later complete finite diagnostics rather than tolerance/coverage credit.
  outside=missing.difference(shapely.union_all([ownprojection,protected]))
  additions=np.asarray(patches.grid_surface_faces(sampler,outside),float).reshape(-1,3,3)if not outside.is_empty else np.empty((0,3,3))
  new=np.concatenate([fresh,additions]);set_faces(patch,new);patches.snap_boundary_to_parent(patch,bounds,sampler);new=patches._faces(patch)
  # Literal packing cannot spill into any closed inner protection rectangle.
  nlo=new[:,:,[0,2]].min(axis=1);nhi=new[:,:,[0,2]].max(axis=1)
  for b in inner:assert not(np.all(nlo<=b[2:],axis=1)&np.all(nhi>=b[:2],axis=1)).any(),'Packed new terrain enters retained closed protection'
  set_faces(patch,np.concatenate([new,retained_faces]));patch,gridproof=copy_complete_aligned_old_grid(patch,old)
  assert np.array_equal(patches._faces(patch)[len(new):],retained_faces)
  patch['meta']['targetUids']=UIDS;patch['meta']['source']['retainedCurrentTerrain']=dict(originalPatch=ref(oldpath),wholeLiteralFaces=len(retained_faces),retainedSources=old['meta']['source']['nativeSources'])
  patch['nativeMesh']['source']['policy']='Explicit candidate: authentic 13A/13B plus bounded root-parent transition and WHOLE literal current market facets; no building geometry change or native reapproval.'
  patch['nativeMesh']['source']['finalBoundarySnap']=snap
  _,polys,missing,excess=patches.projected_context(patch,bounds);extent=shapely.box(*bounds);union=shapely.union_all(polys);gap=float(union.symmetric_difference(extent).area)
  maximum=max(.25,extent.area*1e-3);assert gap<=maximum
  # Preserve the exact old sampler fallback ENABLEMENT; record new measured
  # whole coverage honestly. Copied grid planes are not newly drawn mesh faces.
  assert old['nativeMesh']['source']['numericalCoverageGap']['policy']=='parent-grid-fallback'
  patch['nativeMesh']['source']['numericalCoverageGap']=dict(policy='parent-grid-fallback',measuredAreaM2=gap,maximumAreaM2=maximum,maximumFraction=1e-3)
  path=LOCAL/'sparkle-authentic-with-literal-retained-market.json';save(path,patch)
  if excess>0:patches.approve_original_overlap(patch,path,DOC/'native-overlap.json',files);patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
  validator(patch,parent);save(path,patch)
  assert np.array_equal(patches._faces(patch)[len(new):],retained_faces)
  save(DOC/'literal-retention-construction.json.gz',dict(uids=UIDS,currentManifest=start,allFourWorldBindings=bindings,innerDyadicFacetRectangles=inner.tolist(),outerDyadicFacetRectangles=outer.tolist(),strictOwnedSeparation=separation,completeOldNativeFaces=len(old_faces),wholeOldProtectedFaceIDs=old_ids.tolist(),wholeOldProtectedLiteralXYZSHA256=digest(retained_faces.tobytes()),completeCapturedProtectedFaceIDs=captured_ids.tolist(),oldOmittedFacetsClosedBoxSeparated=True,newPackedFacetsClosedBoxSeparated=True,highestNativeSurfaceFunctionIdenticalOnProtectedRectangles=True,oldScalarFallbackGrid=gridproof,oldFallbackEnablementPreserved=True,arbitraryIEEEQueryBitIdentityNotClaimed=True,currentTerrainChangedOnlyInCandidate=True,sourceGeometryChanges=0,currentAcceptance=False,nativeReacceptance=False,completeCoverageAndSeamAcceptanceStillRequired=True))
  save(DOC/'terrain-candidates.json',dict(batch=BATCH,patches=[dict(path=ref(path)['path'],sha256=ref(path)['sha256'],uids=UIDS[:2],bounds=bounds,triangles=len(patch['nativeMesh']['index'])//3,replaces=dict(url=OLD_URL,sha256=OLD_SHA,retainedUids=UIDS[2:]))]))
  summary=dict(uids=UIDS,terrainProposalCreated=True,candidateFilesProduced=True,candidateValidatorPassed=True,terrainProposalGeometryChanged=True,mixedAuthenticatedAndLiteralCurrentTerrain=True,sourceGeometryChanges=0,deployedTerrainChanges=0,currentAcceptance=False,nativeReacceptance=False,allOwnedForeignNativePhysicalGatesStillRequired=True,completeCurrent6648ChangedDomainCheckStillRequired=True,completeCoverageAndSeamAcceptanceStillRequired=True,newlyInstalled=0)
 except AssertionError as e:
  save(DOC/'construction-guard-failure.json',dict(error=str(e),traceback=traceback.format_exc(),candidateAcceptance=False,noGuardWaiver=True))
  created=(LOCAL/'sparkle-authentic-with-literal-retained-market.json').is_file()
  summary=dict(uids=UIDS,terrainProposalCreated=created,candidateFilesProduced=created,candidateValidatorPassed=False,attemptedCandidateConstruction=True,terrainProposalGeometryChanged=created,sourceGeometryChanges=0,deployedTerrainChanges=0,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0)
 for pin in refs:verify(pin)
 assert ref(manifest)==start and reservations.owns(lease)
 save(DOC/'construction-summary.json',summary)
 freeze=module('sparkle_retained_candidate_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py')
 paths=[verify(p)for p in {p['path']:p for p in refs}.values()]+[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json']
 freeze.freeze(BATCH,'sparkle-authentic-retained-literal-market-candidate-construction-v1',paths,summary)
def main():
 if '--validate-helper'in sys.argv:return validation()
 if '--owned'in sys.argv:return owned()
 assert '--generate-candidate-only'in sys.argv and not DOC.exists()and not LEASE.exists()
 claim=reservations.claim('sparkle-retained-literal-candidate-'+str(uuid.uuid4()),['building:'+u for u in FORM_UIDS]+['terrain-patch:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok']
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
