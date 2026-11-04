"""Measure unchanged podium roof coverage over the recorded shelter footprint."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v1_20261015 import module,BASE
BATCH='government-xl-primrose-shelter-roof-coverage-v1-20261015';DOC=BASE/BATCH
OLD=BASE/'government-xl-primrose-shelter-source-context-v1-20261015'
def main():
 assert not DOC.exists();receipt=read(OLD/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 x=read(OLD/'context.json');b=x['currentForm'];poly=Polygon(b['rings'][0],b['rings'][1:]);t=np.asarray(x['intersectingOriginalTriplets']);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);groups={}
 for i,face,n in zip(x['intersectingOriginalFaces'],t,cross):
  clipped=Polygon(face[:,[0,2]]).intersection(poly)
  if clipped.area<=1e-10:continue
  assert np.ptp(face[:,1])==0,'non-horizontal surface requires plane calculation'
  y=float(face[0,1]);g=groups.setdefault(y,dict(faces=[],pieces=[]));g['faces'].append(i);g['pieces'].append(clipped)
 rows=[]
 for y,g in sorted(groups.items()):
  union=shapely.union_all(g['pieces']);rows.append(dict(sourceY=y,sourceFaces=g['faces'],unionAreaM2=float(union.area),footprintCoverage=float(union.area/poly.area),deltaFromRecordedTopM=y-b['topHeightHKPD']))
 save(DOC/'coverage.json',dict(uid=b['uid'],footprintAreaM2=poly.area,recordedTop=b['topHeightHKPD'],rows=rows,duplicateSuppressionApproved=False,fullAcceptance=False))
 paths=[ROOT/q['path']for q in receipt['evidenceRefs']]+[OLD/'result.json',Path(__file__),HERE/'primrose_compound_foundation_v1_20261015.py']
 module('shelter_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-source-horizontal-roof-footprint-coverage-v1',paths,dict(uids=[b['uid'],'landsd/74573:0'],rows=rows,fullAcceptance=False,qualification='Geometric coverage evidence only; no automatic identity or duplicate suppression approval.'))
 print(rows,flush=True)
if __name__=='__main__':main()
