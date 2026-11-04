"""Classify original rim topology without inventing internal-diagonal support gates."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-oi-sin-carpark-all-surface-rim-v1-20261017';PHYS=BASE/'government-xl-oi-sin-four-originals-physical-v2-20261017'
BATCH='government-xl-oi-sin-carpark-rim-topology-v1-20261017';DOC=BASE/BATCH;RT=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for folder in [PRIOR,PHYS]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p in [RT,PRIOR/'rim.json.gz',PHYS/'support-checks.json.gz']:
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 g=next(x for x in read(RT)['rows']if x['uid']=='landsd/256457:0');t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];bottom=t[:,:,1].min();out=[];boundary_samples=set()
 for i,e in enumerate(read(PRIOR/'rim.json.gz')['rows']):
  fs=e['sourceFaces'];tris=t[fs];normals=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);flat=np.all(tris[:,:,1]==bottom,axis=1)
  # Both exact source facets share the complete edge. Coplanar bottom triangles
  # are not a wall-to-bottom rim, regardless of an unresolved endpoint.
  internal=len(fs)==2 and bool(flat.all());boundary=len(fs)==2 and int(flat.sum())==1 and bool(np.any(normals[~flat, [0,2]]!=0))
  assert internal or boundary,(i,fs)
  row=dict(edge=i+1,segment=e['segment'],sourceFaces=fs,originalNormals=normals.tolist(),role='internal-bottom-triangulation'if internal else 'wall-bottom-boundary',failurePoints=e['failurePoints'],wholeEdgeBandPassed=e['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']);out.append(row)
  if boundary:boundary_samples.update(e['failurePoints'])
 unresolved=next(x['interface']['unresolved']for x in read(PHYS/'support-checks.json.gz')['rows']if x['uid']==g['uid']);boundary=[x for x in out if x['role']=='wall-bottom-boundary'];failed=[x for x in out if not x['wholeEdgeBandPassed']]
 summary=dict(selectedEdges=len(out),wallBottomBoundaryEdges=len(boundary),allSelectedBoundaryEdgesWithinBand=all(x['wholeEdgeBandPassed']for x in boundary),unresolvedContactSamples=len(unresolved),samplesOnSelectedBoundary=len(boundary_samples),samplesNotOnBoundary=sorted(set(range(len(unresolved)))-boundary_samples),failedInternalDiagonals=len(failed),allFailedEdgesInternal=all(x['role']=='internal-bottom-triangulation'for x in failed),rawStrictContactsPassed=False,fullAcceptance=False,geometryChanges=0)
 save(DOC/'topology.json',dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],summary=summary,rows=out))
 result=module('oi_rim_topology_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-original-carpark-boundary-topology-v1',refs,dict(uids=[g['uid']],summary=summary,nextStep='Do not require proximity of internal bottom-face diagonals. Retain all original strict failures; qualify actual boundary source roles and the two buried vertical junction faces, then complete publication gates.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
