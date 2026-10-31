"""Whole original source faces at surviving podium grade diagnostics."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-original-grade-faces-v1-20261018';DOC=BASE/BATCH
TERRAIN=BASE/'government-xl-olympian-two-three-podium-terrain-v2-20261018';LOC=BASE/'government-xl-olympian-two-podium-clearance-locations-v2-20261018'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [TERRAIN,LOC]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 second=module('olympian_grade',HERE/'xl-second-pass.py');parts=[]
 for sheet in read(BASE/'government-xl-olympian-two-current-retained-terrain-v1-20261018/source-recovery.json')['sheets']:
  for e in sheet['terrainFiles']:
   p=ROOT/sheet['cache']/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':parts.append(second.terrain_triangles(p))
 original=np.concatenate(parts);summaries=[]
 for g in read(HERE/'local'/TERRAIN.name/'runtime-geometry.json.gz')['rows']:
  uid=g['uid'];loc=read(LOC/(uid.split('/')[1]+'-locations.json.gz'));tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
  selected=sorted({i for row in loc['rows']if row['candidateGapM']<-.5 for i in row['incidentIndexedFaces']});rows=[]
  for name,ground in [('originalTin',original),('candidate',np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3))]:
   poly=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(poly)>1e-10;gg=ground[valid];poly=poly[valid];tree=shapely.STRtree(poly)
   for i in selected:
    f=tri[i];n=np.cross(f[1]-f[0],f[2]-f[0]);length=np.linalg.norm(n);q=face_ground_context(f,gg,poly,tree)if length else degenerate_ground_context(f,gg,poly,tree);q=apply_exact_coverage(q,f,gg);rows.append(dict(sourceFace=i,terrain=name,triangle=f.tolist(),normalYRatio=float(n[1]/length)if length else None,areaM2=float(length/2),context=q))
  save(DOC/(uid.split('/')[1]+'-faces.json.gz'),dict(uid=uid,sourceSHA256=g['sourceSHA256'],rows=rows));summaries.append(dict(uid=uid,sourceSHA256=g['sourceSHA256'],flaggedFaces=selected,contexts=len(rows)));print(summaries[-1],flush=True)
 save(DOC/'summary.json',dict(rows=summaries,fullAcceptance=False))
 refs.extend(ROOT/p for p in pins);refs.extend([HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_projection_coverage_fallback_context_20261009.py'])
 module('grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-original-grade-whole-faces-v1',list(set(refs)),dict(uids=[g['uid']for g in summaries],fullAcceptance=False))
if __name__=='__main__':main()
