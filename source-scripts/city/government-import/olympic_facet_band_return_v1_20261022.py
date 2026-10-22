"""Join only a two-metre terrain strip to the exact prior native upper surface."""
from pathlib import Path
from fractions import Fraction
import traceback,numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from native_facet_band_return_v1 import join
from native_patch_resolution import grid_surface_faces
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-facet-band-return-v1-20261022'
def clean(v):
 if isinstance(v,Fraction):return str(v)
 if isinstance(v,dict):return {str(k):clean(x)for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [clean(x)for x in v]
 if isinstance(v,np.generic):return v.item()
 return v
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();prior=BASE/'government-xl-olympic-narrow-retained-candidate-v1-20261022';r,pins=authenticate(prior);path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['candidate']['sha256'];p=read(path);oldpath=ROOT/'3d-viewer'/r['candidate']['replaces']['url'];assert digest(oldpath.read_bytes())==r['candidate']['replaces']['sha256'];old=read(oldpath);rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);mp=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(mp.read_bytes());input=prior/'input.json';assert digest(input.read_bytes())==pins[str(input.relative_to(ROOT))];outer=read(input)['cut'];width=2.
 runtime=BASE/'government-xl-olympic-station-narrow-runtime-v1-20261022';_,rpins=authenticate(runtime);gp=HERE/'local'/runtime.name/'runtime-geometry.json.gz';assert digest(gp.read_bytes())==rpins[str(gp.relative_to(ROOT))];v=np.asarray(read(gp)['rows'][0]['position']).reshape(-1,3);distance=float(np.minimum.reduce([v[:,0]-outer[0],outer[2]-v[:,0],v[:,2]-outer[1],outer[3]-v[:,2]]).min());assert distance>width
 builder=module('olympic_native_return_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');domain=builder.extent(p['coarseCells'],root);root_sampler=builder.terrain.fine.DemSampler(root,rendered=True)
 def actual(node):return np.asarray(node['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(node['nativeMesh']['index']).reshape(-1,3)]
 before,new=actual(old),actual(p);print(dict(phase='authored-facet-band-join',oldFaces=len(before),newFaces=len(new),wholeModelBoundaryMarginM=distance),flush=True);out,proof=join(before,new,domain,outer,width,builder.exact,lambda region:grid_surface_faces(root_sampler,region));save(doc/'facet-band-certificate.json.gz',clean(proof));p['nativeMesh']['position']=out.reshape(-1).tolist();p['nativeMesh']['index']=list(range(out.size//3));p['nativeMesh'].pop('sourceOverlap',None)
 for key in ['numericalCoverageGap','numericalProjectionOverlap']:p['nativeMesh']['source'].pop(key,None)
 p['nativeMesh']['source']['nativeFacetBandReturn']=dict(widthM=width,modelMinimumBoundaryDistanceM=distance,certificate=dict(path=str((doc/'facet-band-certificate.json.gz').relative_to(ROOT)),sha256=digest((doc/'facet-band-certificate.json.gz').read_bytes())),policy='Terrain-only computed strip retains separate original outer facets/layers and joins the new finite maximum field. Any missing field pieces use actual newly generated root-DEM facets inside the strip, outside the complete building bounds. This is not a single continuous upper-graph proof. Original building/source pose unchanged. Fresh packing, whole-source, neighbour and browser checks required.')
 refs=[Path(__file__),prior/'result.json',input,path,oldpath,rootpath,mp,runtime/'result.json',gp,HERE/'native_facet_band_return_v1.py',HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py',HERE/'exact_faithful_multisurface_transition_domain_v1_20261011.py',HERE/'exact_compute_transition_mesh_v1_20261011.py',HERE/'exact_source_core_ten_metre_transition_domain_v1_20261011.py',HERE/'exact_closed_ground_aabb_pruning_v1_20261011.py',HERE.parent/'assembly-support-review/exact_tin.py',ROOT/'3d-viewer/city/native-terrain.js',ROOT/'3d-viewer/city/world.js'];result=dict(uids=r['uids'],retainedUids=r['retainedUids'],sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,publication=False,widthM=width,modelMinimumBoundaryDistanceM=distance,terrainTriangles=len(out),terrainTriangleBudget=len(before)+25000)
 try:
  from float32_coverage import approve_roundoff
  save(doc/'coverage.json',approve_roundoff(p,domain));checker=module('olympic_native_return_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');checker.DOC=doc;checker.overlap_proof(p,refs);builder.validate_patch(p,root);assert len(out)<=len(before)+25000
  target=local/'candidate-terrain.json';save(target,p);refs.append(target);result.update(status='private-terrain-validator-passed',candidate=dict(path=str(target.relative_to(ROOT)),sha256=digest(target.read_bytes()),replaces=r['candidate']['replaces']))
 except Exception as e:result.update(status='bounded-native-return-investigation',reason=str(e));save(doc/'failure.json',dict(message=str(e),traceback=traceback.format_exc()));save(doc/'unapproved-terrain.json',p)
 assert digest(mp.read_bytes())==msha;save(doc/'scope.json',dict(uids=r['uids'],cells=p['coarseCells'],bounds=domain));save(doc/'summary.json',result);refs.extend([HERE/'float32_coverage.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py']);module('olympic_bounded_native_return_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-prior-native-upper-surface-return',refs,result);print(result,flush=True)
if __name__=='__main__':main()
