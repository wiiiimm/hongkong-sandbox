"""Preserve original base terrain beneath two unrelated Sol City footprints; private only."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-long-ping-candidate-physical-v1-20261017';OLD=BASE/'government-xl-long-ping-private-terrain-v2-20261017';BATCH='government-xl-long-ping-preserve-sol-city-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/251569:0','landsd/268424:0']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PRIOR,OLD]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 candidate=read(OLD/'terrain-candidates.json')[0];patch=read(ROOT/candidate['path']);assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];bounds=candidate['bounds'];inputs=read(PRIOR/'neighbour-inputs.json.gz');forms={r['building']['uid']:r['building']for r in inputs['rows']};g=read(HERE/'local'/PRIOR.name/'runtime-geometry.json.gz')['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]))
 protected=shapely.union_all([Polygon(forms[u]['rings'][0],forms[u]['rings'][1:]).buffer(1,join_style='mitre')for u in UIDS]);assert protected.intersection(projection).area<1e-8
 parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path);second=module('long_ping_sol_second',HERE/'xl-second-pass.py');patches=module('long_ping_sol_patch',HERE/'native_patch_resolution.py');sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
 proof=patches.preserve_parent_under_projection(patch,bounds,protected,sampler);proof.update(uids=UIDS,sourceIntersectionM2=float(protected.intersection(projection).area),sourceDistanceM=float(protected.distance(projection)),publicationApproved=False);save(DOC/'preservation.json',proof)
 patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler);patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler);path=LOCAL/'long-ping-sol-city-preserved.json';save(path,patch)
 files=read(OLD/'construction.json')['sourceFiles']
 if patches.projected_context(patch,bounds)[3]>1e-8:
  patch['nativeMesh'].pop('sourceOverlap',None);save(path,patch);patches.approve_original_overlap(patch,path,DOC/'native-overlap.json',files);patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
 else:patch['nativeMesh'].pop('sourceOverlap',None)
 second.resolution.validate_patch(patch,parent);save(path,patch);new={**candidate,'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'triangles':len(patch['nativeMesh']['index'])//3};save(DOC/'terrain-candidates.json',[new])
 refs.extend([ROOT/candidate['path'],OLD/'terrain-candidates.json',OLD/'construction.json',PRIOR/'neighbour-inputs.json.gz',HERE/'local'/PRIOR.name/'runtime-geometry.json.gz',parent_path,path,HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py']);refs.extend(ROOT/p for p in inputs['inputHashes']);refs.extend(ROOT/f['path']for f in files)
 out=module('long_ping_sol_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'long-ping-two-unrelated-sol-city-base-terrain-preservation-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/107382:0']+UIDS,candidate=new,preservation=proof,fullAcceptance=False,nextStep='Rerun station foundation and all basic/native neighbours. The overlapping unnamed OSM station-access actor remains unresolved; do not suppress it by inference.'));print(dict(jobId=out['jobId'],candidate=new,preservation=proof),flush=True)
if __name__=='__main__':main()
