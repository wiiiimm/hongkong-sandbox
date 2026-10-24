"""Measure the eight original school ramp faces; no terrain or building edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-quality-music-school-podium-eight-ramp-context-v1-20261025'
RUNTIME='government-xl-quality-music-school-three-original-private-runtime-v1-20261025'
CONTEXT='government-xl-quality-music-school-three-original-private-continuous-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 c=take(CONTEXT,BASE/CONTEXT/'244789:0.json.gz');g=next(r for r in take(RUNTIME,HERE/'local'/RUNTIME/'runtime-geometry.json.gz')['rows']if r['uid']=='landsd/244789:0')
 assert c['sourceSHA256']==g['sourceSHA256']=='71fe74b86400021233c7e29869de099708f751e04842a9fcd2a3b24746a358e9'
 tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert digest(tri.astype('<f8').tobytes())==c['sourceBinding']['decodedWorldTrianglesSHA256']
 expected=[2463,2464,2467,2468,2469,2470,2471,2472];assert c['otherAffectedFaces']==expected;rows=[]
 for i in expected:
  t=tri[i];n=np.cross(t[1]-t[0],t[2]-t[0]);ratio=float(n[1]/np.linalg.norm(n));assert .96<ratio<.97
  assert float(t[:,1].min())==87.38500213623047
  rows.append(dict(face=i,vertices=t.tolist(),normalYRatio=ratio,projectedAreaM2=float(n[1]/2),yRange=[float(t[:,1].min()),float(t[:,1].max())],rawCompleteGroundMinimum=c['faces'][i]['minimum']))
 result=dict(uids=['landsd/244789:0'],sourceSHA256=c['sourceSHA256'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,physicalAcceptance=False,installationApproved=False,qualification='All eight non-wall negatives are upward sloped original faces at87.385..88.298m,not downward basal closures. They remain real original-TIN ramp/terrain conflicts; no wall exemption or changed-.5m clearance limit. Any proposed terrain correction must remain separate, bounded, reproducible and pass full source/neighbour/old-domain checks. This diagnostic grants no terrain edit or publication credit.')
 save(out/'summary.json',result);module('school_ramp_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-school-eight-upward-ramp-terrain-conflict-context',refs,result)
if __name__=='__main__':main()
