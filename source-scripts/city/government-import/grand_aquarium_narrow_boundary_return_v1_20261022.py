"""Private two-metre parent return, outside Grand Aquarium's complete original bounds."""
from pathlib import Path
import numpy as np,traceback
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from bounded_root_terrain_return_v1 import transition
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-narrow-boundary-return-v1-20261022'
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists()
 prior=BASE/'government-xl-grand-aquarium-retained-followthrough-v1-20261022-candidate';r,pins=authenticate(prior);path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['candidate']['sha256'];p=read(path);rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath)
 rp=BASE/'government-xl-grand-aquarium-repaired-boundary-runtime-v3-20261022';_,gp=authenticate(rp);geometrypath=HERE/'local'/rp.name/'runtime-geometry.json.gz';assert digest(geometrypath.read_bytes())==gp[str(geometrypath.relative_to(ROOT))];g=read(geometrypath)['rows'][0];v=np.asarray(g['position']).reshape(-1,3)
 builder=module('narrow_return_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');bb=builder.extent(p['coarseCells'],root);width=2.;distance=float(np.minimum.reduce([v[:,0]-bb[0],bb[2]-v[:,0],v[:,2]-bb[1],bb[3]-v[:,2]]).min());assert distance>width
 refs=[Path(__file__),HERE/'bounded_root_terrain_return_v1.py',prior/'result.json',prior/'summary.json',path,rootpath,rp/'result.json',geometrypath]
 sampler=builder.terrain.fine.DemSampler(root,rendered=True);pg=root['meta']['georef'];cell=pg['aE'];c0,r0,c1,r1=p['coarseCells'];cells=[]
 for row in range(r0,r1):
  for col in range(c0,c1):
   a=np.array([pg['bE']+col*cell-834500,816500-pg['bN']+row*cell]);b=a+[cell,0];d=a+[0,cell];e=a+[cell,cell];cells.extend([np.array([a,b,d]),np.array([b,e,d])])
 pos=np.asarray(p['nativeMesh']['position']).reshape(-1,3);faces=pos[np.asarray(p['nativeMesh']['index']).reshape(-1,3)];out=transition(faces,bb,cells,sampler.ground,width,builder.exact)
 p['nativeMesh']['position']=out.reshape(-1).tolist();p['nativeMesh']['index']=list(range(out.size//3));p['nativeMesh'].pop('sourceOverlap',None)
 for key in ['numericalCoverageGap','numericalProjectionOverlap']:p['nativeMesh']['source'].pop(key,None)
 p['meta']['source']['boundedParentReturn']=dict(widthM=width,modelMinimumBoundaryDistanceM=distance,policy='Terrain-only strip split on original root DEM triangles, exact root join at boundary and unchanged interior. No original model geometry edits; whole retained scene requires fresh checks.')
 result=dict(uids=r['uids'],retainedUids=r['retainedUids'],sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0,publication=False,scriptExternalAICalls=0)
 try:
  from float32_coverage import approve_roundoff
  save(doc/'coverage.json',approve_roundoff(p,bb));proof=module('narrow_return_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=doc;proof.overlap_proof(p,refs);builder.validate_patch(p,root);budget=r['retainedTerrainFaces']+25000;assert len(out)<=budget,'Incremental terrain runtime budget exceeded'
  target=local/'candidate-terrain.json';save(target,p);refs.append(target);result.update(status='private-terrain-validator-passed',candidate=dict(path=str(target.relative_to(ROOT)),sha256=digest(target.read_bytes()),replaces=r['candidate']['replaces']),terrainTriangles=len(out),terrainTriangleBudget=budget,widthM=width,modelMinimumBoundaryDistanceM=distance)
 except Exception as e:result.update(status='narrow-return-investigation',reason=str(e));save(doc/'failure.json',dict(message=str(e),traceback=traceback.format_exc()));save(doc/'unapproved-terrain.json',p)
 save(doc/'scope.json',dict(uids=r['uids'],cells=p['coarseCells'],bounds=bb));save(doc/'summary.json',result);refs.extend(HERE/n for n in ['resolve_pass_indexed_parent_clipping_v2.py','sham_shui_po_pool_shared_terrain_v2_20261016.py','float32_coverage.py']);module('narrow_return_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-parent-terrain-return',refs,result);print(result,flush=True)
if __name__=='__main__':main()
