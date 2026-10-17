"""Offline bounded benchmark only. No DB/reservation/acceptance."""
import time,json
import numpy as np
from run import ROOT,HERE,read,save,digest
from west_wing26195_complete_finite_face_draft_v1_20261012 import CompleteGround,face_proof
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
B=ROOT/'docs/astra-city/government-import';CAP=B/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012';OUT=B/'government-xl-west-wing26195-complete-finite-ground-proposal-v1-20261012'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 scope=read(CAP/'capture-scope.json');o=read(CAP/'original-full-source-root-context.json.gz');t=np.asarray(o['completeOriginalBinary64WorldTriangles'],dtype='<f8');rtp=HERE/'local'/CAP.name/'runtime-geometry.json.gz';g=np.asarray(read(rtp)['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 assert t.shape==(46918,3,3)and digest(t.tobytes())==scope['completeOriginalWorldSHA256'];assert len(g)==3240 and digest(g.tobytes())==scope['completeActualGroundSHA256'];complete=CompleteGround(g)
 # Deterministic low source faces plus whole-input spaced faces; not representative whole-surface proof.
 ids=sorted(set(list(np.argsort(t[:,:,1].min(1),kind='stable')[:4])+[0,11729,23459,35188]));rows=[]
 for i in ids:
  i=int(i);start=time.monotonic();q=finite(t[i],g);coarse=time.monotonic()-start;start=time.monotonic();p=face_proof(t[i],complete,i,None);elapsed=time.monotonic()-start
  assert p['completeProjectionCovered']==q['groundProjectionCovered'];assert p['selection']['selectedOriginalGroundFaces']==q['allProjectedBoundingCandidateOriginalGroundFacets'];assert p['selectedGroundKernelProof']['exactCertifiedLowerClearanceM']==q['exactCertifiedLowerClearanceM'];rows.append(dict(face=i,fullGroundCoarseSeconds=coarse,prunedCoarseAndPairedSeconds=elapsed,selectedGroundFacets=p['selection']['selectedFacetCount'],ordinaryFiniteProved=p['ordinaryFiniteProved'],proof=p));print(json.dumps({k:v for k,v in rows[-1].items()if k!='proof'}),flush=True)
 complete.verify_binding();save(OUT/'bounded-offline-benchmark.json',dict(benchmarkOnly=True,completeFaceProof=False,DBQueries=0,leases=0,completeSourceSHA256=digest(t.tobytes()),completeGroundSHA256=digest(g.tobytes()),sampledFaceIDs=list(map(int,ids)),rows=rows,evidenceRefs=[ref(CAP/'capture-scope.json'),ref(CAP/'original-full-source-root-context.json.gz'),ref(rtp),ref(HERE/'west_wing26195_complete_finite_face_draft_v1_20261012.py'),ref(__import__('pathlib').Path(__file__))],extrapolationIsNotRuntimeGuarantee=True))
if __name__=='__main__':main()
