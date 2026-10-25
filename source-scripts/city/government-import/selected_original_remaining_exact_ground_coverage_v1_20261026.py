"""Resolve remaining numerical coverage flags by closed rational facet coverage.

Raw continuous warnings remain unchanged. A real uncovered remainder stays false.
"""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import exact_coverage

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','continuous','uid']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
 def take(n,path):
  if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 ctx=take(a.continuous,base/a.continuous/(a.uid.split('/')[1]+'.json.gz'))
 g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
 selection=take(a.runtime,base/a.runtime/'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==a.uid)
 asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==g['sourceSHA256']==ctx['sourceSHA256'];refs.append(asset)
 tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];raw_ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 # Match the original continuous-context ground basis exactly; no new pruning.
 valid=shapely.area(shapely.polygons(raw_ground[:,:,[0,2]]))>1e-10;ground=raw_ground[valid]
 assert digest(tri.astype('<f8').tobytes())==ctx['sourceBinding']['decodedWorldTrianglesSHA256']
 assert digest(ground.astype('<f8').tobytes())==ctx['sourceBinding']['drawnGroundSHA256']
 assert len(ctx['faces'])==len(tri)==ctx['wholeSourceFaces']==source['triangles']
 assert [r['sourceFace']for r in ctx['faces']]==list(range(len(tri)))
 raw=[r for r in ctx['faces']if not r['groundProjectionCovered']];assert len(raw)==ctx['wholeSourceUncoveredFaces']
 rows=[]
 for r in raw:
  i=r['sourceFace'];proof=exact_coverage(tri[i],ground);rows.append(dict(sourceFace=i,rawContinuousCoverage=False,rawUncoveredProjectionAreaM2=r.get('uncoveredProjectionAreaM2'),rawUncoveredProjectionLengthM=r.get('uncoveredProjectionLengthM'),proof=proof))
  print(dict(sourceFace=i,exactProjectionCovered=proof['exactProjectionCovered']),flush=True)
 result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],sourceBinding=ctx['sourceBinding'],wholeOriginalFacesAccounted=len(tri),completeCapturedGroundFaces=len(raw_ground),continuousContextGroundFaces=len(ground),rawUncoveredFaces=len(raw),exactRemainingCoverage=rows,remainingExactlyUncoveredFaces=[r['sourceFace']for r in rows if not r['proof']['exactProjectionCovered']],completeProjectionCoverageProved=all(r['proof']['exactProjectionCovered']for r in rows),continuousClearanceAcceptance=False,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Existing continuous positive coverage retained; every remaining false numerical flag tested by exact closed rational area/line/point coverage against the identical complete continuous-context ground basis. No buffer, tolerance credit, source edit, clearance override or publication approval. Raw false flags stay in their original receipts.')
 save(out/'summary.json',result);refs.extend([HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_original_projection_coverage_20261010.py']);module('remaining_exact_ground_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-remaining-original-ground-projection-coverage',refs,result)
 print(dict(rawUncoveredFaces=len(raw),remainingExactlyUncoveredFaces=result['remainingExactlyUncoveredFaces']),flush=True)
if __name__=='__main__':main()
