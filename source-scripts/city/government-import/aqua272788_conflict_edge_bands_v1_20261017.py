"""Exact unchanged 0.1 m whole-edge proximity diagnostic for recorded source conflicts."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-aqua272788-conflict-source-context-v1-20261017';BATCH='government-xl-aqua272788-conflict-edge-bands-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 runtime=HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz';assert str(runtime.relative_to(ROOT))in {e['path']for e in r['evidenceRefs']}
 tri={g['uid']:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in read(runtime)['rows']};rows=[]
 for face in [32,1836]:
  for edge in range(3):
   segment=tri['landsd/272788:0'][face,[edge,(edge+1)%3]];proof=verify(segment,tri['landsd/193086:0']);rows.append(dict(face=face,edge=edge,segment=segment.tolist(),proof=proof));print(face,edge,proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'],flush=True)
 save(DOC/'edges.json.gz',dict(rows=rows,fixedBandM=.1,geometryChanges=0,installationApproved=False));passed=sum(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in rows)
 refs=[Path(__file__),PRIOR/'result.json',*[ROOT/e['path']for e in r['evidenceRefs']],HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py']
 out=module('aqua_edge_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-complete-original-conflict-edge-proximity-v1',refs,dict(uids=['landsd/272788:0'],wholeEdges=6,certifiedWithinExistingBand=passed,fullAcceptance=False,nextStep='Retain raw foundation failure. Use exact edge results to distinguish nearby original joint from separated facets; no support or publication waiver.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
