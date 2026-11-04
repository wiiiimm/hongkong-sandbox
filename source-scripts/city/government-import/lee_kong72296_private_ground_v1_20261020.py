"""Private flat native-parent composition. No publication or acceptance waivers."""
import json,sys,uuid,subprocess,traceback
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lee-kong72296-private-ground-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SCOPE=BASE/'government-xl-lee-kong72296-current-scope-v1-20261020';GROUND=BASE/'government-xl-next-twenty-original-ground-v3-20261020';CAP=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';UID='landsd/72296:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)];receipts={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SCOPE,GROUND,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');receipts[folder.name]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def pin(p,folder):
  key=str(p.relative_to(ROOT));h=receipts[folder.name][key];assert digest(p.read_bytes())==h,key;assert key not in pins or pins[key]==h;pins[key]=h
 for key in receipts[SCOPE.name]:pin(ROOT/key,SCOPE)
 pin(CAP/'selection.json.gz',CAP);row=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']==UID);pin(ROOT/row['candidate']['path'],CAP)
 groundpath=HERE/'local'/GROUND.name/'72296:0-ground.json.gz';pin(groundpath,GROUND);data=read(groundpath);sourcepath=ROOT/data['sourcePath'];pin(sourcepath,GROUND)
 for buf in read(sourcepath)['buffers']:pin(sourcepath.parent/buf['uri'],GROUND)
 scope=read(SCOPE/'scope.json')['rows'][0];assert len(scope['overlappingInstalledTerrain'])==1;old=scope['overlappingInstalledTerrain'][0];parentpath=ROOT/'3d-viewer'/old['url'];parent=read(parentpath);assert parent.get('nativeMesh') and not parent.get('patches');assert digest(parentpath.read_bytes())==old['sha256']
 builder=module('unnamed_ground_builder',HERE/'resolve-pass-indexed-parent-clipping.py');repair=module('unnamed_ground_repair',HERE/'native_patch_resolution.py');rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);bounds=old['extent'];assert builder.extent(parent['coarseCells'],root)==bounds
 original=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());xz=original[:,:,[0,2]];print('begin exact projection',flush=True)
 area=shapely.union_all(shapely.polygons(xz));print('area union complete',flush=True)
 edges=shapely.linestrings(np.concatenate([xz,xz[:,:1]],axis=1));remaining=shapely.difference(edges,area)
 # A union B equals A union (B minus A); avoid noding all interior edges.
 outside=remaining[~shapely.is_empty(remaining)];projection=shapely.union_all([area,*outside])
 points=shapely.points(xz.reshape(-1,2));extra=points[~shapely.covers(projection,points)]
 if len(extra):projection=shapely.union_all([projection,*extra])
 edge_residue=shapely.difference(edges,projection);empty=shapely.is_empty(edge_residue)
 assert shapely.covers(projection.buffer(1,join_style='mitre'),edges).all(),'actual-terrain-protection-omits-source-edge'
 assert shapely.covers(projection.buffer(1,join_style='mitre'),points).all(),'actual-terrain-protection-omits-source-vertex'
 print('complete protected projection',len(edges),'edges',len(outside),'outside',len(extra),'extra vertices',flush=True)
 lo,hi=original.min((0,1)),original.max((0,1));core=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2];native=np.asarray(data['completeOriginalTerrain']);influence=[core[0]-10,core[1]-10,core[2]+10,core[3]+10];native=native[(native[:,:,0].max(1)>=influence[0])&(native[:,:,0].min(1)<=influence[2])&(native[:,:,2].max(1)>=influence[1])&(native[:,:,2].min(1)<=influence[3])]
 DOC.mkdir();save(DOC/'projection-accounting.json',dict(completeSourceFaces=len(original),completeSourceEdges=len(edges)*3,remainingOutsideRings=len(outside),extraVertices=len(extra),exactEmptyEdgeRings=int(empty.sum()),nonemptyEdgeRings=int((~empty).sum()),residualEdgeLengthM=float(shapely.length(edge_residue).sum()),actualUnchangedOneMetreProtectionCoversEveryEdgeAndVertex=True,geometryChanges=0));save(DOC/'scope.json',dict(uid=UID,fullReplacementBounds=bounds,requiredNativeUids=old['parentNativeUids'],touchingLocalNativeUids=old['touchingNativeUids'],nativeParentCannotNest=True,identityApprovalPending=True,publication=False));error=None
 try:
  validator=builder.validate_patch
  builder.validate_patch=lambda *_:None
  sources=[dict(terrainPaths=[str(sourcepath.relative_to(ROOT))],provenanceReceipt=read(GROUND/'result.json')['jobId'])]
  try:patch=builder.make_patch(dict(uids=[UID],cells=parent['coarseCells']),root,native,sources,native_core=core,terrain_triangle_budget=25000)
  finally:builder.validate_patch=validator
  from rendered_patch_sampler import RenderedPatchSampler
  rootsampler=builder.terrain.fine.DemSampler(root,rendered=True);
  class ExactRetainedSampler(RenderedPatchSampler):
   def surface_faces(self,protected):
    output=[];inside=protected.intersection(self.extent);outside=protected.difference(self.extent);covered=[];unchanged=0;clippedCount=0
    for i in self.tree.query(inside,predicate='intersects'):
     face=self.faces[i];poly=self.polygons[i]
     if inside.covers(poly):
      output.append(face.tolist());covered.append(poly);unchanged+=1;continue
     clipped=poly.intersection(inside);covered.append(clipped);clippedCount+=1
     for part in shapely.get_parts(clipped):
      if part.geom_type!='Polygon':continue
      for triangle in repair._triangles(part):output.append([[x,self.height(face,x,z),z]for x,z in list(triangle.exterior.coords)[:3]])
    gaps=inside.difference(shapely.union_all(covered));output.extend(repair.grid_surface_faces(self.grid,gaps));output.extend(repair.grid_surface_faces(self.fallback,outside))
    save(DOC/'retained-exact-facets.json',dict(unchangedOriginalFloat32Facets=unchanged,clippedOriginalFacets=clippedCount,existingParentGapAreaM2=gaps.area,sourceBuildingChanges=0));assert output;return output
  sampler=ExactRetainedSampler(parent,rootsampler,builder.terrain.fine.DemSampler(parent,rendered=True));protected=shapely.box(*bounds).difference(projection.buffer(1,join_style='mitre'))
  proof=repair.preserve_parent_under_projection(patch,bounds,protected,sampler,edge_sampler=rootsampler)
  # The surface sampler omits projected-vertical faces. Preserve all those drawn
  # parent facets explicitly; their presence must pass subsequent collision checks.
  faces=repair._faces(parent);det=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0])[:,1];vertical=faces[np.abs(det)<=1e-10]
  start=len(patch['nativeMesh']['position'])//3;patch['nativeMesh']['position'].extend(vertical.reshape(-1).tolist());patch['nativeMesh']['index'].extend(range(start,start+len(vertical)*3));proof['retainedParentVerticalFaces']=len(vertical);save(DOC/'parent-preservation.json',proof)
  patch['meta']['targetUids']=list(dict.fromkeys(parent['meta']['targetUids']+[UID]));path=LOCAL/'candidate-terrain.json';save(path,patch)
  save(DOC/'projection-coverage.json',dict(missingAreaM2=repair.projected_context(patch,bounds)[2].area,projectedExcessM2=repair.projected_context(patch,bounds)[3],sourceGeometryChanges=0))
  assert len(patch['nativeMesh']['index'])//3<=25000,'final-terrain-runtime-budget'
  validator(patch,root)
  save(DOC/'terrain-candidates.json',[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=[UID],replaces=dict(url=old['url'],sha256=old['sha256'],retainedUids=old['parentNativeUids']))])
 except Exception as exc:
  error=str(exc);save(DOC/'guard-failure.json',dict(error=error,traceback=traceback.format_exc(),installationApproved=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert reservations.owns(lease);refs.extend(ROOT/p for p in pins);refs.extend([rootpath,HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'native_patch_resolution.py',HERE/'rendered_patch_sampler.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 result=module('unnamed_ground_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'flat-native-parent-private-source-terrain-candidate',refs,dict(uids=[UID],guardFailure=error,installationApproved=False,identityApprovalPending=True,fullParentActorsPending=True));print(result['jobId'],error,flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();scope=read(SCOPE/'scope.json')['rows'][0]['overlappingInstalledTerrain'][0];keys=['building:'+u for u in scope['parentNativeUids']+[UID]]+['terrain:'+scope['url']];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
