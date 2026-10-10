"""Complete original trim lower edges and named glyph back opening; diagnostic only."""
import collections,importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify
BATCH='xl-terrain-recovery-20261010-festival-lower-trim-and-back-glyph-mount-diagnostic-v1';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261010-festival-pair-authentic-multi-current-original-support-v3';PHYS=BASE/'government-xl-terrain-recovery-festival-pair-finite-sampler-current-v4-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');rs=read(PHYS/'selection.json.gz')['rows'];assets=[ROOT/r['candidate']['path'] for r in rs];tri=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(tri.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];rootids=np.array(sorted(i for k in g['resolvedOriginalComponents'] for i in g['components'][k]['globalOriginalFaces']));n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nn=np.linalg.norm(n,axis=1);roof=rootids[n[rootids,1]>.25*nn[rootids]];results=[]
 for k in [258,259,263,219]:
  ids=g['components'][k]['globalOriginalFaces'];part=tri[ids];edges=collections.defaultdict(list)
  for i in ids:
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
    if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
  boundary=[e for e,v in sorted(edges.items()) if len(v)==1]
  if k==219:
   # Authored outer back-opening source faces, selected from complete source inspection.
   edge_faces={28820,28823,28824,28826,28828,28830,28832,28835,28837,28838,28840,28842,28844,28847,28848,28849,28852,28854,28855,28858,28859,28861,28863,28865,28867,28870,28871,28874,28875,28878,28881,28882,28885,28886,28888,28889,28892,28894,28896,28898,28899,28902,28904,28905,28907}
   chosen=[e for e in boundary if len(edges[e])==1 and edges[e][0] in edge_faces];assert len(chosen)==45;hosts=rootids[np.abs(n[rootids,1])<=.05*nn[rootids]];kind='named-original-glyph-complete-outer-back-opening'
  else:
   low=part[:,:,1].min();chosen=[e for e in sorted(edges) if e[0][1]==e[1][1]==low];assert chosen;hosts=roof;kind='complete-original-roof-trim-lowest-edges'
  proofs=[]
  for e in chosen:
   lo=np.minimum(*map(np.array,e))-.1;hi=np.maximum(*map(np.array,e))+.1;near=hosts[np.all(tri[hosts].max(axis=1)>=lo,axis=1)&np.all(tri[hosts].min(axis=1)<=hi,axis=1)];assert len(near)
   q=verify(np.array(e),tri[near]);proofs.append(dict(edge=e,originalFaces=edges[e],completeCandidateOriginalHostFaces=near.tolist(),band=q));print(k,len(proofs),q['verifiedCompleteOriginalEdgeFiniteFacadeBand'],flush=True)
  a=collections.defaultdict(set)
  for x,y in chosen:a[x].add(y);a[y].add(x)
  results.append(dict(component=k,kind=kind,completeOriginalFaces=ids,completeOriginalBounds=g['components'][k]['bounds'],completeOriginalMountEdges=proofs,completeOriginalGeometricBoundary=[dict(edge=e,faces=edges[e]) for e in boundary],mountBoundaryClosedCycle=bool(a) and all(len(v)==2 for v in a.values()),allMountEdgesWithinExistingFiniteBand=all(q['band']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for q in proofs),rawOtherBoundaryRetained=True,visualRoleAccepted=False,groundRootCredit=False,structuralBridgeCredit=False))
 refs=[ref(p) for p in [Path(__file__),GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PHYS/'selection.json.gz',*assets,HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_20261010.py',HERE/'test_exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']];save(DOC/'diagnostic.json.gz',dict(uids=[r['uid'] for r in rs],rows=results,completeOriginalWorldSHA256=digest(tri.tobytes()),independentlyRootedComponents=g['resolvedOriginalComponents'],evidenceRefs=refs,sourceGeometryChanges=0,installationApproved=False));sp=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.freeze(BATCH,'festival-complete-original-lower-trim-and-back-opening-fixed-band-diagnostic-v1',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in rs],results=[dict(component=q['component'],band=q['allMountEdgesWithinExistingFiniteBand'],closedCycle=q['mountBoundaryClosedCycle']) for q in results],sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False))
if __name__=='__main__':main()
