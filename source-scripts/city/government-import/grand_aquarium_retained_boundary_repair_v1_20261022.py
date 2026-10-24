"""Private root-DEM edge transition for Grand Aquarium's complete retained terrain."""
from pathlib import Path
import traceback,numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-grand-aquarium-retained-boundary-repair-v1-20261022'
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists()
 prior=BASE/'government-xl-grand-aquarium-retained-followthrough-v1-20261022-candidate';_,pins=authenticate(prior)
 previous=read(prior/'summary.json');path=ROOT/previous['candidate']['path'];assert digest(path.read_bytes())==previous['candidate']['sha256']==pins[str(path.relative_to(ROOT))]
 candidate=read(path);rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);oldpath=ROOT/'3d-viewer'/previous['candidate']['replaces']['url'];assert digest(oldpath.read_bytes())==previous['candidate']['replaces']['sha256']
 lineage=BASE/'government-xl-grand-aquarium-boundary-lineage-diagnostic-v1-20261022';authenticate(lineage)
 refs=[Path(__file__),prior/'result.json',prior/'summary.json',path,rootpath,oldpath,lineage/'result.json',lineage/'summary.json']
 builder=module('grand_boundary_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');proof=module('grand_boundary_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=doc
 vertices=np.asarray(candidate['nativeMesh']['position']).reshape(-1,3);faces=vertices[np.asarray(candidate['nativeMesh']['index']).reshape(-1,3)]
 result=dict(uids=['landsd/93424:0'],installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,scriptExternalAICalls=0)
 try:
  def prepare(p):
   from float32_coverage import approve_roundoff
   save(doc/'coverage.json',approve_roundoff(p,builder.extent(candidate['coarseCells'],root)))
   proof.overlap_proof(p,refs)
  fixed=builder.make_patch(dict(cells=candidate['coarseCells'],uids=candidate['meta']['targetUids']),root,faces,candidate['meta']['source'].get('nativeSources',[]),parent_sha256=digest(rootpath.read_bytes()),terrain_triangle_budget=150000,prepare_validation=prepare)
  # Keep the installed patch's grid, water mask, vegetation and actor nomination.
  candidate['nativeMesh']=fixed['nativeMesh'];candidate['meta']['source']['rootBoundaryTransition']=dict(policy='Established 10m outer transition split on original root-DEM triangle boundaries. Whole retained model set requires fresh checks.',diagnostic=str((lineage/'summary.json').relative_to(ROOT)),diagnosticSHA256=digest((lineage/'summary.json').read_bytes()))
  count=len(candidate['nativeMesh']['index'])//3;budget=previous['retainedTerrainFaces']+25000
  if count>budget:
   from constant_colour_terrain_consolidation_v1 import consolidate_patch
   consolidated,certificate=consolidate_patch(candidate);save(doc/'exact-consolidation-certificate.json.gz',certificate);candidate['nativeMesh']['position']=consolidated.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(consolidated.size//3))
   refs.extend(HERE/n for n in ['constant_colour_terrain_consolidation_v1.py','exact_runtime_coplanar_consolidation_20261010.py','exact_coplanar_boundary_census_20261010.py','exact_runtime_coplanar_groups_20261010.py'])
  candidate['nativeMesh'].pop('sourceOverlap',None)
  for key in ['numericalCoverageGap','numericalProjectionOverlap']:candidate['nativeMesh']['source'].pop(key,None)
  from float32_coverage import approve_roundoff
  save(doc/'final-coverage.json',approve_roundoff(candidate,builder.extent(candidate['coarseCells'],root)))
  proof.overlap_proof(candidate,refs);builder.validate_patch(candidate,root)
  out=local/'candidate-terrain.json';save(out,candidate);refs.append(out);count=len(candidate['nativeMesh']['index'])//3
  result.update(status='private-terrain-validator-passed'if count<=budget else'terrain-runtime-budget-investigation',candidate=dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),replaces=previous['candidate']['replaces']),terrainTriangles=count,terrainTriangleBudget=budget,retainedUids=previous['retainedUids'])
 except Exception as e:
  result.update(status='retained-boundary-repair-investigation',reason=str(e));save(doc/'failure.json',dict(message=str(e),traceback=traceback.format_exc()))
 save(doc/'summary.json',result);refs.extend(HERE/n for n in ['resolve_pass_indexed_parent_clipping_v2.py','sham_shui_po_pool_shared_terrain_v2_20261016.py','float32_coverage.py'])
 module('grand_boundary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'retained-original-terrain-root-boundary-repair',refs,result)
 print(result,flush=True)
if __name__=='__main__':main()
