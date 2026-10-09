"""Complete exact nearest original rooted facet witnesses for four entrances.

No distance threshold grants support. Every rooted original facet is tested
or rigorously excluded by a >=1m whole-part bounding-box distance witness.
Nearest result is certified only when an actual tested distance is <1m.
"""
import json,math
from fractions import Fraction as F
import numpy as np
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_distance_20261009 import triangle_distance
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261009-118230-original-entrance-mount-distances-v1';DOC=BASE/BATCH
def main():
 assert not DOC.exists();g=read(BASE/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1/diagnostic.json.gz');role=read(BASE/'xl-terrain-recovery-20261009-118230-current-roof-perimeter-role-v1/typed-role.json.gz');row=read(BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009/selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw);rootids=sorted(i for k in role['resolvedOriginalComponents'] for i in g['components'][k]['globalOriginalFaces']);byface={i:k for k,c in enumerate(g['components']) for i in c['globalOriginalFaces']};lo=tri.min(axis=1);hi=tri.max(axis=1);results=[]
 for k in [417,418,419,420]:
  ids=g['components'][k]['globalOriginalFaces'];plo=tri[ids].min(axis=(0,1));phi=tri[ids].max(axis=(0,1));near=[];excluded=[]
  for j in rootids:
   gaps=[max(F(float(plo[a]))-F(float(hi[j,a])),F(float(lo[j,a]))-F(float(phi[a])),F(0)) for a in range(3)];lb=sum(v*v for v in gaps)
   if lb>=1:excluded.append(dict(originalSourceFace=j,exactWholePartBBoxDistanceLowerSquaredM2=str(lb)))
   else:near.append(j)
  assert len(near)+len(excluded)==len(rootids);rows=[]
  for i in ids:
   nearest=None;tested=0
   for j in near:
    gaps=[max(F(float(lo[i,a]))-F(float(hi[j,a])),F(float(lo[j,a]))-F(float(hi[i,a])),F(0)) for a in range(3)];lb=sum(v*v for v in gaps)
    if nearest is not None and lb>F(nearest['exactSquaredDistanceM2']):continue
    r=triangle_distance(tri[i],tri[j]);tested+=1
    if nearest is None or F(r['exactSquaredDistanceM2'])<F(nearest['exactSquaredDistanceM2']):nearest=dict(r,rootedSourceFace=j,rootedOriginalComponent=byface[j])
   assert nearest is not None and F(nearest['exactSquaredDistanceM2'])<1,'Chosen whole-scope exclusion bound insufficient'
   rows.append(dict(sourceFace=i,completeOriginalVertices=tri[i].tolist(),nearestCompleteOriginalRootedSurface=nearest,exactFacetPairsEvaluated=tested,globallyCertifiedAgainstAllRootedSourceFaces=True,noMountOrSupportCredit=True))
   print(json.dumps(dict(component=k,face=i,nearestRootedFace=nearest['rootedSourceFace'],distanceM=math.sqrt(float(F(nearest['exactSquaredDistanceM2']))),pairs=tested)),flush=True)
  results.append(dict(component=k,completeOriginalFaces=ids,everyOriginalFaceNearestWitness=rows,completeRootedOriginalScopeFaces=rootids,rigorouslyExcludedOriginalFaces=excluded,remainingOriginalRootedFaces=near,exactContactFound=any(r['nearestCompleteOriginalRootedSurface']['exactOriginalContact'] for r in rows),structuralRootCredit=False))
 save(DOC/'diagnostic.json.gz',dict(sourceSHA256=digest(raw),completeOriginalWorldSHA256=digest(tri.tobytes()),everyOriginalEntrancePart=results,originalSourceGeometryChanges=0,fullAcceptance=False,installationApproved=False))
if __name__=='__main__':main()
