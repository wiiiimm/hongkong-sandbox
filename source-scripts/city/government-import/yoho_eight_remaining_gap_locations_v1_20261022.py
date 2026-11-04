"""Locate two failed candidate coverage residues; approximate geometry, no acceptance."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union, nearest_points
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-yoho-eight-gap-locations-v1-20261022'
RESIDUAL='government-xl-yoho-eight-core-020-residual-preflight-v1-20261022'
PATCH='government-xl-yoho-eight-core-margin-020-v1-20261022'
RUNTIME='government-xl-after-fu-loy-three-current-capture-v1-20261022'
def main():
 out=BASE/BATCH;assert not out.exists()
 refs=[Path(__file__)];pins={}
 for name in [RESIDUAL,PATCH,RUNTIME]:
  _,p=authenticate(BASE/name);pins.update(p);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 residual=take(BASE/RESIDUAL/'summary.json');patch=take(BASE/PATCH/'result.json')
 terrain=take(ROOT/patch['candidate']['path']);runtime=take(HERE/'local'/RUNTIME/'runtime-geometry.json.gz')
 g=next(r for r in runtime['rows']if r['uid']=='landsd/146396:0')
 source=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 n=terrain['nativeMesh'];ground=np.asarray(n['position'],dtype='float32').astype(float).reshape(-1,3)[np.asarray(n['index']).reshape(-1,3)]
 rows=[]
 for face in residual['stillUncovered']:
  tri=source[face][:,[0,2]];lo=tri.min(0);hi=tri.max(0);xz=ground[:,:,[0,2]]
  indices=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1))
  polygons=[Polygon(xz[i])for i in indices if Polygon(xz[i]).area>0]
  gap=Polygon(tri).difference(unary_union(polygons))
  parts=list(gap.geoms)if hasattr(gap,'geoms')else[gap]
  pieces=[]
  for part in parts:
   if part.area<=0:continue
   c=part.representative_point();nearest=sorted((float(Polygon(xz[i]).distance(c)),int(i))for i in indices)[:6]
   pieces.append(dict(areaM2=part.area,bounds=list(part.bounds),geometry=mapping(part),nearestCandidateFacets=nearest))
  rows.append(dict(sourceFace=int(face),sourceTriangle=source[face].tolist(),approximateGapAreaM2=gap.area,pieces=pieces))
 report=dict(uids=['landsd/146396:0'],sourceSHA256=g['sourceSHA256'],candidateSHA256=patch['candidate']['sha256'],rows=rows,installationApproved=False,qualification='Approximate GEOS location diagnostic only. Existing exact rational coverage failures are authoritative. No geometry edits, tolerance credit or physical acceptance.')
 save(out/'summary.json',report)
 module('gap_locations_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'candidate-residual-gap-location',refs,report)
 print([(r['sourceFace'],r['approximateGapAreaM2'],len(r['pieces']))for r in rows],flush=True)
if __name__=='__main__':main()
