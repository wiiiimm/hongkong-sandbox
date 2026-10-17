"""Build a private source-terrain candidate for exact reviewed Long Ping; never publish."""
import sys,json,uuid,subprocess
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import box
from rendered_patch_sampler import RenderedPatchSampler
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PHYSICAL=BASE/'government-xl-long-ping-current-physical-v1-20261017';REVIEW=BASE/'government-xl-long-ping-reviewed-identity-v1-20261017';TIN=BASE/'government-xl-long-ping-source-terrain-v1-20261017';BATCH='government-xl-long-ping-private-terrain-v2-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/107382:0';SHA='f462a97834afe39e5f66932c562eaa1daa4fa9f6958d5879663d1878b4251add'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for p in [PHYSICAL,REVIEW,TIN]:
   r=read(p/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p/'result.json')
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 decision=read(REVIEW/'identity-review.json');assert decision['uid']==UID and decision['sourceSHA256']==SHA and decision['identityReviewApproved']and not decision['publicationApproved']
 selection=read(PHYSICAL/'selection.json.gz');row=selection['rows'][0];manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256'];m=read(manifest)
 for url in m['officialModelCatalogues']:assert not any(e['uid']==UID for e in read(ROOT/'3d-viewer'/url)['models'])
 g=read(HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz')['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert row['sourceSHA256']==SHA==digest((ROOT/row['candidate']['path']).read_bytes())
 source_receipt=read(TIN/'result.json');downloads=[ROOT/q['path']for q in source_receipt['evidenceRefs']if q['path'].endswith('/original/download.json')];assert len(downloads)==1;folder=downloads[0].parent.parent
 verifier=module('long_ping_private_verified_tin',HERE/'xl-cell-indexed-terrain-continuation.py');verified=verifier.verified_terrain(folder);assert verified;receipt,files=verified
 second=module('long_ping_private_second',HERE/'xl-second-pass.py');second.LOCAL=LOCAL;patches=module('long_ping_private_patches',HERE/'native_patch_resolution.py')
 parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path);world=[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()];cells=second.resolution.rectangle_for(world,parent)
 retained_url='city/data/government-native-265310-0.json';retained_path=ROOT/'3d-viewer'/retained_url;retained=read(retained_path);retained_sha=digest(retained_path.read_bytes());refs.append(retained_path)
 assert retained.get('nativeMesh') and not retained.get('patches')
 old_cells=retained['coarseCells'];cells=[min(cells[0],old_cells[0]),min(cells[1],old_cells[1]),max(cells[2],old_cells[2]),max(cells[3],old_cells[3])];bounds=second.resolution.extent(cells,parent)
 retained_uids=retained['meta']['targetUids'];assert set(retained_uids)=={'landsd/265310:0','landsd/265311:0','landsd/265312:0','landsd/265313:0'}
 retained_bounds={}
 for url in m['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url
  for entry in read(cat)['models']:
   if entry['uid'] in retained_uids:
    asset=cat.parent/entry['asset'];assert asset.exists(),str(asset);raw=asset.read_bytes();assert digest(raw)==entry['sha256'];retained_bounds[entry['uid']]=packed_world_bounds(raw);refs.extend([cat,asset])
 assert set(retained_bounds)==set(retained_uids)
 for p in m['terrainPatches']:
  if p['url']==retained_url:continue
  other=read(ROOT/'3d-viewer'/p['url']);geo=other['meta']['georef'];ob=[geo['bE']-834500,816500-geo['bN'],geo['bE']-834500+(other['w']-1)*geo['aE'],816500-geo['bN']-(other['h']-1)*geo['aN']];assert box(*bounds).intersection(box(*ob)).area<=1e-8,('Requires retained terrain handling',p['url'])
 sources=[];parts=[]
 for f in files:
  p=folder/'terrain'/f['name'];assert digest(p.read_bytes())==f['sha256'];sources.append(dict(path=str(p.relative_to(ROOT)),sha256=f['sha256']));refs.append(p)
  if p.suffix=='.gltf':parts.append(second.terrain_triangles(p))
 native=np.concatenate(parts);native=native[(native[:,:,0].max(axis=1)>=bounds[0])&(native[:,:,0].min(axis=1)<=bounds[2])&(native[:,:,2].max(axis=1)>=bounds[1])&(native[:,:,2].min(axis=1)<=bounds[3])];assert len(native)
 projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));low=native[:,:,1].min(axis=1)<1.2;lowarea=float(shapely.union_all(shapely.polygons(native[low][:,:,[0,2]])).intersection(projection).area)if low.any()else 0
 if low.any()and lowarea<1e-6:native=native[~low]
 used=[dict(sheet=folder.name,revision=receipt['revisionDate'],sourceETag=receipt['sourceETag'],directorySHA256=receipt['directorySHA256'],sourceFiles=sources)];core=[world[0][0]-1,world[0][2]-1,world[1][0]+1,world[1][2]+1];validator=second.resolution.validate_patch
 # Existing construction sequence validates after source seam and boundary reconciliation.
 second.resolution.validate_patch=lambda *_:None
 try:patch=second.resolution.make_patch(dict(uids=[UID],cells=cells),parent,native,used,native_core=core,terrain_triangle_budget=100000,allow_native_below_clamp=bool(low.any()and lowarea>=1e-6),parent_url='city/data/terrain.json',parent_sha256=digest(parent_path.read_bytes()))
 finally:second.resolution.validate_patch=validator
 patch_path=LOCAL/(patch['id']+'.json');sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
 old_bounds=patches._patch_bounds(retained);protected=box(*old_bounds).difference(projection.buffer(.1,join_style='mitre'));assert protected.intersection(projection).area<1e-8
 for uid,proof in retained_bounds.items():
  lo,hi=proof['originalWholeSourceBounds'];assert protected.covers(box(lo[0],lo[2],hi[0],hi[2])),('Retained original intersects new source',uid)
 old_sampler=RenderedPatchSampler(retained,sampler,second.resolution.terrain.fine.DemSampler(retained,rendered=True))
 preservation=patches.preserve_parent_under_projection(patch,bounds,protected,old_sampler,edge_sampler=sampler)
 old_faces=patches._faces(retained);vertical=np.abs(np.cross(old_faces[:,1]-old_faces[:,0],old_faces[:,2]-old_faces[:,0])[:,1])<=1e-10
 preservation.update(replaces=retained_url,replacesSHA256=retained_sha,retainedSourceBounds=retained_bounds,sourceProjectionIntersectionM2=float(protected.intersection(projection).area),oldDrawnVerticalFaces=int(vertical.sum()),allRenderedRepresentationsVerified=False,qualification='Private candidate only: clipped old surface planes retained; actual rendered/Float32/vertical-face and full-neighbour proof remains required.')
 save(DOC/'preservation.json',preservation)
 for old_source in retained['meta']['source']['nativeSources']:
  for f in old_source['sourceFiles']:
   assert digest((ROOT/f['path']).read_bytes())==f['sha256'];refs.append(ROOT/f['path'])
   if f not in sources:sources.append(f)
 patch['meta']['targetUids']=sorted(set([UID]+retained_uids))
 gap=patches.projected_context(patch,bounds)[2].intersection(projection);save(LOCAL/'unfilled-patch.json',patch)
 fill=patches.fill_narrow_source_seam(patch,bounds,projection,sampler,tolerance=.02)if gap.area>1e-6 else patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler)
 remaining=float(patches.projected_context(patch,bounds)[2].area);maximum=max(.25,(bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3);assert remaining<=maximum
 if remaining>1e-8:patch['nativeMesh']['source']['numericalCoverageGap']=dict(policy='parent-grid-fallback',measuredAreaM2=remaining,maximumAreaM2=maximum,maximumFraction=1e-3)
 patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler);save(patch_path,patch)
 if patches.projected_context(patch,bounds)[3]>1e-8:
  patches.approve_original_overlap(patch,patch_path,DOC/'native-overlap.json',sources);patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
 validator(patch,parent);save(patch_path,patch);candidate=dict(path=str(patch_path.relative_to(ROOT)),sha256=digest(patch_path.read_bytes()),uids=[UID],bounds=bounds,triangles=len(patch['nativeMesh']['index'])//3)
 candidate['replaces']=dict(url=retained_url,sha256=retained_sha,retainedUids=retained_uids)
 save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'construction.json',dict(candidate=candidate,coarseCells=cells,core=core,parentHoleFill=fill,sourceFiles=sources,validatorPassed=True,neighboursChecked=False,publicationApproved=False))
 refs.extend([parent_path,manifest,REVIEW/'identity-review.json',PHYSICAL/'selection.json.gz',HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz',downloads[0],folder/'directory/result.json',patch_path,HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
 out=module('long_ping_private_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'long-ping-reviewed-source-private-native-terrain-construction-v2',list(dict.fromkeys(refs)),dict(uids=[UID],candidate=candidate,validatorPassed=True,fullAcceptance=False,nextStep='Check actual production contact/foundation and all current actors touching the complete changed coarse-cell extent. No neighbour or publication credit from construction.'));print(dict(jobId=out['jobId'],candidate=candidate),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID,'terrain-patch:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
