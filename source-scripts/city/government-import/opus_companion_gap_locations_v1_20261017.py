"""Locate exact uncovered pieces before/after terrain Float32 conversion; no repair."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import point,signed_area,subtract,exact_coverage
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-opus-companion-complete-patch-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';BATCH='government-xl-opus-companion-gap-locations-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PREV/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']};refs=[Path(__file__),PREV/'result.json',HERE/'exact_original_projection_coverage_v2_20261010.py']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 cap=consume(PREV/'drawn-patch.json.gz');patch=consume(ROOT/cap['patchPath']);tri=np.array(consume(WORLD/'world-triangles.json.gz')['original']['landsd/319559:0']);old=consume(PREV/'proofs.json.gz');render=np.array(cap['position']).reshape(-1,3)[np.array(cap['index']).reshape(-1,3)];raw=np.array(patch['nativeMesh']['position']).reshape(-1,3)[np.array(patch['nativeMesh']['index']).reshape(-1,3)];rows=[]
 for row in old['rows']:
  if row['proof']['groundProjectionCovered']:continue
  i=row['sourceFace'];f=tri[i];xz=f[:,[0,2]];gxz=render[:,:,[0,2]];ids=np.flatnonzero(np.all(gxz.max(1)>=xz.min(0),axis=1)&np.all(gxz.min(1)<=xz.max(0),axis=1));remaining=[[point(p) for p in xz]]
  for j in ids:
   t=[point(p) for p in gxz[j]]
   if signed_area(t):remaining=[p for piece in remaining for p in subtract(piece,t)]
  area=sum(abs(signed_area(p)) for p in remaining);assert area==Fraction(row['proof']['completeOriginalProjectionCoverage']['exactUncoveredAreaM2'])
  before=exact_coverage(f,raw);pieces=[dict(exactVertices=[[str(v) for v in p] for p in poly],vertices=[[float(v) for v in p] for p in poly],exactAreaM2=str(abs(signed_area(poly)))) for poly in remaining];rows.append(dict(sourceFace=i,renderedUncoveredAreaM2=float(area),preFloatCoverage=before,pieces=pieces));print(i,float(area),before['exactProjectionCovered'],flush=True)
 DOC.mkdir();save(DOC/'gaps.json.gz',dict(rows=rows,sourceGeometryChanges=0,terrainChanges=0));summary=dict(failedFaces=len(rows),coveredBeforeFloat32=sum(r['preFloatCoverage']['exactProjectionCovered'] for r in rows),faceProjectedGapAreaSumM2=sum(r['renderedUncoveredAreaM2'] for r in rows),qualification='Sum counts overlapping source projections separately, not unique terrain gap area.',fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 result=module('opus_gap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-exact-companion-terrain-gap-locations-v1',refs,dict(uids=['landsd/319559:0'],**summary));print(dict(jobId=result['jobId'],**summary),flush=True)
if __name__=='__main__':main()
