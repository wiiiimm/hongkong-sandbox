"""Private source terrain candidate retaining both existing native children in full."""
import json, sys, uuid, subprocess
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import native_patch_resolution as repair

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-lai-chi-kok-full-terrain-candidate-v2-20261019'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
SCOPE = BASE/'government-xl-lai-chi-kok-expanded-terrain-scope-v1-20261019'
PROJECTION = BASE/'government-xl-star-ferry-retained-projection-v1-20261019'
UID = 'landsd/281463:0'

def half(poly, axis, value, sign):
    out = []
    for a, b in zip(poly, poly[1:]+poly[:1]):
        da, db = sign*(a[axis]-value), sign*(b[axis]-value)
        if da >= 0:
            out.append(a)
        if (da < 0 < db) or (db < 0 < da):
            out.append(a+(b-a)*(da/(da-db)))
    return out

def outside(face, bounds):
    """Clip in XYZ, including projected-vertical triangles, without moving planes."""
    inside, result = list(face), []
    for axis, value, sign in [(0,bounds[0],1),(0,bounds[2],-1),(2,bounds[1],1),(2,bounds[3],-1)]:
        if len(inside) < 3:
            break
        rejected = half(inside, axis, value, -sign)
        # Entirely boundary-coincident faces belong to the retained child.
        if any(sign*(p[axis]-value) < 0 for p in inside):
            result.extend([[rejected[0],rejected[i],rejected[i+1]] for i in range(1,len(rejected)-1)])
        inside = half(inside, axis, value, sign)
    return result

def owned():
 from source_surface_inset_collection_v1_20261019 import inset_faces
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 refs=[Path(__file__),HERE/'source_surface_inset_collection_v1_20261019.py',HERE/'native_patch_resolution.py'];pins={}
 folders=[SCOPE,BASE/'government-xl-lai-chi-kok-exposed-source-nomination-v2-20261019',BASE/'government-xl-lai-chi-kok-remaining-buried-coverage-v2-20261019']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in folders:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 scope=read(SCOPE/'summary.json');cells=scope['coarseCells'];bounds=scope['expandedExtent'];assert len(scope['overlappingTerrain'])==1
 oldinfo=scope['overlappingTerrain'][0];oldpath=ROOT/oldinfo['path'];old=read(oldpath);assert digest(oldpath.read_bytes())==oldinfo['sha256'];oldbounds=oldinfo['extent']
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
 selectionpath=BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz';selection=read(selectionpath);row=next(r for r in selection['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 builder=module('lai_full_constructor',HERE/'resolve-pass-indexed-parent-clipping.py');assert builder.extent(cells,parent)==bounds
 groundpath=HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/281463:0-ground.json.gz';ground=read(groundpath);native=np.asarray(ground['completeAdjoiningTerrain']);mask=(native[:,:,0].max(1)>=bounds[0])&(native[:,:,0].min(1)<=bounds[2])&(native[:,:,2].max(1)>=bounds[1])&(native[:,:,2].min(1)<=bounds[3]);native=native[mask]
 sourcespath=BASE/'government-xl-next-five-adjoining-ground-v1-20261018/acquisitions.json';sources=[s for s in read(sourcespath)if s['sheet']in ground['sheets']]
 lo,hi=row['candidate']['entry']['worldBounds'];core=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2];validator=builder.validate_patch;builder.validate_patch=lambda *_:None
 try:patch=builder.make_patch(dict(uids=[UID,*old['meta']['targetUids']],cells=cells),parent,native,sources,native_core=core,allow_native_below_clamp=True,terrain_triangle_budget=1000000)
 finally:builder.validate_patch=validator
 t=decode_original_world_triangles(asset.read_bytes())[:,:,[0,2]];projection=shapely.union_all([shapely.union_all(shapely.polygons(t)),shapely.union_all(shapely.linestrings(np.concatenate([t,t[:,:1]],axis=1))),shapely.union_all(shapely.points(t.reshape(-1,2)))])
 sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
 repair.preserve_parent_under_projection(patch,bounds,shapely.box(*bounds).difference(projection.buffer(1,join_style='mitre')),sampler)
 faces=repair._faces(patch);clipped=[]
 for face in faces:
  if face[:,0].max()<oldbounds[0]or face[:,0].min()>oldbounds[2]or face[:,2].max()<oldbounds[1]or face[:,2].min()>oldbounds[3]:clipped.append(face)
  else:clipped.extend(outside(face,oldbounds))
 retained=repair._faces(old);faces=np.concatenate([np.asarray(clipped).reshape(-1,3,3),retained]);proofs=[]
 for d in folders[1:]:
  source=read(d/'surface-nomination.json.gz');faces,proof=inset_faces(faces,np.asarray(source['triangles']));save(DOC/(d.name+'-inset-proof.json.gz'),proof);proofs.append(dict(source=str(d.relative_to(ROOT)),changedFaces=len(proof['changedTerrainFaceIndices']),areaM2=proof['removedProjectedAreaM2']))
 patch['nativeMesh']['position']=faces.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(faces.size//3));patch['nativeMesh']['source']['authoredSurfaceInsets']=proofs
 path=DOC/'private-terrain.json';save(path,patch);error=None
 try:validator(patch,parent)
 except Exception as exc:error=str(exc)
 candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=[UID],replaces=dict(url=oldinfo['path'].removeprefix('3d-viewer/'),sha256=oldinfo['sha256'],retainedUids=old['meta']['targetUids']))
 save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'selection.json.gz',{**selection,'rows':[row]})
 summary=dict(uid=UID,changedExtent=bounds,coarseCells=cells,affectedNativeUids=scope['touchingNativeUids'],terrainFaces=len(faces),retainedOriginalFaces=len(retained),insetProofs=proofs,nativeValidatorError=error,installationApproved=False,sourceGeometryChanges=0,liveAssetsChanged=False)
 save(DOC/'summary.json',summary);refs.extend([asset,parentpath,oldpath,selectionpath,groundpath,sourcespath,HERE/'resolve-pass-indexed-parent-clipping.py'])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease)
 module('lai_full_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-full-private-terrain-candidate',refs,dict(uids=[UID],summary=summary,installationApproved=False));print(summary,flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();scope=read(SCOPE/'summary.json');uids=[UID,*scope['touchingNativeUids']];resources=sorted({'building:'+u for u in uids}|{'terrain-patch:'+u for u in uids})
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
