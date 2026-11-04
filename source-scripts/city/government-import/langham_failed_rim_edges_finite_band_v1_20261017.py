"""Whole original low-edge finite band diagnosis, preserving all contact failures."""
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-failed-rim-edges-finite-band-v1-20261017';DOC=BASE/BATCH
CAP=BASE/'government-xl-langham-current-pair-v1-20261017';CHECK=BASE/'government-xl-langham-current-support-v1-20261017';RT=HERE/'local'/CAP.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();r=read(CHECK/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 geo={g['uid']:g for g in read(RT)['rows']};tri={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for u,g in geo.items()};source=tri['landsd/79318:0'];support=tri['landsd/224399:0'];bottom=source[:,:,1].min();failures=read(CHECK/'support-checks.json.gz')['rows'][0]['unresolved'];edges={}
 for point,f in enumerate(failures):
  for face in f['originalSourceFaces']:
   i=face['faceIndex'];t=source[i]
   for a,b in [(0,1),(1,2),(2,0)]:
    if max(t[a,1],t[b,1])>bottom+.35:continue
    segment=t[[a,b]];key=tuple(sorted(map(tuple,segment)));e=edges.setdefault(key,dict(segment=segment,incidentSourceFaces=[],failurePoints=[]));e['incidentSourceFaces'].append(i);e['failurePoints'].append(point)
 assert edges;out=[]
 for e in edges.values():
  proof=verify(e['segment'],support);out.append(dict(segment=e['segment'].tolist(),incidentSourceFaces=sorted(set(e['incidentSourceFaces'])),failurePoints=sorted(set(e['failurePoints'])),proof=proof));print(dict(faces=out[-1]['incidentSourceFaces'],passed=proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']),flush=True)
 summary=dict(edges=len(out),completeEdgesWithinExistingBand=sum(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in out),fixedBandM=.1,installationApproved=False,qualification='Whole finite-edge distance only, not support contact, structural role, collision, renderer or acceptance proof. Raw four interface failures remain unchanged.')
 save(DOC/'edges.json.gz',dict(rows=out,summary=summary));refs=[Path(__file__),RT,CHECK/'result.json',CHECK/'support-checks.json.gz',HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py']
 result=module('langham_edge_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-original-langham-failed-low-edge-fixed-band-diagnostic-v1',refs,dict(uids=['landsd/79318:0'],summary=summary,fullAcceptance=False,nextStep='Review complete edge evidence and source attachment without replacing contact rules with a nearest-point waiver.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
