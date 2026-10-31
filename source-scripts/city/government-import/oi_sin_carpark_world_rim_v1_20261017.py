"""Bind the eight actual source boundary edges to all captured renderer modes."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-oi-sin-four-originals-world-capture-v2-20261017';TOP=BASE/'government-xl-oi-sin-carpark-rim-topology-v1-20261017';BATCH='government-xl-oi-sin-carpark-world-rim-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for d in [CAP,TOP]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p in [CAP/'world-triangles.json.gz',TOP/'topology.json']:
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 worlds=read(CAP/'world-triangles.json.gz');edges=[e for e in read(TOP/'topology.json')['rows']if e['role']=='wall-bottom-boundary'];assert len(edges)==8
 source=np.asarray(worlds['original']['landsd/256457:0']);out=[]
 for e in edges:
  fi=e['sourceFaces'][0];indices=[]
  for p in e['segment']:
   ix=np.flatnonzero(np.all(source[fi]==p,axis=1));assert len(ix)==1;indices.append(int(ix[0]))
  for mode,w in worlds.items():
   t=np.asarray(w['landsd/256457:0']);host=np.asarray(w['landsd/91128:0']);seg=t[fi,indices];a,b=seg;delta=b-a;proof=verify(seg,host)
   if not proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']:
    pieces=[verify(np.asarray([a+delta*(j/8),a+delta*((j+1)/8)]),host)for j in range(8)]
    proof=dict(verifiedCompleteOriginalEdgeFiniteFacadeBand=all(x['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in pieces),pieces=pieces,originalProof=proof)
   out.append(dict(edge=e['edge'],mode=mode,sourceFace=fi,vertexIndices=indices,segment=seg.tolist(),proof=proof));print(mode,e['edge'],proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'],flush=True)
 summary=dict(boundaryEdges=8,modes=len(worlds),completeChecks=len(out),passed=sum(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in out),fullAcceptance=False)
 save(DOC/'world-rim.json.gz',dict(summary=summary,rows=out));refs.extend([HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py'])
 r=module('oi_world_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-carpark-boundary-all-renderer-modes-v1',refs,dict(uids=['landsd/256457:0','landsd/91128:0'],summary=summary,nextStep='Retain canonical strict failures; complete exact-source junction/identity qualification and current four-original neighbour checks before installation.'));print(dict(jobId=r['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
