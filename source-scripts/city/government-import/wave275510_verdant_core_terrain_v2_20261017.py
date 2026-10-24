"""Construct and measure a full original-TIN candidate. Never publish or waive failures."""
import json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave275510-verdant-core-terrain-candidate-v2-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
OLD=None;PARENT='city/data/terrain.json'
def plan():
 rows=read(BASE/'government-xl-wave275510-pair-capture-v1-20261017/selection.json.gz')['rows'];second=module('wave_candidate_scope',HERE/'xl-second-pass.py');parent=read(ROOT/'3d-viewer'/PARENT);rects=[];bounds=[]
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];b=packed_world_bounds(raw)['originalWholeSourceBounds'];bounds.append(b);expanded=[[b[0][0]-.1,b[0][1],b[0][2]-.1],[b[1][0]+.1,b[1][1],b[1][2]+.1]];rects.append(second.resolution.rectangle_for(expanded,parent))
 cells=[min(r[0]for r in rects),min(r[1]for r in rects),max(r[2]for r in rects),max(r[3]for r in rects)];domain=second.resolution.extent(cells,parent)
 return rows,bounds,cells,domain

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);rows,world,cells,domain=plan();refs=[Path(__file__)];pins={}
 for name in ['government-xl-wave275510-assembly-original-tin-v1-20261017','government-xl-wave275510-current-native-scope-v1-20261017','government-xl-wave-verdant-surface-hits-v1-20261017']:
  d=BASE/name;r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);manifestsha=digest(manifestpath.read_bytes());parentpath=ROOT/'3d-viewer'/PARENT;parent=read(parentpath)
 prior=BASE/'government-xl-wave275510-current-native-scope-v1-20261017';bounds=read(prior/'complete-bounds.json.gz')['rows'];current={e['uid']:e for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']};assert set(current)=={r['uid']for r in bounds}
 touching=[]
 for r in bounds:
  assert current[r['uid']]['sha256']==r['sourceSHA256']
  if not closed_disjoint(r['completeFourWorldBounds'],domain):touching.append(r['uid'])
 final=module('wave275510_candidate_final',HERE/'xl-final-script-pass.py');forms=final.load_forms(domain);scope=dict(parentCells=cells,parentExtent=domain,currentNativeActors=len(bounds),touchingNativeUids=sorted(touching),basicAndNativeForms=[b['uid']for b,_,_ in forms],allCurrentActorsNominated=True,fullAcceptance=False);save(DOC/'scope.json',scope)
 # Other patch overlap requires an explicit replacement plan, never silent exclusion.
 patches=module('wave275510_candidate_patches',HERE/'native_patch_resolution.py');overlap=[]
 for p in manifest['terrainPatches']:
  if p['url']!=OLD and box(*domain).intersection(box(*patches._patch_bounds(read(ROOT/'3d-viewer'/p['url'])))).area>1e-8:overlap.append(p['url'])
 assert not overlap,overlap
 second=module('wave275510_candidate_terrain',HERE/'xl-second-pass.py');second.LOCAL=LOCAL;terrain=BASE/'government-xl-four-qualified-original-podiums-physical-20261007-301560-0';sources=[];used=[];files=[]
 for sheet in read(terrain/'source-recovery.json')['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];sfiles=[];refs.append(folder/'original/download.json')
  for e in sheet['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p);sfiles.append(dict(path=str(p.relative_to(ROOT)),sha256=e['sha256']))
   if p.suffix=='.gltf':sources.append(second.terrain_triangles(p))
  used.append(dict(sheet=folder.name,revision=proof['revisionDate'],sourceETag=proof['sourceETag'],directorySHA256=proof['directorySHA256'],sourceFiles=sfiles));files.extend(sfiles)
 native=np.concatenate(sources);native=native[(native[:,:,0].max(1)>=domain[0])&(native[:,:,0].min(1)<=domain[2])&(native[:,:,2].max(1)>=domain[1])&(native[:,:,2].min(1)<=domain[3])];assert len(native)
 verdant=next(r for r in read(BASE/'government-xl-wave-neighbours-terrain-capture-v1-20261017/selection.json.gz')['rows']if r['uid']=='landsd/195000:0');raw=(ROOT/verdant['candidate']['path']).read_bytes();assert digest(raw)==verdant['sourceSHA256'];world.append(packed_world_bounds(raw)['originalWholeSourceBounds']);refs.append(ROOT/verdant['candidate']['path']);core=[min(b[0][0]for b in world)-1,min(b[0][2]for b in world)-1,max(b[1][0]for b in world)+1,max(b[1][2]for b in world)+1];uids=[r['uid']for r in rows]
 validate=second.resolution.validate_patch;second.resolution.validate_patch=lambda *_:None
 try:patch=second.resolution.make_patch(dict(uids=uids,cells=cells),parent,native,used,native_core=core,terrain_triangle_budget=100000,allow_native_below_clamp=bool((native[:,:,1]<1.2).any()),parent_url=PARENT,parent_sha256=digest(parentpath.read_bytes()))
 finally:second.resolution.validate_patch=validate
 sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True);meshes={}
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];meshes[r['uid']]=decode_original_world_triangles(raw)
  dest=LOCAL/'assets'/(r['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);r['candidate']['path']=str(dest.relative_to(ROOT));r['candidate']['entry']['asset']='assets/'+dest.name;refs.append(dest)
 projection=shapely.union_all([shapely.union_all(shapely.polygons(t[:,:,[0,2]]))for t in meshes.values()]);save(LOCAL/'unfilled-patch.json',patch);gap=patches.projected_context(patch,domain)[2].intersection(projection)
 fill=patches.fill_narrow_source_seam(patch,domain,projection,sampler,tolerance=.02)if gap.area>1e-6 else patches.fill_parent_only_holes(patch,parent,domain,projection,sampler)
 remaining=float(patches.projected_context(patch,domain)[2].area);maximum=max(.25,(domain[2]-domain[0])*(domain[3]-domain[1])*1e-3);assert remaining<=maximum
 if remaining>1e-8:patch['nativeMesh']['source']['numericalCoverageGap']=dict(policy='parent-grid-fallback',measuredAreaM2=remaining,maximumAreaM2=maximum,maximumFraction=1e-3)
 patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,domain,sampler);path=LOCAL/(patch['id']+'.json');save(path,patch)
 if patches.projected_context(patch,domain)[3]>1e-8:patches.approve_original_overlap(patch,path,DOC/'native-overlap.json',files);patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
 validate(patch,parent);save(path,patch);refs.append(path)
 candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=uids,bounds=domain,triangles=len(patch['nativeMesh']['index'])//3)
 save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestsha));save(DOC/'construction.json',dict(core=core,nativeTriangles=len(native),fill=fill,remainingGapM2=remaining,strictTerrainValidatorPassed=True,publication=False))
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 rt=read(LOCAL/'runtime-geometry.json.gz');foundations=[]
 for r in rows:
  g=next(g for g in rt['rows']if g['uid']==r['uid']);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert tri.shape==meshes[r['uid']].shape and np.max(np.abs(tri-meshes[r['uid']]))<=1e-9;ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=r['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));ok=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0;foundations.append(dict(uid=r['uid'],passed=ok,buried=f['fullyBuriedTriangles']));save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);print(foundations[-1],flush=True)
 for p,h in rt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([LOCAL/'runtime-geometry.json.gz',terrain/'source-recovery.json',prior/'complete-bounds.json.gz',manifestpath,parentpath,HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py']);assert digest(manifestpath.read_bytes())==manifestsha and reservations.owns(lease)
 summary=dict(scope=scope,foundations=foundations,strictTerrainValidatorPassed=True,fullAcceptance=False);save(DOC/'summary.json',summary);out=module('wave275510_candidate_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'same-parent-verdant-whole-source-protected-core-candidate-v2',list(set(refs)),dict(uids=uids,summary=summary,fullAcceptance=False,nextStep='Complete basic/native before-after regression, source crossing interpretation and canonical support/runtime/browser requirements before publication.'));print(dict(jobId=out['jobId'],summary=summary),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();rows,world,cells,domain=plan();final=module('wave275510_candidate_lease_forms',HERE/'xl-final-script-pass.py');uids={r['uid']for r in rows}|{b['uid']for b,_,_ in final.load_forms(domain)}
 prior=read(BASE/'government-xl-wave275510-current-native-scope-v1-20261017/complete-bounds.json.gz')['rows'];uids|={r['uid']for r in prior if not closed_disjoint(r['completeFourWorldBounds'],domain)}
 resources=[('building:'if u.startswith('landsd/')else'source-form:')+u for u in sorted(uids)]+['terrain-surface:wave-original-301560']+['terrain-patch:'+r['uid']for r in rows]
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
