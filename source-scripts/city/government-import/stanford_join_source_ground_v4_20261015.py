"""Complete unchanged hotel source against actual private joined terrain; diagnostic only."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-join-source-ground-v4-20261015';DOC=BASE/BATCH;CAP=BASE/'government-xl-stanford-join-runtime-capture-v4-20261015'
def main():
 assert not DOC.exists();DOC.mkdir();r=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json',HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 source=next(s for s in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if s['modelId']=='B365201779201063C0');asset=ROOT/source['asset']['path'];refs.append(asset);assert digest(asset.read_bytes())==source['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());ground=np.asarray(read(CAP/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;zero=np.flatnonzero(~valid).tolist();ground=ground[valid];polys=polys[valid];tree=shapely.STRtree(polys);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);rows=[]
 for i,face in enumerate(tri):
  c=face_ground_context(face,ground,polys,tree)if length[i]>0 else degenerate_ground_context(face,ground,polys,tree);c['sourceFace']=i;rows.append(c)
  if i%1000==0:print(i,len(tri),flush=True)
 failed=[i for i,c in enumerate(rows)if c.get('minimum')and c['minimum']['minimumGapM']<-.5];up=[i for i in failed if length[i]and normal[i,1]/length[i]>.25];missing=[i for i,c in enumerate(rows)if not c['groundProjectionCovered']];summary={'completeSourceFaces':len(tri),'belowHalfMetreFaces':failed,'upwardBelowHalfMetreFaces':up,'uncoveredFaces':missing,'sourceSHA256':source['sourceSHA256'],'sourceGeometryChanges':0,'fullAcceptance':False,'qualification':'Original world coordinates against actual rendered terrain. Floating continuous minima only; explicit runtime model arithmetic, support, sampler fallback and browser checks remain.'};save(DOC/'faces.json.gz',{'rows':rows,'nonHeightFieldTerrainFaces':zero});save(DOC/'summary.json',summary)
 module('freeze_stanford_source_ground',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-source-actual-joined-terrain-minima-v4',refs,{'uids':['landsd/305584:0','landsd/335875:0'],'summary':summary,'fullAcceptance':False});print({k:(len(v)if isinstance(v,list)else v)for k,v in summary.items()},flush=True)
if __name__=='__main__':main()
