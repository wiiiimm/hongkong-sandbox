"""Exact point terrain layers at previously recorded residual witnesses; no acceptance."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-unmapped-witness-layers-v1-20261015'
DOC=BASE/BATCH

def layers(tri, point):
 x,z=map(F,(point[0],point[2]));out=[]
 # Broad phase only; exact barycentrics decide inclusion.
 ids=np.flatnonzero((tri[:,:,0].min(1)<=float(x))&(tri[:,:,0].max(1)>=float(x))&(tri[:,:,2].min(1)<=float(z))&(tri[:,:,2].max(1)>=float(z)))
 for i in ids:
  a,b,c=[[F(float(v))for v in p]for p in tri[i]]
  dx,dz=x-a[0],z-a[2];ux,uz=b[0]-a[0],b[2]-a[2];vx,vz=c[0]-a[0],c[2]-a[2];det=ux*vz-uz*vx
  if not det:continue
  u=(dx*vz-dz*vx)/det;v=(ux*dz-uz*dx)/det
  if u<0 or v<0 or u+v>1:continue
  h=a[1]+u*(b[1]-a[1])+v*(c[1]-a[1]);gap=F(point[1])-h
  out.append({'originalTerrainFace':int(i),'heightExact':str(h),'heightM':float(h),'gapM':float(gap),'belowHalfMetre':gap<F(-1,2)})
 return out

def main():
 assert not DOC.exists();DOC.mkdir()
 f=module('witness_layer_decode',HERE/'xl-final-script-pass.py')
 prior=BASE/'government-xl-unmapped-continuous-native-ground-v1-20261015';receipt=read(prior/'result.json');paths=[Path(__file__),prior/'result.json',HERE/'xl-final-script-pass.py'];rows=[]
 for ref in receipt['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];paths.append(p)
 for s in receipt['rows']:
  p=prior/(s['modelId']+'.json.gz');d=read(p);paths.append(p)
  ground=np.concatenate([f.s.terrain_triangles(ROOT/p)for p in d['terrainPaths']])
  for i in s['upwardBelowHalfMetreFaces']:
   witness=d['faces'][i]['minimum']['position'];hits=layers(ground,witness)
   rows.append({'modelId':s['modelId'],'sourceFace':i,'witness':witness,'terrainLayers':hits,'allIntersectedLayersBelowHalfMetre':bool(hits)and all(x['belowHalfMetre']for x in hits)})
 save(DOC/'layers.json',{'rows':rows,'qualification':'Exact rational arithmetic at recorded floating witness coordinates only; not full-face certification or publication approval.'})
 bindings=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json';paths.append(bindings);uids=sorted({b['viewerUID']for r in read(bindings)['rows']for b in r['bindings']})
 counts={'witnesses':len(rows),'allLayersBuried':sum(r['allIntersectedLayersBelowHalfMetre']for r in rows),'noExactTerrainHit':sum(not r['terrainLayers']for r in rows)}
 save(DOC/'summary.json',counts)
 module('freeze_unmapped_layers',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-recorded-witness-terrain-layers-v1',paths,{'uids':uids,'summary':counts,'nextAction':'Use source-backed entrance/perimeter terrain treatment where every terrain layer crosses the original surface; do not waive burial limits or infer full-face acceptance from point checks.'})
 print(counts,flush=True)
if __name__=='__main__':main()
