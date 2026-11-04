"""Complete original low edges containing Oi Sin's unresolved samples; no waiver."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-orchards-original-podium-support-v1-20261017';OLD=PRIOR
BATCH='government-xl-orchards-original-corner-edges-v1-20261017';DOC=BASE/BATCH
UID='landsd/254629:0';SUPPORT='landsd/233002:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 inputs=read(OLD/'support-inputs.json');tri={x['uid']:decode_original_world_triangles((ROOT/x['candidate']['path']).read_bytes())for x in inputs['sources']};source=tri[UID];bottom=source[:,:,1].min()
 edges={}
 for i,t in enumerate(source):
  for a,b in [(0,1),(1,2),(2,0)]:
   if max(t[a,1],t[b,1])>bottom+.35 or np.array_equal(t[a],t[b]):continue
   key=tuple(sorted(map(tuple,t[[a,b]])));e=edges.setdefault(key,dict(segment=np.asarray(key),faces=[]));e['faces'].append(i)
 failures=read(PRIOR/'support-checks.json.gz')['rows'][0]['unresolved'];out=[];accounted=set()
 horizontal_ids=np.flatnonzero(np.all(tri[SUPPORT][:,:,1]==tri[SUPPORT][:,0,1,None],axis=1));horizontal=tri[SUPPORT][horizontal_ids]
 for e in edges.values():
  a,b=e['segment'];delta=b-a;ids=[]
  for i,f in enumerate(failures):
   p=np.array(f['position']);t=np.clip(np.dot(p-a,delta)/np.dot(delta,delta),0,1)
   if np.linalg.norm(p-(a+t*delta))<=.001:ids.append(i)
  if not ids:continue
  proof=verify(e['segment'],horizontal);out.append(dict(segment=e['segment'].tolist(),sourceFaces=sorted(set(e['faces'])),failurePoints=ids,proof=proof));accounted.update(ids)
  print(dict(edge=len(out),passed=proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']),flush=True)
 summary=dict(failedSamples=len(failures),samplesAccounted=len(accounted),unaccountedSamples=sorted(set(range(len(failures)))-accounted),affectedWholeEdges=len(out),wholeEdgesWithinFixedBand=sum(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in out),fixedBandM=.1,installationApproved=False,qualification='Complete finite-edge distance diagnostic only. No contact, identity, foundation or publication acceptance; failed conservative proofs are not proof of a real gap.')
 save(DOC/'edges.json.gz',dict(summary=summary,rows=out,horizontalHostOriginalFaceIDs=horizontal_ids.tolist()))
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'support-checks.json.gz',OLD/'support-inputs.json',HERE/'xl-second-pass.py',HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py']+[ROOT/x['candidate']['path']for x in inputs['sources']]
 result=module('oi_sin_edges_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-complete-original-corner-edges-to-horizontal-podium-v1',refs,dict(uids=[UID,SUPPORT],summary=summary,nextStep='Use whole-edge results to focus source-interface interpretation; retain canonical contact/foundation/identity gates and all raw failures.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
