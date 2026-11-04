"""Private pool/market shared source terrain, retaining all original model bytes."""
from pathlib import Path
import numpy as np
import shapely
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import inset_faces
import native_patch_resolution as patches
BATCH='government-xl-sham-shui-po-pool-shared-terrain-v1-20261016';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;BASIN=BASE/'government-xl-sham-shui-po-pool-basin-source-v1-20261016';CURRENT=BASE/'government-xl-sham-shui-po-pool-current-ground-v1-20261016'
def overlap_proof(patch,sources):
 mesh=patch['nativeMesh'];mesh.pop('sourceOverlap',None);raw=DOC/'unapproved-terrain.json';save(raw,patch);t=np.asarray(mesh['position'],dtype=np.float32).astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];ps=shapely.polygons(t[:,:,[0,2]]);valid=shapely.area(ps)>1e-10;ids=np.flatnonzero(valid);ps=ps[valid];pairs=shapely.STRtree(ps).query(ps,predicate='intersects');rows=[];samples=0;error=0.
 for ia,ib in zip(*pairs):
  if ia>=ib:continue
  p=ps[ia].intersection(ps[ib])
  if p.area<=1e-10:continue
  xy=shapely.get_coordinates(p);es=[]
  for f in [t[ids[ia]],t[ids[ib]]]:
   a,b,c=f;u=b-a;v=c-a;d=xy-a[[0,2]];det=u[0]*v[2]-u[2]*v[0];s=(d[:,0]*v[2]-d[:,1]*v[0])/det;q=(u[0]*d[:,1]-u[2]*d[:,0])/det;bary=a[1]+s*u[1]+q*v[1];n=np.cross(u,v);plane=a[1]-(n[0]*d[:,0]+n[2]*d[:,1])/n[1];es.append(float(np.abs(bary-plane).max()));samples+=len(xy)
  error=max(error,*es);rows.append(dict(faces=[int(ids[ia]),int(ids[ib])],areaM2=p.area,equationErrorsM=es))
 excess=float(shapely.area(ps).sum()-shapely.union_all(ps).area)
 if rows:
  assert error<.01
  ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
  evidence=DOC/'highest-surface-proof.json';save(evidence,dict(stagedGeometrySha256=digest(raw.read_bytes()),nativeProjectedExcessM2=excess,float32HighestRayAgreement=dict(samples=samples,maxError=error,rows=rows,method='Every positive overlap polygon vertex; independent affine/barycentric plane equations. Runtime checks remain separate.'),source=dict(files=[ref(p) for p in [raw,Path(__file__),*sources]])))
  mesh['sourceOverlap']=dict(policy='highest-native-surface',measuredProjectedExcessM2=excess,evidencePath=str(evidence.relative_to(ROOT)),evidenceSHA256=digest(evidence.read_bytes()))
def main():
 assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__),HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [BASIN,CURRENT]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for q in r['evidenceRefs']:assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);oldurl='city/data/government-native-138091-0.json';assert any(p['url']==oldurl for p in manifest['terrainPatches']);oldpath=ROOT/'3d-viewer'/oldurl;old=read(oldpath);refs.append(oldpath);retained=[]
 for url in manifest['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url
  for e in read(cp)['models']:
   if e['uid']in ['landsd/113733:0','landsd/138091:0']:retained.append(e);refs.append(cp)
 assert len(retained)==2;selection=read(CURRENT/'selection.json.gz');row=selection['rows'][0];entries=[row['candidate']['entry'],*retained];bounds=np.array([e['worldBounds'] for e in entries]);combined=[bounds[:,0,:].min(axis=0).tolist(),bounds[:,1,:].max(axis=0).tolist()];helper=module('pool_shared_constructor',HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);cells=helper.rectangle_for(combined,parent);cells=[min(cells[0],old['coarseCells'][0]),min(cells[1],old['coarseCells'][1]),max(cells[2],old['coarseCells'][2]),max(cells[3],old['coarseCells'][3])];domain=helper.extent(cells,parent);sourcefiles=[];sourceMeta=[];parts=[]
 for s in old['meta']['source']['nativeSources']:
  for f in s['sourceFiles']:
   p=ROOT/f['path'];assert digest(p.read_bytes())==f['sha256'];sourcefiles.append(p);refs.append(p)
   if p.suffix=='.gltf':
    t=helper.context.triangles(p);mask=(t[:,:,0].max(axis=1)>=domain[0])&(t[:,:,0].min(axis=1)<=domain[2])&(t[:,:,2].max(axis=1)>=domain[1])&(t[:,:,2].min(axis=1)<=domain[3]);parts.append(t[mask]);sourceMeta.append(dict(path=f['path'],sha256=f['sha256']))
 source=read(BASIN/'basin-source.json.gz');sourcefile=BASIN/'basin-source.json.gz';sourcefiles.append(sourcefile);basin=np.array(source['triangles']);native=np.concatenate(parts);lo,hi=combined;core=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2];protected=shapely.union_all([shapely.box(e['worldBounds'][0][0],e['worldBounds'][0][2],e['worldBounds'][1][0],e['worldBounds'][1][2]) for e in entries]);DOC.mkdir();LOCAL.mkdir();validate=helper.validate_patch
 def finish(p,parent):
  grid=helper.terrain.fine.DemSampler(parent,rendered=True);fill=patches.fill_parent_only_holes(p,parent,domain,protected,grid);before=patches._faces(p);after,proof=inset_faces(before,basin);save(DOC/'inset-proof.json.gz',proof);p['nativeMesh']['position']=after.reshape(-1).tolist();p['nativeMesh']['index']=list(range(after.size//3));p['nativeMesh']['source']['authoredBasinInset']=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],sourceFaceIndices=source['sourceFaceIndices'],policy=proof['policy']);save(DOC/'parent-fill.json',fill);overlap_proof(p,sourcefiles);save(DOC/'pre-validation-terrain.json',p);validate(p,parent)
 helper.validate_patch=finish;group=dict(uids=[e['uid'] for e in entries],cells=cells);patch=helper.make_patch(group,parent,native,sourceMeta,native_core=core,allow_native_below_clamp=True);path=DOC/'private-terrain.json';save(path,patch);candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=[row['uid']],replaces=dict(url=oldurl,sha256=digest(oldpath.read_bytes()),retainedUids=[e['uid'] for e in retained]));save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'selection.json.gz',selection)
 tool=HERE/'acceptance-metrics-retained-group-parent.mjs';cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str((HERE/'local'/CURRENT.name).relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with (DOC/'worker.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 metrics=read(DOC/'metrics.json');assert not metrics['rows'][0].get('error');g=read(LOCAL/'runtime-geometry.json.gz')['rows'][0];t=np.array(g['position']).reshape(-1,3)[np.array(g['index']).reshape(-1,3)];ground=np.array(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];foundation=module('pool_shared_foundation',HERE/'xl-final-script-pass.py').foundation_context(t,ground,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=dict(uid=row['uid'],retainedUids=[e['uid'] for e in retained],changedParentExtent=domain,coarseCells=cells,sourceCore=core,terrainFaces=len(patch['nativeMesh']['index'])//3,validationPassed=True,foundation=foundation,metrics=metrics['rows'][0],fullAcceptance=False,neighboursChecked=False,liveAssetsChanged=False);save(DOC/'summary.json',summary);refs.extend([parentpath,manifestpath,tool,LOCAL/'runtime-geometry.json.gz',HERE/'resolve-pass.py',HERE/'xl-final-script-pass.py'])
 out=module('pool_shared_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-pool-market-shared-original-terrain-v1',list(dict.fromkeys(refs)),dict(uids=group['uids'],summary=summary,fullAcceptance=False,newlyInstalled=0,privateTerrainGeometryChanged=True));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
