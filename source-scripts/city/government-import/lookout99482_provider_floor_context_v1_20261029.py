"""Compare residual source undersides with exact provider TIN and current ground."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from exact_original_triangle_pair_column_gap_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lookout99482-after-sha-tin-provider-floor-context-v1-20261029'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 runtime='government-xl-lookout99482-after-sha-tin-targeted-runtime-v1-20261029';old='government-xl-runtime-fit-99482-original-terrain-recovery-v4-20261022';g=take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows'][0];summary=take(old,BASE/old/'summary.json');checked=summary['rows'][0];assert g['sourceSHA256']==checked['sourceSHA256']
 tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];current=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);decoder=module('lookout_floor_source_tin',HERE/'xl-second-pass.py');parts=[]
 for name in checked['sourceTerrainPaths']:
  p=ROOT/name;meta=take(old,p)
  for b in meta.get('buffers',[]):
   f=p.parent/b['uri'];assert digest(f.read_bytes())==pins[old][str(f.relative_to(ROOT))];refs.append(f)
  parts.append(decoder.terrain_triangles(p))
 provider=np.concatenate(parts);rows=[]
 for i in [312,313,24653]:
  face=tri[i];by={}
  for label,ground in [('provider',provider),('current',current)]:
   lo,hi=face[:,[0,2]].min(0),face[:,[0,2]].max(0);xz=ground[:,:,[0,2]];ids=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1));candidate=ground[ids]
   coverage=exact_coverage(face,candidate);pairs=[]
   for j,t in zip(ids,candidate):
    p=verify(face,t)
    if p['exactClosedHorizontalProjectionsMeet']:pairs.append(dict(groundFace=int(j),proof=p))
   assert pairs
   by[label]=dict(coverage=coverage,exactMinimumFiniteColumnGapM=str(min(Fraction(p['proof']['exactMinimumFiniteColumnGapM'])for p in pairs)),pairs=pairs)
  rows.append(dict(sourceFace=i,vertices=face.tolist(),providerAndCurrent=by))
 result=dict(uids=['landsd/99482:0'],sourceSHA256=g['sourceSHA256'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Complete exact finite-column and projection evidence for the three residual downward facets against the cached original provider TIN and actual current drawn ground. Identifies source-authored undersides versus coarse-terrain mismatch without lowering terrain merely to erase a diagnostic. No source geometry or threshold change.')
 save(out/'summary.json',result);refs.extend([HERE/'xl-second-pass.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py'])
 module('lookout_provider_floor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-residual-downward-provider-and-current-ground-context',list(dict.fromkeys(refs)),result)
 print([(r['sourceFace'],{k:v['exactMinimumFiniteColumnGapM']for k,v in r['providerAndCurrent'].items()})for r in rows],flush=True)
if __name__=='__main__':main()
